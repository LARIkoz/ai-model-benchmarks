#!/usr/bin/env python3
"""
Canary: daily health check for all benchmark and source URLs.

Pings every URL referenced in benchmarks.json and a sample of score sources.
Reports 404s, timeouts, and redirects. Useful for detecting deprecated benchmarks.

Usage:
    python scripts/canary.py
    python scripts/canary.py --full   # Check ALL score source URLs (slow)
"""

import json
import sys
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

REPO_ROOT = Path(__file__).parent.parent
BENCHMARKS_FILE = REPO_ROOT / "data" / "benchmarks.json"
MODELS_FILE = REPO_ROOT / "data" / "models.json"


def check_url(url: str, timeout: int = 10) -> tuple[int, str]:
    """Check URL, return (status_code, status_text)."""
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        return resp.status_code, "OK" if resp.status_code < 400 else "FAIL"
    except requests.Timeout:
        return 0, "TIMEOUT"
    except requests.ConnectionError:
        return 0, "CONN_ERROR"
    except requests.RequestException as e:
        return 0, str(e)[:50]


def main():
    parser = argparse.ArgumentParser(description="Check benchmark and source URLs")
    parser.add_argument(
        "--full", action="store_true", help="Check ALL score source URLs"
    )
    args = parser.parse_args()

    # 1. Check benchmark URLs
    benchmarks = json.loads(BENCHMARKS_FILE.read_text())
    print(f"Checking {len(benchmarks)} benchmark URLs...")
    bench_issues = []
    for b in benchmarks:
        url = b.get("url")
        if not url:
            continue
        status, text = check_url(url)
        icon = "✓" if status < 400 and status > 0 else "✗"
        if status >= 400 or status == 0:
            bench_issues.append(f"  {icon} {b['id']}: {url} → {status} {text}")
            print(f"  {icon} {b['id']}: {status} {text}")
        else:
            print(f"  {icon} {b['id']}: {status}")

    # 2. Check score source URLs (sample or full)
    models = json.loads(MODELS_FILE.read_text())
    urls_to_check = set()
    for m in models:
        for bench_id, score in m.get("scores", {}).items():
            if isinstance(score, dict) and score.get("source"):
                urls_to_check.add(score["source"])

    if not args.full:
        # Sample: unique URLs only (many models share same source)
        print(f"\nChecking {len(urls_to_check)} unique source URLs...")
    else:
        print(f"\nFull check: {len(urls_to_check)} unique source URLs...")

    source_issues = []
    for url in sorted(urls_to_check):
        status, text = check_url(url)
        if status >= 400 or status == 0:
            source_issues.append(f"  ✗ {url} → {status} {text}")
            print(f"  ✗ {url} → {status} {text}")

    # Summary
    print(f"\n--- SUMMARY ---")
    print(f"Benchmarks: {len(benchmarks)} checked, {len(bench_issues)} issues")
    print(f"Sources: {len(urls_to_check)} checked, {len(source_issues)} issues")

    if bench_issues or source_issues:
        print(f"\n--- ISSUES ---")
        for issue in bench_issues + source_issues:
            print(issue)
        sys.exit(1)
    else:
        print("All URLs healthy.")


if __name__ == "__main__":
    main()
