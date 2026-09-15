"""
Enrichment Module: Extracts company intelligence, domain metadata,
and corporate validity from raw lead submissions.
"""

import re
from typing import Set

try:
    from .schemas import LeadInput, EnrichedContext
except ImportError:
    from schemas import LeadInput, EnrichedContext

# Common free / disposable email domains
PUBLIC_EMAIL_PROVIDERS: Set[str] = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "aol.com", "proton.me", "protonmail.com", "zoho.com", "mail.com",
    "gmx.com", "yandex.com", "fastmail.com", "live.com"
}

# Industry keyword mapping for heuristic grounding
INDUSTRY_PATTERNS = {
    "Healthcare / MedTech": [r"health", r"clinic", r"pharma", r"med", r"care", r"biotech"],
    "Financial Services / FinTech": [r"capital", r"fund", r"invest", r"wealth", r"credit", r"pay", r"bank"],
    "B2B SaaS / Software": [r"software", r"saas", r"cloud", r"app", r"platform", r"dev", r"tech", r"ai"],
    "Digital & Growth Agency": [r"agency", r"marketing", r"media", r"creative", r"studio", r"consulting"],
    "Logistics & Supply Chain": [r"logistics", r"freight", r"supply", r"fleet", r"cargo", r"delivery"],
    "Legal & Professional Services": [r"law", r"legal", r"attorney", r"advisory", r"cpa", r"audit"]
}


class DomainEnricher:
    """Enriches prospect contact submissions with company and domain metadata."""

    @staticmethod
    def extract_domain(email: str) -> str:
        parts = email.strip().lower().split("@")
        return parts[1] if len(parts) == 2 else ""

    @classmethod
    def is_corporate(cls, domain: str) -> bool:
        return domain not in PUBLIC_EMAIL_PROVIDERS and len(domain) > 3

    @classmethod
    def clean_company_name(cls, company_field: str, domain: str) -> str:
        if company_field and company_field.strip():
            # Clean unwanted characters
            cleaned = re.sub(r"[^\w\s\.-]", "", company_field.strip())
            return cleaned.title()

        # Fall back to domain name extraction (e.g. acme-logistics.com -> Acme Logistics)
        domain_stem = domain.split(".")[0]
        words = re.split(r"[-_]", domain_stem)
        return " ".join(words).title()

    @classmethod
    def infer_industry(cls, text_corpus: str) -> str:
        corpus_lower = text_corpus.lower()
        for industry, patterns in INDUSTRY_PATTERNS.items():
            for pattern in patterns:
                if re.search(r"\b" + pattern, corpus_lower):
                    return industry
        return "B2B Professional Services / Technology"

    @classmethod
    def enrich(cls, lead: LeadInput) -> EnrichedContext:
        domain = cls.extract_domain(lead.email)
        is_corp = cls.is_corporate(domain)
        cleaned_company = cls.clean_company_name(lead.company or "", domain)

        # Infer industry from inquiry + company name
        combined_text = f"{lead.company or ''} {lead.inquiry} {domain}"
        industry = cls.infer_industry(combined_text)

        # Estimate team size range (50-300 ICP target calibration)
        team_size = "50–300 employees (Core ICP Target)" if is_corp else "1–10 employees (Early Stage / Freelance)"

        return EnrichedContext(
            domain=domain,
            is_corporate_email=is_corp,
            clean_company_name=cleaned_company,
            inferred_industry=industry,
            estimated_team_size=team_size
        )
