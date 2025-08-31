# backend/generator/ai/niches.py
from typing import Dict, List

NICHES: Dict[str, Dict[str, List[str] | str]] = {
    "general": {
        "context": "Broad B2B/B2C operations and client comms.",
        "goals": ["clarity", "actionability", "professional tone"],
        "voice": "Clear, concise, no fluff.",
        "do": [
            "Lead with outcome",
            "Give numbered, scannable steps",
            "Surface deadlines and owners"
        ],
        "dont": [
            "Jargon without value",
            "Vague CTAs",
            "Overly long paragraphs"
        ],
        "terms": ["deliverable", "deadline", "owner", "status"],
    },
    "freelance": {
        "context": "Solo contractor / small service provider workflow.",
        "goals": ["set expectations", "confirm scope", "ensure payment clarity"],
        "voice": "Warm but direct, boundaries respected.",
        "do": [
            "Confirm requirements and acceptance criteria",
            "Outline timeline & revisions policy",
            "Provide payment method & due date"
        ],
        "dont": [
            "Commit without scope",
            "Ambiguous pricing",
            "Open-ended timelines"
        ],
        "terms": ["scope", "milestone", "deposit", "final delivery", "invoice"],
    },
    "consulting": {
        "context": "Advisory engagements and stakeholder alignment.",
        "goals": ["insight", "structured next steps", "risk visibility"],
        "voice": "Executive concise.",
        "do": [
            "Summarize findings",
            "List recommendations with impact",
            "Call out assumptions/risks"
        ],
        "dont": [
            "Hand-wavy claims",
            "Buried ledes",
            "No owners/dates"
        ],
        "terms": ["recommendation", "impact", "owner", "ETA", "risk"],
    },
    "events": {
        "context": "Event planning, vendors, run-of-show.",
        "goals": ["logistics precision", "timelines", "contingencies"],
        "voice": "Operationally crisp.",
        "do": [
            "Use checklists & timeboxes",
            "Confirm vendors and SLAs",
            "Include contact & contingency"
        ],
        "dont": [
            "Missing run-sheet",
            "Unassigned tasks",
            "No fallback"
        ],
        "terms": ["run-of-show", "SLA", "load-in/out", "POC", "contingency"],
    },
    "coaching": {
        "context": "Client accountability and session planning.",
        "goals": ["clear goals", "manageable actions", "follow-up cadence"],
        "voice": "Supportive, accountable.",
        "do": [
            "Define SMART goals",
            "Assign simple weekly actions",
            "Schedule next check-in"
        ],
        "dont": [
            "Overloading tasks",
            "Vague outcomes",
            "No follow-up"
        ],
        "terms": ["goal", "checkpoint", "reflection", "next step"],
    },
    "design": {
        "context": "Creative briefs, feedback loops, deliverables.",
        "goals": ["requirements clarity", "feedback cycles", "file handoff"],
        "voice": "Creative yet precise.",
        "do": [
            "Capture brand constraints",
            "Define feedback windows",
            "Specify formats and handoff"
        ],
        "dont": [
            "Ambiguous brief",
            "Unlimited revisions",
            "Missing exports"
        ],
        "terms": ["brief", "style guide", "iteration", "export pack", "handoff"],
    },
}

def niche_guide(niche_slug: str | None) -> str | None:
    if not niche_slug:
        return None
    pack = NICHES.get(niche_slug.lower()) or NICHES["general"]
    lines: List[str] = []
    lines.append(f"Context: {pack['context']}")
    lines.append("Goals: " + "; ".join(pack["goals"]))          # type: ignore[index]
    lines.append("Voice: " + str(pack["voice"]))
    lines.append("Do: " + "; ".join(pack["do"]))                 # type: ignore[index]
    lines.append("Don't: " + "; ".join(pack["dont"]))            # type: ignore[index]
    if pack.get("terms"):
        lines.append("Preferred terms: " + ", ".join(pack["terms"]))  # type: ignore[index]
    lines.append("If a detail is unknown, keep it generic and do not invent specifics.")
    return "\n".join(lines)
