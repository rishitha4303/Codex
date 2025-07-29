from llama_index.core import ServiceContext, VectorStoreIndex, StorageContext,load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
import chromadb
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
from pymongo import MongoClient
from llama_index.core.vector_stores.simple import SimpleVectorStore
from datetime import datetime
import hashlib, json
from llama_index.core.storage.docstore.simple_docstore import SimpleDocumentStore
from llama_index.core.storage.index_store.simple_index_store import SimpleIndexStore
import requests
from llama_index.core.schema import Document
from dotenv import load_dotenv
load_dotenv()
# Deserialize back to Document objects



from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.llms import Ollama
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.core.query_engine import RetrieverQueryEngine
from dotenv import load_dotenv
import os

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
def is_summary_or_workflow_question(q):
    q = q.lower()
    keywords = ["summary", "overview", "workflow", "how it works", "explain repo"]
    return any(k in q for k in keywords)


import re

def format_response_for_browser(response_text):
    lines = response_text.strip().split('\n')
    formatted = []

    for line in lines:
        stripped = line.strip()

        # Numbered sections
        if re.match(r'^\d+\.\s+.+', stripped):
            formatted.append(f'<p style="margin-top: 1em;"><strong>🔹 {stripped}</strong></p>')
        # Headers
        elif stripped.startswith("##") or stripped.endswith(":"):
            clean = stripped.strip("# ").rstrip(":")
            formatted.append(f'<h3 style="color:#1e88e5;">{clean}</h3>')
        # Bullets
        elif stripped.startswith("*") or stripped.startswith("-"):
            formatted.append(f'<li>{stripped[1:].strip()}</li>')
        # Normal paragraph
        else:
            formatted.append(f'<p>{stripped}</p>')

    # Wrap <li> in <ul> if any
    html_output = []
    in_list = False
    for line in formatted:
        if line.startswith("<li>") and not in_list:
            html_output.append("<ul>")
            in_list = True
        elif not line.startswith("<li>") and in_list:
            html_output.append("</ul>")
            in_list = False
        html_output.append(line)
    if in_list:
        html_output.append("</ul>")

    return "\n".join(html_output)

def embed_and_search(docs, question, repo_url,branch):
    # ✅ Unique repo identifier (hash) and Chroma DB path
    unique_repo_key = f"{repo_url}@{branch}"
    repo_id = hashlib.sha256(unique_repo_key.encode()).hexdigest()

    chroma_path = f"./chroma_db/{repo_id}"
    collection_name = f"repo_{repo_id}"

    # ✅ Init Chroma client
    db = chromadb.PersistentClient(path=chroma_path)
    chroma_collection = db.get_or_create_collection(name=collection_name)

    # ✅ Set up vector store with Chroma
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # ✅ Set global config (only once)
    Settings.embed_model = HuggingFaceEmbedding(model_name="all-MiniLM-L6-v2")
    Settings.llm = Ollama(model="gemma:2b", request_timeout=300, temperature=0.3, streaming=False)

    Settings.text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

    # ✅ Check if index is already in Chroma (very basic heuristic)
    if len(chroma_collection.get()["ids"]) == 0:
        print("🚀 Creating and storing new index...")
        
        index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
    else:
        print("✅ Loading index from Chroma...")
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    # ✅ Query setup
    # Pseudocode
    if is_summary_or_workflow_question(question):
        retriever = index.as_retriever(similarity_top_k=20)
    else:
        retriever = index.as_retriever(similarity_top_k=4)
    retrieved_nodes = retriever.retrieve(question)

# DEBUG: Print or log the retrieved document texts
    context_parts = []
    print("\n📄 Retrieved Documents:")
    for i, node in enumerate(retrieved_nodes, 1):
        file_path = node.metadata.get("file_path", "Unknown file path")
        print(f"\n--- Document {i} ---")
        print(f"📄 File: {file_path}")
        print(node.text[:1000])  # Preview
        context_parts.append(f"File: {file_path}\n{node.text}")

    context = "\n\n".join(context_parts)

    # 2. Prepare the prompt
    prompt = f"""Use the context below to answer the question clearly. If asked for a code file, give back the exact code with explanation.

    Context:
    {context}

    Question:
    {question}
    """

    # 3. POST to Gemini API
    
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    # 4. Send request
    response = requests.post(GEMINI_URL, headers=headers, json=payload)
    result = response.json()
    gemini_output = result['candidates'][0]['content']['parts'][0]['text']
    print("\n🔍 Gemini Response:")
    print(gemini_output)
    return str(gemini_output)


    query_engine = RetrieverQueryEngine.from_args(retriever)

    # ✅ Smart prompt
    concise_question = f"""{question.strip()} Explain neatly in a length that is suitable for the question, so that a beginner can understand. Dont make it too big. Use the given context to answer this. If asked for dependencies or libraries refer the imports in all the files provided'."""

    response = query_engine.query(concise_question)
    return str(response)

