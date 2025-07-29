# Codex - AI-Powered Github repository Assistant

A comprehensive web application that provides AI-powered code analysis, documentation generation, and repository insights.

## Features

- **File Summarization**: AI-powered analysis and summarization of code files
- **README Generation**: Automatic README file generation for repositories
- **Dependency Graph Visualization**: Interactive visualization of project dependencies
- **GitHub Repository Analysis**: Parse and analyze GitHub repositories
- **User Authentication**: Secure user registration and login system
- **Graph Visualization**: Interactive network graphs for code relationships

## Project Structure

```
├── client/                 # React frontend (Vite + React)
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── pages/         # Application pages
│   │   └── utils/         # Utility functions
│   └── public/            # Static assets
├── flask-ai/              # Python Flask backend with AI features
│   ├── app.py            # Main Flask application
│   ├── github_parser.py  # GitHub repository parsing
│   ├── file_summarizer.py # AI file summarization
│   ├── readme_generator.py # README generation
│   ├── dependency_graph.py # Dependency analysis
│   └── embedding_store.py # Vector embeddings storage
├── server/                # Node.js authentication server
│   ├── routes/           # API routes
│   └── models/           # Database models
└── lib/                  # External libraries and dependencies
```

## Tech Stack

### Frontend
- **React** with Vite for fast development
- **CSS3** for styling
- **Vis.js** for graph visualization

### Backend
- **Flask** (Python) for AI services
- **Node.js** with Express for authentication
- **LlamaIndex** for AI-powered analysis
- **ChromaDB** for vector storage
- **PyVis** for graph generation

### AI/ML
- **LlamaIndex** for document processing
- **OpenAI/Hugging Face** models for text analysis
- **Vector embeddings** for semantic search

## Setup and Installation

### Prerequisites
- Node.js (v14 or higher)
- Python 3.8+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Vasita27/Codex.git
cd Codex
```

### 2. Setup Backend (Flask AI)
```bash
cd flask-ai
pip install -r requirements.txt
python app.py
```

### 3. Setup Authentication Server
```bash
cd server
npm install
npm start
```

### 4. Setup Frontend
```bash
cd client
npm install
npm run dev
```

## Environment Variables

Create `.env` files in the respective directories:

### flask-ai/.env
```
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_token
```

### server/.env
```
JWT_SECRET=your_jwt_secret
DATABASE_URL=your_database_url
```

## Usage

1. **Start all services** in the following order:
   - Flask AI backend: `python flask-ai/app.py`
   - Authentication server: `npm start` in server/
   - Frontend: `npm run dev` in client/

2. **Access the application** at `http://localhost:5173`

3. **Key Features**:
   - Upload or link GitHub repositories for analysis
   - Generate comprehensive README files
   - Visualize project dependencies
   - Get AI-powered file summaries

## API Endpoints

### Flask AI Service
- `POST /summarize` - Summarize code files
- `POST /generate-readme` - Generate README files
- `GET /dependency-graph` - Get dependency visualization
- `POST /parse-github` - Parse GitHub repositories

### Authentication Service
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/verify` - Token verification

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LlamaIndex for AI document processing
- Vis.js for graph visualization
- React and Vite for the frontend framework
- Flask for the backend API

---

**Note**: Make sure to set up your API keys and environment variables before running the application.
