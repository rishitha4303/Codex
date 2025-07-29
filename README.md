# Codex: Your AI-Powered GitHub Repository Assistant

Codex is a powerful web application designed to simplify and enhance your interaction with GitHub repositories. It provides intelligent tools for generating README files, summarizing code, and querying codebases directly. Key features include secure user authentication, a user-friendly interface, and integration with various AI models for advanced code analysis. Codex leverages a robust backend to provide efficient and reliable services.

![JavaScript](https://img.shields.io/badge/-JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![React](https://img.shields.io/badge/-React-61DAFB?style=flat&logo=react&logoColor=black)
![Node.js](https://img.shields.io/badge/-Node.js-339933?style=flat&logo=node.js&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

- **README Generator**: Automatically generates comprehensive README files for any GitHub repository, including detailed descriptions and dependency lists.
- **Code Summarizer**: Quickly generates concise summaries of individual files or entire repositories, saving you time and effort.
- **Code Querying**: Allows users to ask natural language questions about a repository's codebase and receive accurate answers.
- **User Authentication**: Securely manages user accounts and protects access to sensitive features.

## 🛠️ Technology Stack

### Frontend
React, React Router, Axios, Lucide-React, React Markdown, Remark-GFM, CSS

### Backend
Flask, Python, Llama, ChromaDB, PyMongo, Google Generative AI, Node.js, Express.js, Mongoose, MongoDB

## 📁 Project Structure

```
├── client
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── src
│   │   ├── App.jsx
│   │   ├── components
│   │   │   ├── GraphViewer.jsx
│   │   │   └── PrivateRoute.jsx
│   │   ├── main.jsx
│   │   ├── pages
│   │   │   ├── Dashboard.jsx
│   │   │   ├── FileToFileSummarizer.jsx
│   │   │   ├── GraphPage.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── MainPage.jsx
│   │   │   ├── ReadmeGenerator.jsx
│   │   │   └── Signup.jsx
│   │   └── utils
│   │       └── auth.js
│   └── vite.config.js
├── flask-ai
│   ├── app.py
│   ├── dependency_graph.py
│   ├── embedding_store.py
│   ├── file_summarizer.py
│   ├── github_parser.py
│   ├── lib
│   │   ├── bindings
│   │   │   └── utils.js
│   │   ├── tom-select
│   │   │   └── tom-select.complete.min.js
│   │   └── vis-9.1.2
│   │       └── vis-network.min.js
│   ├── package.json
│   ├── readme_generator.py
│   └── static
│       └── repo_graph.html
└── server
    ├── index.js
    ├── models
    │   └── User.js
    ├── package.json
    └── routes
        └── auth.js
```

## 💻 Usage

- **README Generator**: Enter a GitHub repository URL, and Codex will generate a README file. You can then download or copy or preview the generated README.
- **Code Summarizer**: Provide a GitHub repository URL, and Codex will generate file to file summaries. Download the summaries as a PDF.
- **Code Querying**: Input a repository URL, select a branch, ask your code related question and receive relevant answers.
- **User Authentication**: Create an account or log in to access the application's features.

## 🚀 Installation

### Backend (Flask)
Navigate to the flask-ai directory. Install dependencies using `pip install -r requirements.txt`. Run the application using `python app.py`.

### Frontend (React)
Navigate to the client directory. Install dependencies using `npm install`. Run the application using `npm run dev`.

### Backend (Node.js)
Navigate to the server directory. Install dependencies using `npm install`. Run the application using `node index.js`.

## 📄 License

This project is licensed under the MIT License.
