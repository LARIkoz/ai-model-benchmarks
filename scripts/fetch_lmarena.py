#!/usr/bin/env python3
"""
Fetches LM Arena ELO ratings and updates models with lmarena scores.

LM Arena publishes leaderboard data via their HuggingFace space.
This script fetches the latest ELO ratings and compares against our data.

Usage:
    python scripts/fetch_lmarena.py
    python scripts/fetch_lmarena.py --dry-run
"""

import json
import sys
import argparse
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
MODELS_FILE = REPO_ROOT / "data" / "models.json"

# LM Arena publishes data via HuggingFace datasets API
# The leaderboard table data is fetched from their Gradio space
ARENA_API = "https://lmarena.ai/api/v1/leaderboard"
# Fallback: HuggingFace spaces API
ARENA_HF_SPACE = "https://lmsys-lmarena-ai-main.hf.space/api/leaderboard"


def fetch_arena_data() -> list[dict] | None:
    """Try multiple endpoints to get arena leaderboard data."""
    endpoints = [
        ARENA_API,
        ARENA_HF_SPACE,
        "https://lmarena.ai/leaderboard/data",
    ]

    for url in endpoints:
        try:
            resp = requests.get(url, timeout=30, headers={"Accept": "application/json"})
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"Fetched {len(data)} entries from {url}")
                    return data
                elif isinstance(data, dict):
                    # Some endpoints wrap in a dict
                    for key in ("data", "leaderboard", "results", "rows"):
                        if key in data and isinstance(data[key], list):
                            print(
                                f"Fetched {len(data[key])} entries from {url} (key={key})"
                            )
                            return data[key]
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"  {url}: {e}")
            continue

    print("WARNING: Could not fetch LM Arena data from any endpoint.")
    print("This is expected — LM Arena doesn't have a stable public API.")
    print("Scores must be updated manually from https://lmarena.ai/leaderboard")
    return None


def build_name_map(our_models: list[dict]) -> dict[str, dict]:
    """Build map of lowercase model name -> our model for fuzzy matching."""
    name_map = {}
    for m in our_models:
        # Map by various name forms
        name_map[m["name"].lower()] = m
        name_map[m["id"].lower()] = m
    return name_map


def main():
    parser = argparse.ArgumentParser(description="Fetch LM Arena ELO ratings")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    today = date.today().isoformat()

    arena_data = fetch_arena_data()
    if not arena_data:
        print("\nNo data fetched. Manual update required.")
        print("Visit: https://lmarena.ai/leaderboard")
        sys.exit(0)  # Not an error — just no API available

    our_models = json.loads(MODELS_FILE.read_text())
    name_map = build_name_map(our_models)

    updates = 0
    for entry in arena_data:
        # Arena entries vary in format, try common keys
        name = entry.get("model") or entry.get("name") or entry.get("Model") or ""
        elo = entry.get("elo") or entry.get("rating") or entry.get("ELO")

        if not name or not elo:
            continue

        # Try to match to our model
        model = name_map.get(name.lower())
        if not model:
            continue

        current = model.get("scores", {}).get("lmarena", {}).get("value")
        if current != elo:
            print(f"  {model['name']}: {current} -> {elo}")
            if not args.dry_run:
                if "scores" not in model:
                    model["scores"] = {}
                model["scores"]["lmarena"] = {
                    "value": elo,
                    "measured": today[:7],  # YYYY-MM
                    "source": "https://lmarena.ai/leaderboard",
                }
            updates += 1

    print(f"\nUpdates: {updates}")

    if not args.dry_run and updates > 0:
        MODELS_FILE.write_text(json.dumps(our_models, indent=2))
        print(f"Saved: {MODELS_FILE}")

    print(f"Done. {today}")


if __name__ == "__main__":
    main()
