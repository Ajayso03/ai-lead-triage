"""
Interactive CLI Runner: Demonstrates the live execution of the Inbound Deal Triage Workflow.
Uses 'rich' library for formatted terminal rendering with cross-platform encoding safety.
"""

import sys
import json

# Ensure UTF-8 output encoding across Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from workflow import InboundTriageWorkflow

console = Console(force_terminal=True)

SAMPLE_LEADS = [
    {
        "name": "Sarah Jenkins",
        "email": "sarah.jenkins@meridianlogistics.com",
        "company": "Meridian Logistics Group",
        "inquiry": "We run a 140-person regional freight brokerage in Dallas. Every morning our 15 dispatchers spend 3-4 hours manually re-keying quote requests from email into our TMS. Leads are going cold because competitors reply in under 10 minutes while we take half a day. We need an AI workflow that parses inbound quote emails, checks lane rates, and drafts the reply for dispatcher approval. Budget is around $35,000 for implementation.",
        "estimated_budget": "$35,000 implementation + recurring",
        "source": "tally_website_form"
    },
    {
        "name": "Tariq Al-Mansoor",
        "email": "tariq@crescentmedia.ae",
        "company": "Crescent Media Group",
        "inquiry": "Our digital agency in Dubai has 65 team members managing 40+ active retainers. Client onboarding currently requires our account managers to remember to send 5 separate setup emails, create Slack channels, and populate Notion boards manually. Things slip through the cracks every month. Can you build an automated onboarding sequence triggered from our Airtable?",
        "estimated_budget": "$20,000",
        "source": "tally_website_form"
    }
]


def run_demo():
    console.print()
    console.print(Panel.fit(
        "[bold cyan]CREWORK LABS[/bold cyan] | [bold green]Autonomous Inbound Deal Triage & Operator Workflow[/bold green]\n"
        "[italic white]Demonstrating Frontier OpenAI Responses API Primitive & Human-in-the-Loop Operator Cards[/italic white]",
        border_style="cyan"
    ))
    console.print()

    workflow = InboundTriageWorkflow()

    for idx, lead_data in enumerate(SAMPLE_LEADS, start=1):
        console.rule(f"[bold yellow]Test Case {idx}: Inbound Submission from {lead_data['name']} ({lead_data['company']})[/bold yellow]")

        # 1. Incoming Event
        console.print("\n[bold magenta]1. [TRIGGER] Inbound Webhook Payload Received:[/bold magenta]")
        console.print(Syntax(json.dumps(lead_data, indent=2), "json", theme="monokai", line_numbers=True))

        # 2. Execution
        console.print("\n[bold cyan]2. [PROCESSING] Executing Pipeline (Enrichment -> AI Reasoning -> Knowledge Matching -> Action Card)...[/bold cyan]")
        result = workflow.execute(lead_data)

        # 3. Telemetry Table
        stats_table = Table(title="Workflow Telemetry & Performance", border_style="blue")
        stats_table.add_column("Metric", style="bold white")
        stats_table.add_column("Value", style="green")

        stats_table.add_row("Execution Latency", f"{result.execution_time_ms:.2f} ms")
        stats_table.add_row("Execution Status", "[bold green]SUCCESS (HTTP 200)[/bold green]" if result.success else "[bold red]FAILED[/bold red]")
        stats_table.add_row("Idempotency Hash", result.idempotency_key)
        stats_table.add_row("Model Primitive", result.model_used)
        stats_table.add_row("Deal Tier", result.evaluation.deal_tier.value if result.evaluation else "N/A")
        stats_table.add_row("ICP Qualification Score", f"{result.evaluation.qualification_score}/100" if result.evaluation else "N/A")
        stats_table.add_row("Implementation Urgency", f"{result.evaluation.urgency_score}/10" if result.evaluation else "N/A")
        console.print(stats_table)

        # 4. Operator Action Card (Telegram / Slack representation)
        if result.operator_card:
            console.print("\n[bold green]3. [OUTPUT] Dispatched Mobile Operator Action Card (Telegram / Slack):[/bold green]")
            card_panel = Panel(
                result.operator_card.raw_markdown,
                title="[bold yellow]OPERATOR MOBILE LOCK-SCREEN NOTIFICATION[/bold yellow]",
                border_style="green",
                padding=(1, 2)
            )
            console.print(card_panel)

        console.print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    run_demo()
