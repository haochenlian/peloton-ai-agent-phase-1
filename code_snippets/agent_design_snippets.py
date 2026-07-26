"""Illustrative Phase 1 code snippets for the Peloton multi-agent design.

This file is not a production Peloton integration. It demonstrates routing,
human-in-the-loop checks, and validation of the synthetic course datasets.
"""

from __future__ import annotations

import csv
from pathlib import Path


AGENT_KEYWORDS = {
    "Business/Marketing": {
        "campaign",
        "conversion",
        "customer segment",
        "marketing",
        "promotion",
    },
    "Data Science": {
        "cadence",
        "class trend",
        "data quality",
        "output",
        "workout",
    },
    "Membership/Fraud Detection": {
        "account",
        "fraud",
        "login",
        "membership",
        "unauthorized",
    },
    "Order/Shipping": {
        "delivery",
        "order",
        "refund",
        "shipping",
        "tracking",
    },
    "Product Recommendation": {
        "accessory",
        "apparel",
        "equipment",
        "recommend",
        "replacement",
    },
}

HIGH_RISK_TERMS = {
    "automatically approve",
    "diagnose",
    "disable account",
    "ignore consent",
    "medical condition",
    "publish directly",
    "refund automatically",
}


def route_request(user_input: str) -> str:
    """Return the most likely specialist agent for a user request."""
    normalized = user_input.lower()
    scores = {
        agent: sum(keyword in normalized for keyword in keywords)
        for agent, keywords in AGENT_KEYWORDS.items()
    }
    best_agent = max(scores, key=scores.get)
    return best_agent if scores[best_agent] > 0 else "Human-in-the-Loop Review"


def requires_human_review(user_input: str, risk_level: str = "Low") -> bool:
    """Flag high-impact or sensitive requests for human review."""
    normalized = user_input.lower()
    return risk_level.lower() == "high" or any(
        term in normalized for term in HIGH_RISK_TERMS
    )


def validate_dataset(csv_path: str | Path) -> dict[str, int]:
    """Validate record count and coverage in one synthetic dataset."""
    path = Path(csv_path)
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))

    required_columns = {
        "record_id",
        "split",
        "ai_agent",
        "user_story_use_case",
        "user_input",
        "expected_route",
        "expected_action",
        "human_review_required",
        "expected_response_elements",
        "risk_level",
        "data_origin",
    }
    if not rows:
        raise ValueError(f"{path.name} contains no records.")
    missing = required_columns.difference(rows[0])
    if missing:
        raise ValueError(f"{path.name} is missing columns: {sorted(missing)}")

    agents = {row["ai_agent"] for row in rows}
    use_cases = {
        (row["ai_agent"], row["user_story_use_case"])
        for row in rows
    }
    if len(agents) != 5:
        raise ValueError(f"Expected 5 agents; found {len(agents)}.")
    if len(use_cases) != 15:
        raise ValueError(f"Expected 15 user stories; found {len(use_cases)}.")

    return {
        "records": len(rows),
        "agents": len(agents),
        "user_stories": len(use_cases),
    }


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    data_directory = project_root / "training_testing_data"

    for filename in (
        "peloton_ai_training_data.csv",
        "peloton_ai_testing_data.csv",
    ):
        result = validate_dataset(data_directory / filename)
        print(f"{filename}: {result}")

