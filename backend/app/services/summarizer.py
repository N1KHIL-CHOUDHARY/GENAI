"""AI-powered document summarization using Vertex AI Gemini."""
import json
import re
import asyncio
from typing import Dict, Any
from langchain_google_vertexai import ChatVertexAI
from pydantic import ValidationError
from app.models import AnalysisReport, RiskItem, DecisionAssist
from app.services.extractor import load_extracted_text
from app.config import GEMINI_MODEL_NAME, VERTEX_AI_LOCATION, GOOGLE_CLOUD_PROJECT


def get_summarization_prompt(text: str) -> str:
    """Generate the prompt for document summarization."""
    return f"""You are a legal clarity assistant specializing in analyzing legal documents and contracts. 
Analyze the following document and provide a comprehensive structured analysis.

Document Text:
{text[:10000]}  # Limit to first 10k chars to avoid token limits

Please analyze this document and return a JSON object with the following structure:
{{
    "summary": ["point 1", "point 2", ...],  // A list of summary points (strings)
    "key_terms": ["term1", "term2", ...],  // Important legal terms found in the document
    "obligations": {{  // Key obligations organized by party or topic
        "Party A": ["obligation 1", "obligation 2"],
        "Party B": ["obligation 1", "obligation 2"]
    }},
    "costs_and_payments": ["cost/payment point 1", ...],  // Financial obligations and costs
    "risks": [  // Risk assessment
        {{
            "title": "Risk title",
            "why_it_matters": "Explanation of why this risk matters",
            "where_found": "Section or clause reference (optional)",
            "mitigations": ["mitigation 1", "mitigation 2"]
        }}
    ],
    "red_flags": ["flag 1", "flag 2", ...],  // Critical issues or warning signs
    "questions_to_ask": ["question 1", "question 2", ...],  // Questions to clarify with the other party
    "negotiation_suggestions": ["suggestion 1", ...],  // Recommendations for negotiation
    "decision_assist": {{
        "pros": ["pro 1", "pro 2", ...],
        "cons": ["con 1", "con 2", ...],
        "overall_take": "Overall assessment and recommendation"
    }}
}}

IMPORTANT: Return ONLY valid JSON. Do not include any markdown formatting, code blocks, or additional text.
The JSON must be valid and parseable."""


def clean_json_response(response_text: str) -> str:
    """Clean and extract JSON from model response."""
    # Remove markdown code blocks if present
    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*', '', response_text)
    response_text = response_text.strip()
    
    # Try to find JSON object in the response
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        return json_match.group(0)
    
    return response_text


def validate_and_coerce_analysis(data: Dict[str, Any]) -> AnalysisReport:
    """Validate and coerce the analysis data to match the Pydantic model."""
    try:
        # Ensure all required fields exist with defaults
        if "summary" not in data:
            data["summary"] = []
        if "key_terms" not in data:
            data["key_terms"] = []
        if "obligations" not in data:
            data["obligations"] = {}
        if "costs_and_payments" not in data:
            data["costs_and_payments"] = []
        if "risks" not in data:
            data["risks"] = []
        if "red_flags" not in data:
            data["red_flags"] = []
        if "questions_to_ask" not in data:
            data["questions_to_ask"] = []
        if "negotiation_suggestions" not in data:
            data["negotiation_suggestions"] = []
        if "decision_assist" not in data:
            data["decision_assist"] = {"pros": [], "cons": [], "overall_take": ""}
        
        # Validate risks
        validated_risks = []
        for risk in data.get("risks", []):
            if isinstance(risk, dict):
                if "title" not in risk:
                    risk["title"] = "Untitled Risk"
                if "why_it_matters" not in risk:
                    risk["why_it_matters"] = ""
                if "mitigations" not in risk:
                    risk["mitigations"] = []
                validated_risks.append(risk)
        data["risks"] = validated_risks
        
        # Validate decision_assist
        if isinstance(data["decision_assist"], dict):
            if "pros" not in data["decision_assist"]:
                data["decision_assist"]["pros"] = []
            if "cons" not in data["decision_assist"]:
                data["decision_assist"]["cons"] = []
            if "overall_take" not in data["decision_assist"]:
                data["decision_assist"]["overall_take"] = ""
        
        return AnalysisReport(**data)
    except ValidationError as e:
        print(f"Validation error: {e}")
        # Return a minimal valid report
        return AnalysisReport()


def _summarize_document_sync(doc_id: str) -> AnalysisReport:
    """
    Synchronous implementation of document summarization.
    
    Args:
        doc_id: The document ID
        
    Returns:
        AnalysisReport: The structured analysis report
    """
    # Load extracted text
    text = load_extracted_text(doc_id)
    if not text:
        raise ValueError(f"No extracted text found for document {doc_id}")
    
    response_text = ""
    try:
        # Initialize Vertex AI chat model
        llm = ChatVertexAI(
            model_name=GEMINI_MODEL_NAME,
            location=VERTEX_AI_LOCATION,
            project=GOOGLE_CLOUD_PROJECT if GOOGLE_CLOUD_PROJECT else None,
            temperature=0.2,
            max_output_tokens=4096,
        )
        
        # Generate prompt
        prompt = get_summarization_prompt(text)
        
        # Get response from model
        response = llm.invoke(prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Clean and parse JSON
        json_text = clean_json_response(response_text)
        analysis_data = json.loads(json_text)
        
        # Validate and coerce to model
        report = validate_and_coerce_analysis(analysis_data)
        
        return report
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        if response_text:
            print(f"Response text: {response_text[:500]}")
        # Return minimal valid report on error
        return AnalysisReport()
    except Exception as e:
        print(f"Error summarizing document: {e}")
        # Return minimal valid report on error
        return AnalysisReport()


async def summarize_document(doc_id: str) -> AnalysisReport:
    """
    Generate an AI summary for a document (async wrapper).
    
    Args:
        doc_id: The document ID
        
    Returns:
        AnalysisReport: The structured analysis report
    """
    return await asyncio.to_thread(_summarize_document_sync, doc_id)

