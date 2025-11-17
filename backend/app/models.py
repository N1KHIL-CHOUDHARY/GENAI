"""Pydantic models for document analysis."""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    """Model for risk items in document analysis."""
    title: str
    why_it_matters: str
    where_found: Optional[str] = None
    mitigations: List[str] = Field(default_factory=list)


class DecisionAssist(BaseModel):
    """Model for decision assistance in document analysis."""
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    overall_take: str


class AnalysisReport(BaseModel):
    """Complete analysis report model."""
    summary: List[str] = Field(default_factory=list)
    key_terms: List[str] = Field(default_factory=list)
    obligations: Dict[str, List[str]] = Field(default_factory=dict)
    costs_and_payments: List[str] = Field(default_factory=list)
    risks: List[RiskItem] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    questions_to_ask: List[str] = Field(default_factory=list)
    negotiation_suggestions: List[str] = Field(default_factory=list)
    decision_assist: DecisionAssist = Field(default_factory=DecisionAssist)


class UserModel(BaseModel):
    """User model for API responses."""
    id: str
    name: str
    email: str


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


class RegisterRequest(BaseModel):
    """Registration request model."""
    name: str
    email: str
    password: str


class ChatRequest(BaseModel):
    """Chat request model."""
    user_id: str
    query: str

