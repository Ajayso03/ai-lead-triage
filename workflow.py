"""
Pipeline Orchestrator: Executes the end-to-end inbound deal triage workflow
with idempotency caching, sub-second telemetry, and full error isolation.
"""

import time
import hashlib
import logging
from typing import Dict, Any, Optional

try:
    from .schemas import LeadInput, WorkflowResult
    from .enrichment import DomainEnricher
    from .knowledge_base import KnowledgeBaseMatcher
    from .ai_reasoning import AIReasoningEngine
    from .operator_notifier import OperatorCardFormatter
except ImportError:
    from schemas import LeadInput, WorkflowResult
    from enrichment import DomainEnricher
    from knowledge_base import KnowledgeBaseMatcher
    from ai_reasoning import AIReasoningEngine
    from operator_notifier import OperatorCardFormatter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Workflow.Pipeline")


class InboundTriageWorkflow:
    """Production workflow engine processing inbound website leads."""

    def __init__(self):
        self._processed_hashes: set = set()

    def generate_idempotency_key(self, lead: LeadInput) -> str:
        """Computes a deterministic hash of core lead attributes to prevent duplicate alerts."""
        raw_key = f"{lead.email.lower().strip()}_{lead.inquiry.strip()[:100]}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def execute(self, lead_data: Dict[str, Any]) -> WorkflowResult:
        """Executes the 5-stage automated pipeline."""
        start_time = time.perf_counter()

        # Step 1: Input Validation
        try:
            lead = LeadInput(**lead_data)
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"Input validation failed: {exc}")
            # Construct a safe dummy lead for the result object
            dummy_lead = LeadInput(
                name=str(lead_data.get("name", "Invalid")),
                email=str(lead_data.get("email", "invalid@format.com")),
                inquiry=str(lead_data.get("inquiry", "Invalid payload"))
            ) if "@" in str(lead_data.get("email", "")) else LeadInput(
                name="Invalid", email="invalid@format.com", inquiry="Invalid payload"
            )
            return WorkflowResult(
                idempotency_key="error_validation_failed",
                success=False,
                lead_input=dummy_lead,
                execution_time_ms=elapsed_ms,
                model_used="none",
                error_message=f"Validation Error: {exc}"
            )

        # Step 2: Idempotency Verification
        idempotency_key = self.generate_idempotency_key(lead)
        if idempotency_key in self._processed_hashes:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.warning(f"Duplicate event detected for key {idempotency_key}. Suppressing downstream alerts.")
            return WorkflowResult(
                idempotency_key=idempotency_key,
                success=True,
                lead_input=lead,
                execution_time_ms=elapsed_ms,
                model_used="cache_dedup",
                error_message="DUPLICATE_EVENT_DETECTED: Alert suppressed by idempotency filter."
            )

        self._processed_hashes.add(idempotency_key)

        try:
            # Step 3: Domain & Company Enrichment
            enriched = DomainEnricher.enrich(lead)
            logger.info(f"Enriched domain intelligence for '{enriched.clean_company_name}' ({enriched.domain})")

            # Step 4: Knowledge Base Case Study Grounding
            matched_proof = KnowledgeBaseMatcher.find_best_proof(
                industry=enriched.inferred_industry,
                inquiry=lead.inquiry
            )
            logger.info(f"Matched proof point: {matched_proof.client_name}")

            # Step 5: Frontier AI Reasoning & Structured Evaluation
            evaluation, draft, model_used, tokens = AIReasoningEngine.evaluate_and_draft(
                lead=lead,
                enriched=enriched,
                proof=matched_proof
            )
            logger.info(f"Assigned {evaluation.deal_tier.value} (Score: {evaluation.qualification_score}/100)")

            # Step 6: Operator Card Construction & Webhook Dispatch
            operator_card = OperatorCardFormatter.build_card(
                lead=lead,
                enriched=enriched,
                eval_res=evaluation,
                draft=draft,
                proof=matched_proof
            )
            OperatorCardFormatter.dispatch(operator_card)

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"Pipeline executed successfully in {elapsed_ms:.2f}ms")

            return WorkflowResult(
                idempotency_key=idempotency_key,
                success=True,
                lead_input=lead,
                enriched_context=enriched,
                evaluation=evaluation,
                matched_case_study=matched_proof,
                draft_response=draft,
                operator_card=operator_card,
                execution_time_ms=elapsed_ms,
                model_used=model_used,
                token_usage=tokens
            )

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.exception(f"Unhandled pipeline execution error: {exc}")
            return WorkflowResult(
                idempotency_key=idempotency_key,
                success=False,
                lead_input=lead,
                execution_time_ms=elapsed_ms,
                model_used="error_handler",
                error_message=str(exc)
            )
