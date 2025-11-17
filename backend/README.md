# Legal Document Assistant - FastAPI Backend

FastAPI backend for the Legal Document Assistant web application, providing AI-powered document analysis, summarization, and RAG-based question answering.

## Features

- **User Authentication**: Registration and login with MongoDB
- **Document Processing**: PDF upload and text extraction
- **AI Summarization**: Structured document analysis using Vertex AI Gemini
- **RAG Chat**: Question-answering using FAISS vector search and Gemini
- **MongoDB Integration**: Persistent storage for users and documents

## Technology Stack

- **Framework**: FastAPI
- **Database**: MongoDB
- **AI Models**: Google Cloud Vertex AI (Gemini)
- **Text Extraction**: PyPDF2
- **Vector Store**: FAISS
- **Embeddings**: HuggingFace Sentence Transformers

## Prerequisites

- Python 3.9 or higher (Python 3.10+ recommended)
- MongoDB (local or cloud instance like MongoDB Atlas)
- Google Cloud Project with Vertex AI enabled (for AI features)
- Service account with appropriate permissions (for Vertex AI)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Note: Some dependencies may require additional system libraries (e.g., FAISS requires C++ build tools).

### 2. Set Up MongoDB

**Option A: Local MongoDB**

1. Install MongoDB locally ([Download](https://www.mongodb.com/try/download/community))
2. Start MongoDB service:
   ```bash
   # On Windows
   net start MongoDB
   
   # On Linux/Mac
   sudo systemctl start mongod
   ```

**Option B: MongoDB Atlas (Cloud)**

1. Create a free account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster and database
3. Get your connection string from the Atlas dashboard

### 3. Configure Environment Variables

Set up your environment variables:

```bash
# MongoDB Configuration
export MONGODB_URI="mongodb://localhost:27017/"  # For local MongoDB
# OR for MongoDB Atlas:
# export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/"
export MONGODB_DB_NAME="legal_doc_assistant"

# Google Cloud Configuration (for Vertex AI)
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
export VERTEX_AI_LOCATION="us-central1"
export GEMINI_MODEL_NAME="gemini-2.0-flash-exp"
export EMBEDDINGS_MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"

# API Configuration
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

Or create a `.env` file with these variables:

```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=legal_doc_assistant
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
VERTEX_AI_LOCATION=us-central1
GEMINI_MODEL_NAME=gemini-2.0-flash-exp
EMBEDDINGS_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
API_HOST=0.0.0.0
API_PORT=8000
```

**Note**: MongoDB is required for the application to work. Vertex AI is optional (needed for AI features).

### 4. Run the Server

```bash
# Option 1: Using the run script (recommended for development)
python run.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using Python module
python -m app.main
```

The API will be available at `http://localhost:8000`.
You can access the interactive API documentation at `http://localhost:8000/docs`.

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user

### Documents

- `GET /documents/user/{user_id}` - Get all documents for a user
- `POST /documents/upload` - Upload and analyze a PDF document

### Analysis

- `GET /analysis/{documentId}` - Get analysis for a document

### Chat

- `POST /chat/user` - Chat with documents using RAG

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # Pydantic models
│   ├── config.py            # Configuration settings
│   └── services/
│       ├── __init__.py
│       ├── firestore_manager.py    # MongoDB database operations
│       ├── document_processor.py   # Document upload and processing
│       ├── extractor.py            # PDF text extraction
│       ├── summarizer.py           # AI summarization
│       └── qa_engine.py            # RAG question-answering
├── tmp/
│   ├── cache/              # Uploaded files and extracted text
│   └── data/               # FAISS vector stores
├── requirements.txt
├── .env.example
└── README.md
```

## Notes

- The backend runs on `localhost:8000` by default
- CORS is configured to allow requests from `localhost:5173` (frontend)
- MongoDB must be running before starting the backend
- Extracted text is cached in `tmp/cache/` directory
- FAISS vector stores are cached in `tmp/data/` directory
- Passwords are hashed using SHA256 (consider using bcrypt in production)
- The application will run in mock mode if MongoDB connection fails (limited functionality)

## Development

For development with hot-reload:

```bash
uvicorn app.main:app --reload
```

## Production Considerations

- Use environment variables for all sensitive configuration
- Implement proper password hashing (bcrypt/argon2)
- Add rate limiting
- Implement proper authentication tokens (JWT)
- Add logging and monitoring
- Set up proper error handling and logging
- Use MongoDB Atlas or a managed MongoDB service for production
- Consider using a proper file storage service (S3/GCS) instead of local cache
- Add database indexes for frequently queried fields (email, user_id)
- Add API documentation at `/docs` (FastAPI automatic docs)
- Enable MongoDB authentication in production
- Use connection pooling for better performance

