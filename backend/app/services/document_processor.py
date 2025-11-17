"""Document processing module for handling file uploads and text extraction."""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from typing import Tuple, Optional
from app.services.extractor import extract_text_from_pdf, save_extracted_text
from app.config import CACHE_DIR


async def process_document(file: UploadFile) -> Tuple[str, str, Optional[str]]:
    """
    Process an uploaded document.
    
    Returns:
        Tuple of (doc_id, filename, extracted_text)
    """
    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    
    # Save uploaded file to cache
    file_extension = Path(file.filename).suffix
    cached_file_path = CACHE_DIR / f"{doc_id}{file_extension}"
    
    try:
        # Save file to disk
        with open(cached_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(str(cached_file_path))
        
        if extracted_text:
            # Save extracted text to cache
            save_extracted_text(doc_id, extracted_text)
        
        return doc_id, file.filename, extracted_text
    except Exception as e:
        print(f"Error processing document: {e}")
        # Clean up on error
        if cached_file_path.exists():
            cached_file_path.unlink()
        raise