def synthesize_project_summary(docs):
    """
    Generate a basic summary and feature list from filenames, folder names, and code comments
    as a fallback if embeddings-based search returns poor/no results.
    """
    from collections import Counter

    file_names = [doc.metadata.get('file_path', '') for doc in docs]
    main_files = [fn for fn in file_names if os.path.basename(fn).lower() in ['app.js', 'main.py', 'index.js', 'server.js', 'index.py']]
    config_files = [fn for fn in file_names if os.path.basename(fn).lower() in ['package.json', 'requirements.txt', 'pyproject.toml']]
    test_files = [fn for fn in file_names if 'test' in os.path.basename(fn).lower()]
    src_files = [fn for fn in file_names if fn.startswith('src/') or fn.startswith('src\\')]
    doc_files = [fn for fn in file_names if os.path.splitext(fn)[1] in ['.md', '.rst', '.txt']]

    # Heuristic: count file types
    ext_counter = Counter(os.path.splitext(f)[1] for f in file_names)

    summary_lines = []
    summary_lines.append("This project contains the following key files and folders:")
    if main_files:
        summary_lines.append(f"- Main application files: {', '.join(main_files)}")
    if config_files:
        summary_lines.append(f"- Configuration files: {', '.join(config_files)}")
    if src_files:
        summary_lines.append(f"- Source code is organized in a `src/` directory.")
    if test_files:
        summary_lines.append(f"- Includes test files: {', '.join(test_files[:3])}" + (f" and {len(test_files)-3} more" if len(test_files) > 3 else ""))

    # Features from code comments (very basic!)
    feature_lines = []
    for doc in docs:
        # Try to extract lines starting with "#", "//", or "/*" for Python/JS
        for line in doc.text.split('\n'):
            l = line.strip()
            if l.startswith("#") or l.startswith("//") or l.startswith("/*"):
                comment = l.lstrip("#/ ").strip()
                if len(comment) > 12 and "copyright" not in comment.lower():
                    feature_lines.append(f"- {comment}")
            if len(feature_lines) > 5:
                break
        if len(feature_lines) > 5:
            break

    fallback_description = "\n".join(summary_lines) if summary_lines else "No clear project summary found."
    fallback_features = "\n".join(feature_lines) if feature_lines else "- No explicit features found in code comments."

    return fallback_description, fallback_features

def get_file_tree(docs, max_files=10):
    """Return a markdown list of up to max_files files in the repo."""
    files = [doc.metadata.get('file_path', '') for doc in docs]
    files = sorted(files)
    if len(files) > max_files:
        return "\n".join(f"- `{f}`" for f in files[:max_files]) + f"\n- ...and {len(files)-max_files} more"
    return "\n".join(f"- `{f}`" for f in files)

def generate_readme_sections(docs):
    """
    Generate all main README sections using embed_and_search and fallback logic.
    Returns a dict of {section_name: content}.
    """
    # Section prompts
    prompts = {
        "description": "What is this project about? What does it do? Provide a brief overview of its main purpose and functionality in 2-3 sentences.",
        "features": "What are the main features and capabilities of this project? List 3-5 key functionalities as bullet points.",
        "installation": "How does a user install and set up this project? List all dependencies and setup steps.",
        "usage": "How does a user run or use this project? Show usage example(s).",
        "contributing": "How can someone contribute to this project? List basic steps.",
        "license": "Which license does this project use? If you find a LICENSE file, specify the type.",
    }

    sections = {}

    # 1. Description and Features (with fallback)
    desc = embed_and_search(docs, prompts["description"])
    feat = embed_and_search(docs, prompts["features"])
    if not desc or "context does not provide" in desc.lower():
        desc, _ = synthesize_project_summary(docs)
    if not feat or "context does not provide" in feat.lower():
        _, feat = synthesize_project_summary(docs)

    sections["description"] = desc
    sections["features"] = feat

    # 2. File tree/project structure
    sections["structure"] = get_file_tree(docs)

    # 3. Other sections (installation, usage, contributing, license)
    for section in ["installation", "usage", "contributing", "license"]:
        ans = embed_and_search(docs, prompts[section])
        if not ans or "context does not provide" in ans.lower():
            # Fallbacks for install, usage, contributing, license:
            if section == "installation":
                ans = "See the project files above for configuration files like `requirements.txt` or `package.json`. Typical steps: clone repo, install dependencies, and run main file."
            elif section == "usage":
                ans = "Typical usage: install dependencies, then run the main application file. See source files for details."
            elif section == "contributing":
                ans = "1. Fork the repository\n2. Create a feature branch\n3. Commit your changes\n4. Open a Pull Request."
            elif section == "license":
                ans = "See LICENSE file in repository for license type."
        sections[section] = ans

    return sections