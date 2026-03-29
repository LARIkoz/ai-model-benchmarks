#!/usr/bin/env python3
"""
Fetches SWE-Bench Verified/Pro scores from Scale AI SEAL leaderboard.

Scale doesn't have a public JSON API, so this script:
1. Tries known data endpoints
2. Falls back to GitHub-hosted results
3. Reports what needs manual update

Usage:
    python scripts/fetch_swebench.py
    python scripts/fetch_swebench.py --dry-run
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

# Known data sources
SOURCES = [
    # SWE-bench experiments repo (has result JSONs)
    "https://api.github.com/repos/SWE-bench/experiments/contents/evaluation/verified/results",
    # Scale AI SEAL (no public API, but worth checking)
    "https://scale.com/leaderboard/data",
]


def fetch_swebench_github() -> dict | None:
    """Try to fetch SWE-bench results from their GitHub experiments repo."""
    try:
        resp = requests.get(SOURCES[0], timeout=30)
        if resp.status_code != 200:
            return None
        entries = resp.json()
        # Each directory is a model result
        results = {}
        for entry in entries:
            if entry["type"] == "dir":
                # Try to fetch the result JSON
                result_url = f"https://raw.githubusercontent.com/SWE-bench/experiments/main/evaluation/verified/results/{entry['name']}/results.json"
                try:
                    r = requests.get(result_url, timeout=10)
                    if r.status_code == 200:
                        data = r.json()
                        resolved = data.get("resolved", 0)
                        total = data.get("total", 500)
                        pct = round(resolved / total * 100, 1) if total else 0
                        results[entry["name"]] = {
                            "resolved": resolved,
                            "total": total,
                            "pct": pct,
                        }
                except Exception:
                    pass
        if results:
            print(f"Fetched {len(results)} SWE-bench results from GitHub")
            return results
    except Exception as e:
        print(f"GitHub fetch failed: {e}")
    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch SWE-Bench scores")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    today = date.today().isoformat()

    results = fetch_swebench_github()
    if not results:
        print("Could not fetch SWE-bench results automatically.")
        print("Manual update required from: https://scale.com/leaderboard")
        print("Or: https://www.swebench.com")
        sys.exit(0)

    our_models = json.loads(MODELS_FILE.read_text())

    # Build name matching (SWE-bench uses model names like "claude-3.5-sonnet")
    updates = 0
    for model_name, data in results.items():
        for m in our_models:
            # Fuzzy match: check if SWE-bench model name matches our model
            if (
                model_name.lower() in m["id"].lower()
                or m["id"].lower() in model_name.lower()
            ):
                current = m.get("scores", {}).get("swe_v", {}).get("value")
                if current != data["pct"]:
                    print(
                        f"  {m['name']}: swe_v {current} -> {data['pct']}% ({data['resolved']}/{data['total']})"
                    )
                    if not args.dry_run:
                        if "scores" not in m:
                            m["scores"] = {}
                        m["scores"]["swe_v"] = {
                            "value": data["pct"],
                            "measured": today[:7],
                            "source": "https://scale.com/leaderboard",
                        }
                    updates += 1
                break

    print(f"\nUpdates: {updates}")

    if not args.dry_run and updates > 0:
        MODELS_FILE.write_text(json.dumps(our_models, indent=2))
        print(f"Saved: {MODELS_FILE}")

    print(f"Done. {today}")


if __name__ == "__main__":
    main()
