"""
Knowledge Base Module: Internal library of verified operational workflows,
published case studies, and client proof points aligned with Crework Labs' ICP.
"""

from typing import List

try:
    from .schemas import CaseStudyProof
except ImportError:
    from schemas import CaseStudyProof

# Verified operational workflow portfolio (mirroring Crework's publication standards)
CASE_STUDIES: List[CaseStudyProof] = [
    CaseStudyProof(
        client_name="Apex Logistics & Freight (Chicago, IL)",
        industry="Logistics & Supply Chain",
        operational_pain_solved="Inbound quote requests and form submissions sitting for 6+ hours while dispatchers manually calculated lane rates.",
        quantified_result="Turnaround dropped from 6 hours to 45 seconds; win rate on warm inbound quotes increased by 38%.",
        case_study_url="https://shikshita.substack.com/p/how-to-stop-losing-warm-leads-to"
    ),
    CaseStudyProof(
        client_name="Nexus Digital Group (Dubai / NYC)",
        industry="Digital & Growth Agency",
        operational_pain_solved="Client onboarding required manual coordination across 5 SaaS tools, causing 4-day delays before kickoff.",
        quantified_result="Onboarding cycle compressed from 4 days to 3 minutes; zero forgotten onboarding checklist items across 40+ client accounts.",
        case_study_url="https://shikshita.substack.com/p/i-automated-everything-that-happens"
    ),
    CaseStudyProof(
        client_name="Vanguard Wealth Partners (Toronto, ON)",
        industry="Financial Services / FinTech",
        operational_pain_solved="Founders and partners spending 90 minutes every morning manually sifting through 100+ emails and back-to-back calendar invites.",
        quantified_result="Saved 8.5 partner hours weekly with zero missed high-priority client escalations.",
        case_study_url="https://shikshita.substack.com/p/i-wake-up-to-a-full-executive-briefing"
    ),
    CaseStudyProof(
        client_name="CloudScale Systems (Austin, TX)",
        industry="B2B SaaS / Software",
        operational_pain_solved="Sales and client discovery call transcripts sat in Gong/Zoom without written action items, causing deal momentum to stall.",
        quantified_result="Generated structured deal summaries in Notion within 60 seconds post-call; accelerated deal cycle by 11 days.",
        case_study_url="https://shikshita.substack.com/p/i-stopped-paying-for-a-note-taker"
    ),
    CaseStudyProof(
        client_name="Sterling Health Advisory (Boston, MA)",
        industry="Healthcare / MedTech",
        operational_pain_solved="Website visitors bouncing without converting due to static contact forms.",
        quantified_result="Captured and segmented 214 high-intent MQLs in 30 days with a 31% form completion rate.",
        case_study_url="https://shikshita.substack.com/p/turn-website-visitors-into-leads"
    )
]


class KnowledgeBaseMatcher:
    """Retrieves the most semantically and operationally relevant proof point for a lead."""

    @classmethod
    def find_best_proof(cls, industry: str, inquiry: str) -> CaseStudyProof:
        inquiry_lower = inquiry.lower()

        # Score each case study based on keyword overlap and industry alignment
        best_match = CASE_STUDIES[0]
        highest_score = -1

        for study in CASE_STUDIES:
            score = 0
            # Industry match bonus
            if study.industry.lower() in industry.lower() or industry.lower() in study.industry.lower():
                score += 5

            # Operational pain match keywords
            keywords = [
                ("lead", 3), ("reply", 3), ("form", 3), ("sales", 2),
                ("onboard", 4), ("client", 2), ("sheet", 2),
                ("inbox", 4), ("calendar", 4), ("briefing", 4), ("morning", 3),
                ("meeting", 4), ("note", 3), ("transcript", 4), ("summary", 3),
                ("quiz", 4), ("capture", 3), ("visitor", 3)
            ]
            for kw, weight in keywords:
                if kw in inquiry_lower and kw in study.operational_pain_solved.lower():
                    score += weight

            if score > highest_score:
                highest_score = score
                best_match = study

        return best_match
