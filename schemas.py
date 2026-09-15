"""
Data contracts and type definitions for the Inbound Lead Triage Pipeline.
Enforces strict schema validation using Pydantic v2.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class DealTier(str, Enum):
    TIER_1_ENTERPRISE = "TIER_1_ENTERPRISE"   # >$25k budget, 50-300 employees, complex operational workflows
    TIER_2_MIDMARKET = "TIER_2_MIDMARKET"       # $10k-$25k budget, growing teams, specific workflow pain
    TIER_3_SELF_SERVE = "TIER_3_SELF_SERVE"     # <$10k budget, early stage, template fit
    DISQUALIFIED = "DISQUALIFIED"               # Out of scope (e.g. consumer support, crypto shilling, unrelated requests)
    SUSPECTED_SPAM = "SUSPECTED_SPAM"           # Bot submissions, prompt injection attempts, SEO link spam


class LeadInput(BaseModel):
    """Raw inbound submission from website form (e.g., Tally, Typeform, Webflow)."""
    name: str = Field(..., min_length=1, description="Prospect full name")
    email: str = Field(..., description="Prospect email address")
    company: Optional[str] = Field(default="", description="Prospect company name")
    inquiry: str = Field(..., min_length=1, description="Description of the business problem or request")
    estimated_budget: Optional[str] = Field(default="Unspecified", description="Budget tier or amount mentioned")
    source: Optional[str] = Field(default="website_contact_form", description="Originating channel")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean = v.strip().lower()
        if "@" not in clean or "." not in clean.split("@")[-1]:
            raise ValueError(f"Invalid email format: {v}")
        return clean

    @field_validator("estimated_budget", mode="before")
    @classmethod
    def coerce_budget_to_str(cls, v: Any) -> str:
        if v is None:
            return "Unspecified"
        return str(v)


class EnrichedContext(BaseModel):
    """Enriched domain intelligence derived from the prospect's company & email."""
    domain: str = Field(..., description="Extracted company domain")
    is_corporate_email: bool = Field(..., description="True if not from public/free email provider")
    clean_company_name: str = Field(..., description="Normalized company name")
    inferred_industry: str = Field(default="B2B Technology / Services", description="Industry classification")
    estimated_team_size: str = Field(default="50-300 employees", description="Estimated headcount range")


class CaseStudyProof(BaseModel):
    """Verified case study or portfolio metric retrieved from the internal knowledge base."""
    client_name: str = Field(..., description="Client name or anonymized reference")
    industry: str = Field(..., description="Relevant domain or industry")
    operational_pain_solved: str = Field(..., description="Specific workflow problem resolved")
    quantified_result: str = Field(..., description="Measurable metric achieved (e.g., '14 hrs/week saved')")
    case_study_url: str = Field(..., description="Link to the published workflow article or case study")


class ICPEvaluation(BaseModel):
    """Structured AI evaluation produced by frontier reasoning model."""
    deal_tier: DealTier = Field(..., description="Classified prospect tier")
    qualification_score: int = Field(..., ge=0, le=100, description="Overall ICP fit score (0-100)")
    urgency_score: int = Field(..., ge=0, le=10, description="Purchase or implementation urgency (1-10)")
    identified_operational_pain: str = Field(..., description="Core operational friction identified")
    recommended_solution_workflow: str = Field(..., description="Specific custom AI workflow proposed")
    risk_flags: List[str] = Field(default_factory=list, description="Any detected risks or constraints")
    reasoning_summary: str = Field(..., description="High-density justification of tier and score")


class DraftResponse(BaseModel):
    """Context-grounded personalized response generated for operator approval."""
    recipient_name: str
    recipient_email: str
    subject_line: str
    email_body_markdown: str
    suggested_agenda: List[str]
    call_to_action_url: str


class OperatorCard(BaseModel):
    """Structured payload formatted for one-click operator triage via Telegram/Slack."""
    header: str
    qualification_badge: str
    company_intel: str
    pain_summary: str
    matched_proof_point: str
    draft_preview: str
    action_buttons: List[str]
    raw_markdown: str


class WorkflowResult(BaseModel):
    """End-to-end execution summary and audit log."""
    model_config = ConfigDict(protected_namespaces=())

    idempotency_key: str
    success: bool
    lead_input: LeadInput
    enriched_context: Optional[EnrichedContext] = None
    evaluation: Optional[ICPEvaluation] = None
    matched_case_study: Optional[CaseStudyProof] = None
    draft_response: Optional[DraftResponse] = None
    operator_card: Optional[OperatorCard] = None
    execution_time_ms: float
    model_used: str
    token_usage: Dict[str, int] = Field(default_factory=dict)
    error_message: Optional[str] = None
