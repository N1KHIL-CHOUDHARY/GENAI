"""FastAPI main application."""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from app.models import (
    UserModel,
    LoginRequest,
    RegisterRequest,
    ChatRequest,
    AnalysisReport
)
from app.config import CORS_ORIGINS
from app.services.firestore_manager import (
    save_user,
    authenticate_user,
    get_documents_by_user_id,
    save_document_summary,
    get_document_by_id
)
from app.services.document_processor import process_document
from app.services.summarizer import summarize_document
from app.services.qa_engine import chat_with_documents

# Initialize FastAPI app
app = FastAPI(
    title="Legal Document Assistant API",
    description="FastAPI backend for AI-powered legal document analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Legal Document Assistant API",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/auth/register", response_model=Dict[str, Any])
async def register(request: RegisterRequest):
    """Register a new user."""
    try:
        user_id = save_user(request.name, request.email, request.password)
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Failed to create user")
        
        return {
            "message": "User registered",
            "user": {
                "id": user_id,
                "name": request.name,
                "email": request.email
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/auth/login", response_model=Dict[str, Any])
async def login(request: LoginRequest):
    """Login an existing user."""
    user = authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "message": "Login successful",
        "user": {
            "id": user.get("id", ""),
            "name": user.get("name", ""),
            "email": user.get("email", "")
        }
    }


@app.get("/documents/user/{user_id}", response_model=Dict[str, Any])
async def get_user_documents(user_id: str):
    """Get all documents for a user."""
    try:
        documents = get_documents_by_user_id(user_id)
        
        return {
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")


@app.post("/documents/upload", response_model=Dict[str, Any])
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    """Upload and analyze a document."""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Process document (save file and extract text)
        doc_id, filename, extracted_text = await process_document(file)
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
        
        # Generate AI summary
        try:
            summary_report = await summarize_document(doc_id)
            summary_dict = summary_report.model_dump()
        except Exception as e:
            print(f"Error generating summary: {e}")
            # Return minimal summary on error
            summary_dict = {
                "summary": ["Document uploaded successfully. Analysis may be incomplete."],
                "key_terms": [],
                "obligations": {},
                "costs_and_payments": [],
                "risks": [],
                "red_flags": [],
                "questions_to_ask": [],
                "negotiation_suggestions": [],
                "decision_assist": {
                    "pros": [],
                    "cons": [],
                    "overall_take": "Analysis pending"
                }
            }
        
        # Save document summary to Firestore
        save_document_summary(
            user_id=user_id,
            doc_id=doc_id,
            doc_name=filename,
            summary=summary_dict
        )
        
        return {
            "doc_id": doc_id,
            "meta": {
                "filename": filename
            },
            "summary": summary_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.get("/analysis/{documentId}", response_model=Dict[str, Any])
async def get_analysis(documentId: str):
    """Get analysis for a document (re-runs or fetches from cache)."""
    try:
        # Try to get from Firestore first
        doc = get_document_by_id(documentId)
        if doc and doc.get("summary"):
            return doc["summary"]
        
        # If not in Firestore, generate new analysis
        summary_report = await summarize_document(documentId)
        return summary_report.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analysis: {str(e)}")


@app.post("/chat/user", response_model=Dict[str, str])
async def chat_user(request: ChatRequest):
    """Chat with documents using RAG."""
    try:
        # Get all documents for the user
        documents = get_documents_by_user_id(request.user_id)
        
        if not documents:
            return {
                "response": "You don't have any documents yet. Please upload a document first."
            }
        
        # Extract document IDs
        doc_ids = [doc.get("doc_id") for doc in documents if doc.get("doc_id")]
        
        if not doc_ids:
            return {
                "response": "No valid documents found. Please upload a document first."
            }
        
        # Get AI response using RAG
        response_text = await chat_with_documents(doc_ids, request.query)
        
        return {
            "response": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    from app.config import API_HOST, API_PORT
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True
    )

