import os
import json
import re
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class ReadmeGenerator:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        print("Loaded GEMINI_API_KEY:", api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_readme(self, github_url) -> str:
        from github_parser import GitHubParser
        parser = GitHubParser(github_url)
        repo_data = parser.get_repo_data()
        print("Repository parsed. Starting file summarization...")
        return self.generate_readme_content(repo_data)

    def analyze_repo_structure(self, repo_data):
        files = repo_data.get('files', {})
        categorized = {
            'config_files': [],
            'main_files': [],
            'frontend_files': [],
            'backend_files': [],
            'test_files': [],
            'documentation': [],
            'assets': []
        }
        for file_path, file_info in files.items():
            if "node_modules/" in file_path.replace("\\", "/"):
                continue
            if file_info.get('type') != 'file':
                continue
            ext = os.path.splitext(file_path)[-1].lower()
            if ext in ['.json', '.yml', '.yaml', '.env', '.lock', '.conf', '.ini'] or 'config' in file_path.lower():
                categorized['config_files'].append(file_path)
            elif ext in ['.js', '.jsx', '.ts', '.tsx']:
                categorized['main_files'].append(file_path)
            elif ext in ['.css', '.scss', '.sass', '.less', '.html', '.htm']:
                categorized['frontend_files'].append(file_path)
            elif ext in ['.py', '.java', '.php', '.rb', '.go', '.rs']:
                categorized['backend_files'].append(file_path)
            elif ext in ['.md'] or any(name in file_path.lower() for name in ['readme', 'changelog', 'contributing', 'license']):
                categorized['documentation'].append(file_path)
            elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf', '.doc', '.docx']:
                categorized['assets'].append(file_path)
            elif ext in ['.test.js', '.test.ts', '.spec.js', '.spec.ts']:
                categorized['test_files'].append(file_path)
        return categorized

    def extract_dependencies(self, files):
        dependencies = {'npm': [], 'pip': []}
        package_json_files = [f for f in files.keys() if f.endswith('package.json')]
        for file_path in package_json_files:
            try:
                content = files[file_path].get('content', '')
                if content:
                    package_data = json.loads(content)
                    deps = package_data.get('dependencies', {})
                    dev_deps = package_data.get('devDependencies', {})
                    dependencies['npm'].extend(list(deps.keys()) + list(dev_deps.keys()))
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        req_files = [f for f in files.keys() if f.endswith('requirements.txt')]
        for file_path in req_files:
            try:
                content = files[file_path].get('content', '')
                if content:
                    deps = [line.split('==')[0].split('>=')[0].split('<=')[0]
                           for line in content.split('\n') if line.strip() and not line.startswith('#')]
                    dependencies['pip'].extend(deps)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        return dependencies

    def should_skip_summary(self, file_path):
        fname = os.path.basename(file_path).lower()
        if fname == "package.json":
            return True
        if fname.startswith("setup"):
            return True
        if fname.startswith("test") or fname.endswith(".test.js") or fname.endswith(".spec.js") or fname.endswith(".test.ts") or fname.endswith(".spec.ts"):
            return True
        if fname == "vite.config.js":
            return True
        if fname == "eslint.config.js":
            return True
        if "tailwind" in fname:
            return True
        if "postcss" in fname:
            return True
        if "autoprefixer" in fname:
            return True
        return False

    def extract_imports_or_libs(self, content, file_path):
        imports = set()
        ext = os.path.splitext(file_path)[-1].lower()
        if ext in (".js", ".jsx", ".ts", ".tsx"):
            for match in re.findall(r'import\s+(?:[^"\']+\s+from\s+)?[\'"]([^\'"]+)[\'"]', content):
                imports.add(match.split('/')[0])
            for match in re.findall(r'require\([\'"]([^\'"]+)[\'"]\)', content):
                imports.add(match.split('/')[0])
        elif ext == ".py":
            for match in re.findall(r'^\s*import\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE):
                imports.add(match.split('.')[0])
            for match in re.findall(r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import', content, re.MULTILINE):
                imports.add(match.split('.')[0])
        elif ext in (".html", ".htm"):
            for match in re.findall(r'<script.*?src="([^"]+)"', content):
                imports.add(match.split('/')[0])
            for match in re.findall(r'<link.*?href="([^"]+)"', content):
                imports.add(match.split('/')[0])
        elif ext in (".yml", ".yaml"):
            for match in re.findall(r'image:\s*([^\s]+)', content):
                imports.add(match.split('/')[0])
        return [i for i in imports if i]

    def generate_main_feature_summaries(self, repo_data):
        from concurrent.futures import ThreadPoolExecutor, as_completed

        files = repo_data.get('files', {})
        summaries = []

        print("🧠 Summarizing files using Gemini...")

        def summarize_file(file_path, file_info):
            try:
                if not isinstance(file_info, dict) or file_info.get('type') != 'file':
                    return None
                if self.should_skip_summary(file_path):
                    return None

                ext = os.path.splitext(file_path)[-1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf', '.doc', '.docx']:
                    return None

                content = file_info.get('content', '')
                if not content or len(content) < 20:
                    return None

                libs = self.extract_imports_or_libs(content, file_path)
                libs_str = ", ".join(sorted(libs)) if libs else ""
                prompt = (
                    "Provide a clear, high-level summary in 2–3 short sentences describing the main feature or purpose of this code file for a project README. "
                    "Focus on what this file enables for users or the application overall. "
                    "Do NOT include implementation details or mention the file name or path. "
                    "After the summary, add in square brackets a comma-separated list of the key technologies, libraries, or imports used in this file, as detected from the code itself. "
                    "Format: <summary> [Imports/Libraries: ...].\n"
                    f"File: {file_path}\n"
                    f"---\n{content[:3000]}"
                )

                retries = 3
                delay = 5

                for attempt in range(retries):
                    try:
                        response = self.model.generate_content(prompt)
                        text = response.text.strip().replace("\n", " ")
                        return f"- **{file_path}**: {text}" if text else None
                    except Exception as e:
                        if "429" in str(e) or "rate limit" in str(e).lower():
                            wait = delay * (attempt + 1)
                            print(f"⚠️ Rate limited on {file_path}, retrying in {wait}s...")
                            time.sleep(wait)
                        else:
                            print(f"❌ Error summarizing {file_path}: {e}")
                            return None
                return None
            except Exception as e:
                print(f"❌ Unexpected error on {file_path}: {e}")
                return None

        # Use thread pool for concurrency (safe for I/O-bound ops like API calls)
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(summarize_file, path, info): path
                for path, info in files.items()
            }
            for future in as_completed(future_to_file):
                result = future.result()
                if result:
                    summaries.append(result)

        print("\n✅ Summarization complete. Top 5 file summaries:")
        for s in summaries[:5]:
            print(s)

        return "\n".join(summaries)


    def _generate_project_tree(self, repo_data):
        files = repo_data.get('files', {})
        tree = {}
        for path in files.keys():
            if "node_modules/" in path.replace("\\", "/"):
                continue
            parts = path.replace("\\", "/").split('/')
            curr = tree
            for part in parts:
                curr = curr.setdefault(part, {})
        def render(d, prefix=''):
            lines = []
            keys = list(d.keys())
            for i, k in enumerate(sorted(keys)):
                connector = '└── ' if i == len(keys) - 1 else '├── '
                if d[k]:
                    lines.append(f"{prefix}{connector}{k}")
                    extension = '    ' if i == len(keys) - 1 else '│   '
                    lines.extend(render(d[k], prefix + extension))
                else:
                    lines.append(f"{prefix}{connector}{k}")
            return lines
        # Always print the full project structure, including a few files for each directory
        top_level = [k for k in tree.keys()]
        if len(top_level) == 1:
            root = top_level[0]
            root_tree = tree[root]
            structure = f"{root}/\n" + "\n".join(render(root_tree))
        else:
            structure = "\n".join(render(tree))
        return structure

    def generate_readme_content(self, repo_data):
        dependencies = self.extract_dependencies(repo_data['files'])
        main_feature_summaries = self.generate_main_feature_summaries(repo_data)
        project_tree = self._generate_project_tree(repo_data)
        context = {
            'repo_name': repo_data.get('name', 'Unknown'),
            'description': repo_data.get('description', ''),
            'language': repo_data.get('language', 'Multiple'),
            'dependencies': dependencies,
            'main_feature_summaries': main_feature_summaries,
            'project_tree': project_tree
        }
        dependencies_info = "\n".join([
            f"**{dep_type.upper()}:** {', '.join(deps[:10])}" +
            (f" (+{len(deps)-10} more)" if len(deps) > 10 else "")
            for dep_type, deps in context['dependencies'].items() if deps
        ])

        prompt =  f"""
Write a professional, modern, and user-focused README.md for the repository **{context['repo_name']}**.

- **Description:** In 4-5 sentences, describe what the project is, its main purpose, and what makes it valuable. Briefly mention the main features (by name only, in running text), and ensure all features are included.
- Directly after description in new line add at least 4–5 relevant badges (such as main language or key technology badges) based on the detected dependencies and project context. Format them with markdown and ensure they look visually appealing and are relevant to the stack.
- **Features:** List the major features (based on all file summaries), each with a clear, concise (1–2 lines) description focused on the user experience. Do NOT mention or reference file paths or file/component names.
- **Technology Stack:** List the main technologies and frameworks, using the dependencies info.
- **Project Structure:** Present the full, neatly formatted project tree below as a code block. Do NOT truncate or summarize with ellipses—always show several files under each folder and show the entire structure that was generated.
- **Usage:** For each main feature, write a short, user-oriented flow (1–2 lines) on how a typical user would use or experience that feature. Do NOT include code, file paths, or component names. Flows should read naturally.
- **Installation:** Provide setup steps using the dependencies info.
- **Contributing & License:** Add standard sections briefly explaining how to contribute and the license type, using standard templates.
- Use clear markdown and relevant emojis.
- Do NOT speculate or add empty/unmentioned sections.
- Base all content on the provided main file summaries, project tree, and dependencies info.

**Context:**
Main file summaries:
{context['main_feature_summaries']}

Project tree:
{context['project_tree']}

Dependencies info:
{dependencies_info}
"""
        try:
            response = self.model.generate_content(prompt)
            print("Gemini AI generated README.")
            return response.text
        except Exception as e:
            print("Gemini AI error:", e)
            return "# Error generating README: " + str(e)