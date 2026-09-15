"""
Operator Notifier: Formats and dispatches atomic Operator Action Cards
for human-in-the-loop review via Telegram, Slack, or local terminal.
"""

import logging
from typing import Optional
import requests

try:
    from .config import config
    from .schemas import (
        LeadInput, EnrichedContext, ICPEvaluation,
        DraftResponse, CaseStudyProof, OperatorCard, DealTier
    )
except ImportError:
    from config import config
    from schemas import (
        LeadInput, EnrichedContext, ICPEvaluation,
        DraftResponse, CaseStudyProof, OperatorCard, DealTier
    )

logger = logging.getLogger("Workflow.OperatorNotifier")


class OperatorCardFormatter:
    """Creates a high-density, structured review card for founders and operators."""

    BADGE_ICONS = {
        DealTier.TIER_1_ENTERPRISE: "🟢 TIER 1 ENTERPRISE (HIGH PRIORITY)",
        DealTier.TIER_2_MIDMARKET: "🟡 TIER 2 MID-MARKET (QUALIFIED)",
        DealTier.TIER_3_SELF_SERVE: "⚪ TIER 3 SELF-SERVE / TEMPLATE",
        DealTier.DISQUALIFIED: "🔴 DISQUALIFIED (OUT OF SCOPE)",
        DealTier.SUSPECTED_SPAM: "⚠️ SUSPECTED SPAM / BOT"
    }

    @classmethod
    def build_card(
        cls,
        lead: LeadInput,
        enriched: EnrichedContext,
        eval_res: ICPEvaluation,
        draft: DraftResponse,
        proof: CaseStudyProof
    ) -> OperatorCard:
        badge = cls.BADGE_ICONS.get(eval_res.deal_tier, "🔵 INBOUND INQUIRY")
        header = f"🚨 *NEW INBOUND DEAL TRIAGE* | Score: *{eval_res.qualification_score}/100* (Urgency: *{eval_res.urgency_score}/10*)"

        company_intel = (
            f"👤 *Prospect*: {lead.name} (`{lead.email}`)\n"
            f"🏢 *Company*: {enriched.clean_company_name} ({enriched.inferred_industry})\n"
            f"🌐 *Domain*: `{enriched.domain}` (Corporate: {'Yes' if enriched.is_corporate_email else 'No'})\n"
            f"👥 *Est. Size*: {enriched.estimated_team_size}\n"
            f"💰 *Budget*: {lead.estimated_budget}"
        )

        pain_summary = (
            f"🎯 *Identified Pain*: {eval_res.identified_operational_pain}\n"
            f"💡 *Recommended Workflow*: {eval_res.recommended_solution_workflow}"
        )
        if eval_res.risk_flags:
            pain_summary += f"\n⚠️ *Risk Flags*: {', '.join(eval_res.risk_flags)}"

        matched_proof = (
            f"🏆 *Matched Benchmark*: {proof.client_name}\n"
            f"📊 *Result*: {proof.quantified_result}\n"
            f"🔗 *Article*: {proof.case_study_url}"
        )

        draft_preview = (
            f"✉️ *Subject*: {draft.subject_line}\n"
            f"---\n"
            f"{draft.email_body_markdown}\n"
            f"---\n"
            f"📅 *Proposed Agenda*:\n" + "\n".join(f"  {a}" for a in draft.suggested_agenda)
        )

        actions = [
            "✅ [Approve & Send]",
            "✏️ [Edit Draft]",
            "❌ [Disqualify & Archive]"
        ]

        raw_md = (
            f"{header}\n\n"
            f"{badge}\n\n"
            f"{company_intel}\n\n"
            f"{pain_summary}\n\n"
            f"{matched_proof}\n\n"
            f"📝 *PREPARED RESPONSE DRAFT*:\n{draft_preview}\n\n"
            f"⚡ *ACTIONS*: {' | '.join(actions)}"
        )

        return OperatorCard(
            header=header,
            qualification_badge=badge,
            company_intel=company_intel,
            pain_summary=pain_summary,
            matched_proof_point=matched_proof,
            draft_preview=draft_preview,
            action_buttons=actions,
            raw_markdown=raw_md
        )

    @classmethod
    def dispatch(cls, card: OperatorCard) -> bool:
        """Dispatches operator card to configured webhook or logs to stdout."""
        dispatched = False

        # Telegram webhook integration
        if config.telegram_bot_token and config.telegram_chat_id:
            try:
                url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
                payload = {
                    "chat_id": config.telegram_chat_id,
                    "text": card.raw_markdown,
                    "parse_mode": "Markdown"
                }
                resp = requests.post(url, json=payload, timeout=5)
                if resp.status_code == 200:
                    logger.info("Successfully dispatched Operator Card to Telegram.")
                    dispatched = True
                else:
                    logger.warning(f"Telegram dispatch failed: {resp.status_code} - {resp.text}")
            except Exception as exc:
                logger.error(f"Error dispatching to Telegram: {exc}")

        # Slack webhook fallback
        if config.slack_webhook_url and not dispatched:
            try:
                payload = {"text": card.raw_markdown}
                resp = requests.post(config.slack_webhook_url, json=payload, timeout=5)
                if resp.status_code == 200:
                    logger.info("Successfully dispatched Operator Card to Slack.")
                    dispatched = True
            except Exception as exc:
                logger.error(f"Error dispatching to Slack: {exc}")

        return dispatched
