"""PDF text extraction module."""
import os
from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader
from app.config import TEXT_CACHE_DIR


def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def save_extracted_text(doc_id: str, text: str) -> bool:
    """Save extracted text to cache file."""
    try:
        text_file = TEXT_CACHE_DIR / f"extract_{doc_id}.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    except Exception as e:
        print(f"Error saving extracted text: {e}")
        return False


def load_extracted_text(doc_id: str) -> Optional[str]:
    """Load extracted text from cache file."""
    try:
        text_file = TEXT_CACHE_DIR / f"extract_{doc_id}.txt"
        if not text_file.exists():
            return None
        
        with open(text_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading extracted text: {e}")
        return None

