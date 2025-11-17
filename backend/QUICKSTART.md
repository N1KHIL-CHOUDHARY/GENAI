# Quick Start Guide

## Setup in 5 Minutes

### 1. Install Python Dependencies

```bash
cd GENAI/backend
pip install -r requirements.txt
```

### 2. Set Up MongoDB

**Option A: Local MongoDB**

Start MongoDB service:
```bash
# On Windows
net start MongoDB

# On Linux/Mac  
sudo systemctl start mongod
```

**Option B: MongoDB Atlas (Cloud)**

Get connection string from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).

Then set environment variables:

```bash
# For local MongoDB
export MONGODB_URI="mongodb://localhost:27017/"

# OR for MongoDB Atlas
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/"

export MONGODB_DB_NAME="legal_doc_assistant"
```

**Note**: Without MongoDB connection, the backend will run in mock mode (database operations will not persist, but the API will still be available for testing).

### 3. Set Up Google Cloud (Optional - for AI features)

If you want to use AI features (document summarization and RAG chat):

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

**Note**: Without Google Cloud credentials, AI features will not work, but basic API endpoints will still function.

### 4. Run the Server

```bash
python run.py
```

The server will start at `http://localhost:8000`.

### 5. Test the API

- Visit `http://localhost:8000/docs` for interactive API documentation
- The API is ready to accept requests from the frontend at `http://localhost:5173`

## Endpoints Overview

1. **POST /auth/register** - Register a new user
2. **POST /auth/login** - Login user
3. **GET /documents/user/{user_id}** - Get user's documents
4. **POST /documents/upload** - Upload and analyze a PDF
5. **GET /analysis/{documentId}** - Get document analysis
6. **POST /chat/user** - Chat with documents using RAG

## Troubleshooting

### Error: "No module named 'langchain'"
- Run: `pip install -r requirements.txt`

### Error: "FAISS not found"
- Install system dependencies or use: `pip install faiss-cpu`

### Error: "MongoDB connection failed"
- Ensure MongoDB is running (check with `mongosh` or MongoDB Compass)
- Verify `MONGODB_URI` is set correctly
- For MongoDB Atlas, check your IP whitelist and credentials
- Or run in mock mode (data won't persist)

### Error: "Google Cloud credentials not found"
- Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable for AI features
- Without it, AI features won't work but basic API will function

### Port 8000 already in use
- Change port in `app/config.py` or set `API_PORT` environment variable

## Next Steps

1. Configure MongoDB for data persistence
2. Set up Google Cloud for AI features (optional)
3. Set up environment variables for production
4. Review `README.md` for detailed documentation

