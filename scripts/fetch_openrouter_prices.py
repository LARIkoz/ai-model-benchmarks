#!/usr/bin/env python3
"""
Fetches current model pricing from OpenRouter API and updates data/pricing.json.
Reports new models and price changes.

Usage:
    python scripts/fetch_openrouter_prices.py
    python scripts/fetch_openrouter_prices.py --dry-run
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
PRICING_FILE = REPO_ROOT / "data" / "pricing.json"
MODELS_FILE = REPO_ROOT / "data" / "models.json"
OPENROUTER_API = "https://openrouter.ai/api/v1/models"


def fetch_openrouter_models() -> list[dict]:
    """Fetch all models from OpenRouter API."""
    try:
        resp = requests.get(OPENROUTER_API, timeout=30)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch OpenRouter models: {e}")
        sys.exit(1)


def load_json(path: Path) -> dict | list:
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data: dict | list):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {path}")


def extract_pricing(or_model: dict) -> dict | None:
    """Extract pricing info from OpenRouter model object."""
    pricing = or_model.get("pricing", {})
    prompt = pricing.get("prompt")
    completion = pricing.get("completion")

    if prompt is None or completion is None:
        return None

    # OpenRouter returns per-token strings, convert to per-million
    try:
        input_per_m = float(prompt) * 1_000_000
        output_per_m = float(completion) * 1_000_000
    except (ValueError, TypeError):
        return None

    return {
        "input": round(input_per_m, 4),
        "output": round(output_per_m, 4),
    }


def build_or_price_map(or_models: list[dict]) -> dict[str, dict]:
    """Build map of openrouter_id -> pricing."""
    price_map = {}
    for m in or_models:
        model_id = m.get("id")
        if not model_id:
            continue
        pricing = extract_pricing(m)
        if pricing:
            price_map[model_id] = pricing
    return price_map


def check_model_prices(
    our_models: list[dict], or_price_map: dict[str, dict]
) -> tuple[list, list]:
    """
    Compare our tracked models against OpenRouter prices.
    Returns (price_changes, new_or_models_not_tracked).
    """
    price_changes = []

    our_or_ids = set()
    for model in our_models:
        or_id = model.get("openrouter_id")
        if not or_id:
            continue
        our_or_ids.add(or_id)

        or_pricing = or_price_map.get(or_id)
        if not or_pricing:
            continue

        our_pricing = model.get("pricing", {})
        our_input = our_pricing.get("input")
        our_output = our_pricing.get("output")

        or_input = or_pricing["input"]
        or_output = or_pricing["output"]

        if our_input is None or our_output is None:
            continue

        # Allow 1% tolerance for float comparison
        input_changed = abs(float(our_input) - or_input) / max(or_input, 0.001) > 0.01
        output_changed = (
            abs(float(our_output) - or_output) / max(or_output, 0.001) > 0.01
        )

        if input_changed or output_changed:
            price_changes.append(
                {
                    "model_id": model["id"],
                    "openrouter_id": or_id,
                    "name": model["name"],
                    "our_input": our_input,
                    "or_input": or_input,
                    "our_output": our_output,
                    "or_output": or_output,
                }
            )

    # Find models on OpenRouter not in our tracking
    new_models = []
    for or_id, pricing in or_price_map.items():
        if or_id not in our_or_ids and ":free" not in or_id:
            new_models.append({"openrouter_id": or_id, "pricing": pricing})

    return price_changes, new_models


def update_model_prices(
    our_models: list[dict], price_changes: list[dict], today: str
) -> list[dict]:
    """Apply price changes to models list."""
    change_map = {c["model_id"]: c for c in price_changes}

    for model in our_models:
        change = change_map.get(model["id"])
        if change:
            model["pricing"]["input"] = change["or_input"]
            model["pricing"]["output"] = change["or_output"]
            model["pricing"]["updated"] = today

    return our_models


def update_pricing_json(pricing_data: dict, today: str) -> dict:
    """Update the top-level updated date in pricing.json."""
    pricing_data["updated"] = today
    return pricing_data


def main():
    parser = argparse.ArgumentParser(
        description="Fetch OpenRouter prices and update data files"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Report changes without writing files"
    )
    args = parser.parse_args()

    today = date.today().isoformat()

    print(f"Fetching models from OpenRouter API...")
    or_models = fetch_openrouter_models()
    print(f"Fetched {len(or_models)} models from OpenRouter")

    or_price_map = build_or_price_map(or_models)

    our_models = load_json(MODELS_FILE)
    pricing_data = load_json(PRICING_FILE)

    price_changes, new_models = check_model_prices(our_models, or_price_map)

    # Report price changes
    if price_changes:
        print(f"\n--- PRICE CHANGES ({len(price_changes)}) ---")
        for change in price_changes:
            print(
                f"  {change['name']} ({change['openrouter_id']}):\n"
                f"    input:  ${change['our_input']} -> ${change['or_input']}\n"
                f"    output: ${change['our_output']} -> ${change['or_output']}"
            )
    else:
        print("\nNo price changes detected.")

    # Report new models
    if new_models:
        print(f"\n--- NEW MODELS ON OPENROUTER ({len(new_models)}) ---")
        for m in new_models[:20]:
            pricing = m["pricing"]
            print(
                f"  {m['openrouter_id']}: ${pricing['input']}/M in, ${pricing['output']}/M out"
            )
        if len(new_models) > 20:
            print(f"  ... and {len(new_models) - 20} more")
        print("\nACTION REQUIRED: Add new models to data/models.json manually.")
    else:
        print("\nNo new untracked models found.")

    if args.dry_run:
        print("\nDry run — no files written.")
        return

    if price_changes:
        updated_models = update_model_prices(our_models, price_changes, today)
        save_json(MODELS_FILE, updated_models)

    updated_pricing = update_pricing_json(pricing_data, today)
    save_json(PRICING_FILE, updated_pricing)

    if new_models:
        # Write new models to a temp file for manual review
        new_models_file = REPO_ROOT / "data" / "new_models_detected.json"
        save_json(new_models_file, {"detected": today, "models": new_models})
        print(f"\nNew models written to {new_models_file} for manual review.")

    print(f"\nDone. Updated: {today}")

    # Exit code 1 if new models found (triggers GitHub issue creation in CI)
    if new_models:
        sys.exit(1)


if __name__ == "__main__":
    main()
