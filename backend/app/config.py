"""Configuration settings for the application."""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Cache directories
CACHE_DIR = BASE_DIR / "tmp" / "cache"
TEXT_CACHE_DIR = BASE_DIR / "tmp" / "cache"
VECTOR_STORE_DIR = BASE_DIR / "tmp" / "data"

# Create directories if they don't exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
TEXT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

# MongoDB Configuration
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Support both MONGODB_URI and MONGO_URI
)
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "legal_doc_assistant")

# Vertex AI Configuration
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")

# Embeddings Configuration
EMBEDDINGS_MODEL_NAME = os.getenv(
    "EMBEDDINGS_MODEL_NAME", 
    "sentence-transformers/all-MiniLM-L6-v2"
)

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

