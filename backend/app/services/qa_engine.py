"""RAG-based question-answering engine using FAISS and Vertex AI."""
import os
import asyncio
from typing import List, Optional
from pathlib import Path
from langchain_google_vertexai import ChatVertexAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.extractor import load_extracted_text
from app.config import (
    VECTOR_STORE_DIR,
    EMBEDDINGS_MODEL_NAME,
    GEMINI_MODEL_NAME,
    VERTEX_AI_LOCATION,
    GOOGLE_CLOUD_PROJECT
)


# Initialize embeddings
try:
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL_NAME)
except Exception as e:
    print(f"Warning: Could not load embeddings model: {e}")
    embeddings = None


def get_or_create_vector_store(doc_ids: List[str]) -> Optional[FAISS]:
    """Get or create a FAISS vector store for the given documents."""
    if embeddings is None:
        return None
    
    # Create a combined store name from all doc IDs
    store_name = "_".join(sorted(doc_ids))
    store_path = VECTOR_STORE_DIR / f"{store_name}.faiss"
    
    # Try to load existing store
    if store_path.exists() and (VECTOR_STORE_DIR / f"{store_name}.pkl").exists():
        try:
            return FAISS.load_local(
                str(VECTOR_STORE_DIR),
                embeddings,
                allow_dangerous_deserialization=True,
                index_name=store_name
            )
        except Exception as e:
            print(f"Error loading vector store: {e}")
    
    # Create new vector store
    all_texts = []
    for doc_id in doc_ids:
        text = load_extracted_text(doc_id)
        if text:
            all_texts.append(text)
    
    if not all_texts:
        return None
    
    # Combine all texts
    combined_text = "\n\n---DOCUMENT SEPARATOR---\n\n".join(all_texts)
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(combined_text)
    
    if not chunks:
        return None
    
    # Create vector store
    try:
        vector_store = FAISS.from_texts(chunks, embeddings)
        
        # Save vector store
        vector_store.save_local(
            str(VECTOR_STORE_DIR),
            index_name=store_name
        )
        
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None


def get_qa_prompt(query: str, context: str) -> str:
    """Generate the prompt for question answering."""
    return f"""You are a helpful legal document assistant. Answer the user's question based on the following document context.

Document Context:
{context}

User Question: {query}

Provide a clear, concise, and accurate answer based solely on the document context provided. If the context doesn't contain enough information to answer the question, say so. Do not make up information.

Answer:"""


def _chat_with_documents_sync(doc_ids: List[str], query: str) -> str:
    """
    Synchronous implementation of chat with documents.
    
    Args:
        doc_ids: List of document IDs to search
        query: User's question
        
    Returns:
        str: The AI's answer
    """
    if not doc_ids:
        return "No documents available to answer your question."
    
    try:
        # Get or create vector store
        vector_store = get_or_create_vector_store(doc_ids)
        if vector_store is None:
            return "Error: Could not create vector store from documents. Please ensure documents are properly processed."
        
        # Perform similarity search
        docs = vector_store.similarity_search(query, k=3)
        
        # Combine context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Initialize LLM
        llm = ChatVertexAI(
            model_name=GEMINI_MODEL_NAME,
            location=VERTEX_AI_LOCATION,
            project=GOOGLE_CLOUD_PROJECT if GOOGLE_CLOUD_PROJECT else None,
            temperature=0.3,
            max_output_tokens=2048,
        )
        
        # Generate answer
        prompt = get_qa_prompt(query, context)
        response = llm.invoke(prompt)
        
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        print(f"Error in chat_with_documents: {e}")
        return f"Sorry, I encountered an error while processing your question: {str(e)}"


async def chat_with_documents(doc_ids: List[str], query: str) -> str:
    """
    Answer a question using RAG with the given documents (async wrapper).
    
    Args:
        doc_ids: List of document IDs to search
        query: User's question
        
    Returns:
        str: The AI's answer
    """
    return await asyncio.to_thread(_chat_with_documents_sync, doc_ids, query)

