"""MongoDB database manager for user and document operations."""
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
from app.config import MONGODB_URI, MONGODB_DB_NAME


# Initialize MongoDB client
db: Optional[Database] = None
try:
    if MONGODB_URI:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB_NAME]
        # Test connection
        client.admin.command('ping')
        print(f"Successfully connected to MongoDB database: {MONGODB_DB_NAME}")
    else:
        print("Warning: MONGODB_URI not set. Using mock mode.")
except Exception as e:
    print(f"Warning: MongoDB initialization error: {e}. Using mock mode.")
    db = None


def hash_password(password: str) -> str:
    """Hash a password (basic implementation - use bcrypt in production)."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get a user by email from MongoDB."""
    if db is None:
        return None
    
    try:
        users_collection: Collection = db["users"]
        user = users_collection.find_one({"email": email})
        
        if user:
            user["id"] = str(user["_id"])
            user.pop("_id", None)
            return user
        return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get a user by ID from MongoDB."""
    if db is None:
        return None
    
    try:
        users_collection: Collection = db["users"]
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        
        if user:
            user["id"] = str(user["_id"])
            user.pop("_id", None)
            return user
        return None
    except Exception as e:
        print(f"Error getting user by ID: {e}")
        return None


def save_user(name: str, email: str, password: str) -> Optional[str]:
    """Save a new user to MongoDB and return the user ID."""
    if db is None:
        # Mock mode: return a fake user ID
        import uuid
        return str(uuid.uuid4())
    
    try:
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        hashed_password = hash_password(password)
        user_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow()
        }
        
        users_collection: Collection = db["users"]
        result = users_collection.insert_one(user_data)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error saving user: {e}")
        raise


def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user by email and password."""
    user = get_user_by_email(email)
    if not user:
        return None
    
    stored_password = user.get("password", "")
    if verify_password(password, stored_password):
        # Remove password from response
        user.pop("password", None)
        return user
    return None


def get_documents_by_user_id(user_id: str) -> List[Dict[str, Any]]:
    """Get all documents for a specific user."""
    if db is None:
        return []
    
    try:
        documents_collection: Collection = db["documents"]
        cursor = documents_collection.find({"user_id": user_id})
        
        documents = []
        for doc in cursor:
            doc["doc_id"] = str(doc["_id"])
            doc.pop("_id", None)
            documents.append(doc)
        
        return documents
    except Exception as e:
        print(f"Error getting documents by user_id: {e}")
        return []


def save_document_summary(
    user_id: str,
    doc_id: str,
    doc_name: str,
    summary: Dict[str, Any]
) -> bool:
    """Save a document summary to MongoDB."""
    if db is None:
        return True  # Mock mode: return success
    
    try:
        documents_collection: Collection = db["documents"]
        doc_data = {
            "_id": ObjectId(doc_id) if ObjectId.is_valid(doc_id) else ObjectId(),
            "user_id": user_id,
            "doc_id": doc_id,
            "doc_name": doc_name,
            "summary": summary,
            "upload_date": datetime.utcnow()
        }
        
        # Use upsert to insert or update
        documents_collection.replace_one(
            {"_id": doc_data["_id"]},
            doc_data,
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving document summary: {e}")
        return False


def get_document_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    """Get a document by its ID."""
    if db is None:
        return None
    
    try:
        documents_collection: Collection = db["documents"]
        
        # Try to find by _id first (if it's a valid ObjectId)
        if ObjectId.is_valid(doc_id):
            doc = documents_collection.find_one({"_id": ObjectId(doc_id)})
            if doc:
                doc["doc_id"] = str(doc["_id"])
                doc.pop("_id", None)
                return doc
        
        # Fallback: search by doc_id field
        doc = documents_collection.find_one({"doc_id": doc_id})
        if doc:
            doc["doc_id"] = str(doc["_id"]) if "_id" in doc else doc_id
            doc.pop("_id", None)
            return doc
        
        return None
    except Exception as e:
        print(f"Error getting document by ID: {e}")
        return None

