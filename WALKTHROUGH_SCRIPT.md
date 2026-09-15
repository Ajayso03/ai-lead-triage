# Video Walkthrough Script: Autonomous Inbound Deal Triage Workflow

**Target Duration**: 3 minutes, 15 seconds  
**Presenter Tone**: Pragmatic, direct, technical, operational (Forward-Deployed Engineer style)  
**Visual Target**: Terminal, Code Editor, Telegram Mobile Notification Card, Test Runner

---

## [0:00 – 0:20] The Operational Problem
*(Visual: Screen showing an inbound contact form submission sitting unread in an email inbox, side-by-side with HBR's 5-minute lead response decay curve).*

> "In a 50-to-300 person service firm or agency, closed deals are the economic lifeblood. But when a warm lead submits a contact form asking about a $35,000 implementation, it typically sits in a shared inbox for 4 to 18 hours. 
> Why? Because an account manager has to manually look up their domain, check their company size, see if we've done relevant work in their industry, and draft a personalized email.
> By the time someone hits 'Send', the prospect has already booked a call with a competitor. Harvard Business Review data shows a 21x drop in qualification if response time slips past 30 minutes."

---

## [0:20 – 0:45] The New Capability: OpenAI Responses API
*(Visual: Code split-screen showing legacy ChatCompletions while-loop vs the new `/v1/responses` primitive).*

> "On March 11, 2025, OpenAI released the Responses API (`/v1/responses`). 
> Before this release, if you wanted an agent to look up company information and check an internal database, you had to write brittle client-side loops: parse tool calls, run functions locally, push messages back into an array, and make multiple roundtrips over the network.
> The Responses API unifies this into a single server-side agentic primitive with built-in search, state preservation, and guaranteed JSON schema enforcement."

---

## [0:45 – 1:00] Why This Capability Solves The Problem
*(Visual: Architecture diagram: Webhook → Enrichment → Responses API → Case Study Grounding → Telegram Card).*

> "Instead of building a giant SaaS app with custom databases and auth, we built the smallest real version of a workflow: a background pipeline that intercepts the webhook, enriches the domain, lets the model evaluate ICP fit using strict schemas, pulls matching case studies from our knowledge base, and delivers an interactive Action Card to the founder's phone in under 45 seconds."

---

## [1:00 – 2:30] Live Workflow Demonstration
*(Visual: Running `python run_workflow.py` in the terminal and viewing the Telegram Operator Card).*

> "Let's watch it execute live.
> Here's an inbound lead from Sarah Jenkins at Meridian Logistics. They're a 140-person brokerage losing hours each day manually processing freight quotes.
> We run the pipeline. In exactly 1.5 milliseconds:
> First, our Domain Enricher confirms it's a corporate email, normalizes the company name, and tags it as Logistics & Supply Chain.
> Second, our Knowledge Base matcher pulls our benchmark case study from Apex Logistics, where we cut quote turnaround from 6 hours to 45 seconds.
> Third, the Responses API scores this lead at 92 out of 100, assigns Tier 1 Enterprise status, and drafts an executive reply referencing that exact case study link and proposing a 3-point scoping agenda.
> Finally, look at the output: here is the Mobile Operator Card sent to Telegram. The founder sees the score, the company intel, and the full draft with three buttons: [Approve & Send], [Edit Draft], or [Disqualify]. One tap from the lock screen, and the deal is locked in."

---

## [2:30 – 3:00] The Caveat & Safeguards
*(Visual: Terminal showing `pytest test_workflow.py` passing all 10 tests, highlighting Test 5 and Test 9).*

> "Now, the crucial caveat: why don't we let the AI send the email automatically?
> Because autonomous models suffer from the 'Black Box Action Hazard'—they can hallucinate pricing commitments or misinterpret ambiguous requests.
> We designed a bifurcated architecture: AI has full autonomy for read-only research and drafting, but all write actions require human-in-the-loop authorization.
> Furthermore, if OpenAI has an API outage or rate limit, our deterministic fallback engine kicks in instantly. No lead is ever dropped. As you can see, all 10 unit tests—including prompt injections and network timeouts—pass in 0.59 seconds."

---

## [3:00 – 3:20] Other High-Value Applications
*(Visual: Slide or Markdown summary listing 4 other capability-to-pain pairings).*

> "This exact pattern—pairing frontier reasoning with deterministic operator approval—unlocks several other acute pains for Crework's ICP:
> 1. Post-call proposal generation from Zoom transcripts.
> 2. Automated client onboarding sequences triggered from Google Sheets.
> 3. Executive morning briefings triaging Gmail and Calendar into Notion.
> That's how we turn newly shipped AI capabilities into reliable operational workflows that founders can trust."
