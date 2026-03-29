#!/usr/bin/env python3
"""
Validates data files for schema correctness, duplicates, and freshness.

Usage:
    python scripts/validate.py
    python scripts/validate.py --strict   # fail on stale scores
"""

import json
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MODELS_FILE = REPO_ROOT / "data" / "models.json"
EMBEDDINGS_FILE = REPO_ROOT / "data" / "embeddings.json"
BENCHMARKS_FILE = REPO_ROOT / "data" / "benchmarks.json"
ROUTING_FILE = REPO_ROOT / "data" / "routing.json"
PRICING_FILE = REPO_ROOT / "data" / "pricing.json"

REQUIRED_MODEL_FIELDS = {"id", "name", "provider", "tier", "pricing", "context_length"}
REQUIRED_BENCHMARK_FIELDS = {"id", "name", "category", "lifecycle"}
VALID_TIERS = {0, 1, 2, 3}
VALID_LIFECYCLES = {"active", "saturated", "dead", "planned"}

# Benchmark IDs loaded from benchmarks.json for score key validation
KNOWN_BENCHMARK_IDS: set[str] = set()

errors: list[str] = []
warnings: list[str] = []


def error(msg: str):
    errors.append(f"ERROR: {msg}")


def warn(msg: str):
    warnings.append(f"WARN: {msg}")


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        error(f"File not found: {path}")
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        error(f"Invalid JSON in {path}: {e}")
        return None


def validate_benchmarks(benchmarks: list[dict]):
    global KNOWN_BENCHMARK_IDS
    seen_ids = set()

    for b in benchmarks:
        bid = b.get("id", "(no id)")

        for field in REQUIRED_BENCHMARK_FIELDS:
            if field not in b:
                error(f"benchmarks.json: {bid} missing field '{field}'")

        if bid in seen_ids:
            error(f"benchmarks.json: duplicate id '{bid}'")
        seen_ids.add(bid)

        lifecycle = b.get("lifecycle")
        if lifecycle not in VALID_LIFECYCLES:
            error(
                f"benchmarks.json: {bid} invalid lifecycle '{lifecycle}', must be one of {VALID_LIFECYCLES}"
            )

        # URL check for active benchmarks
        url = b.get("url")
        if lifecycle == "active" and not url:
            warn(f"benchmarks.json: {bid} is active but has no URL")
        elif url and not url.startswith("https://"):
            warn(f"benchmarks.json: {bid} url is not https: '{url}'")

    KNOWN_BENCHMARK_IDS = seen_ids
    print(f"  benchmarks.json: {len(benchmarks)} entries, {len(seen_ids)} unique IDs")


def validate_models(models: list[dict], strict: bool):
    seen_ids = set()
    today = datetime.now()
    staleness_thresholds = {"high": 14, "medium": 30, "low": 60}

    # Build volatility map from benchmarks
    volatility_map: dict[str, str] = {}
    benchmarks = load_json(BENCHMARKS_FILE)
    if benchmarks:
        for b in benchmarks:
            volatility_map[b.get("id", "")] = b.get("volatility", "low")

    for model in models:
        mid = model.get("id", "(no id)")

        # Required fields
        for field in REQUIRED_MODEL_FIELDS:
            if field not in model:
                error(f"models.json: {mid} missing field '{field}'")

        # Duplicate check
        if mid in seen_ids:
            error(f"models.json: duplicate id '{mid}'")
        seen_ids.add(mid)

        # Tier validity
        tier = model.get("tier")
        if tier not in VALID_TIERS:
            error(
                f"models.json: {mid} invalid tier '{tier}', must be one of {VALID_TIERS}"
            )

        # Pricing structure
        pricing = model.get("pricing", {})
        if not isinstance(pricing, dict):
            error(f"models.json: {mid} pricing must be an object")
        elif model.get("tier", 0) > 0:
            if "input" not in pricing:
                error(f"models.json: {mid} pricing missing 'input'")
            if "output" not in pricing:
                error(f"models.json: {mid} pricing missing 'output'")

        # Score freshness
        scores = model.get("scores", {})
        for bench_id, score in scores.items():
            if bench_id not in KNOWN_BENCHMARK_IDS and KNOWN_BENCHMARK_IDS:
                warn(f"models.json: {mid} uses unknown benchmark id '{bench_id}'")

            measured = score.get("measured")
            if not measured:
                error(f"models.json: {mid}.{bench_id} missing 'measured' date")
                continue

            try:
                # Support YYYY-MM or YYYY-MM-DD
                if len(measured) == 7:
                    measured_dt = datetime.strptime(measured, "%Y-%m")
                else:
                    measured_dt = datetime.strptime(measured[:10], "%Y-%m-%d")
            except ValueError:
                error(
                    f"models.json: {mid}.{bench_id} invalid measured date '{measured}'"
                )
                continue

            volatility = volatility_map.get(bench_id, "low")
            threshold_days = staleness_thresholds.get(volatility, 60)
            age_days = (today - measured_dt).days

            source = score.get("source")
            if not source:
                warn(f"models.json: {mid}.{bench_id} missing 'source' URL")
            elif not source.startswith("https://"):
                warn(
                    f"models.json: {mid}.{bench_id} source is not an https URL: '{source}'"
                )

            if age_days > threshold_days:
                msg = (
                    f"models.json: {mid}.{bench_id} is {age_days}d old "
                    f"(volatility={volatility}, threshold={threshold_days}d)"
                )
                if strict:
                    error(msg)
                else:
                    warn(msg)

    print(f"  models.json: {len(models)} entries, {len(seen_ids)} unique IDs")


def validate_embeddings(embeddings: list[dict]):
    seen_ids = set()

    for emb in embeddings:
        eid = emb.get("id", "(no id)")

        if "id" not in emb:
            error(f"embeddings.json: entry missing 'id'")
        if "name" not in emb:
            error(f"embeddings.json: {eid} missing 'name'")
        if "provider" not in emb:
            error(f"embeddings.json: {eid} missing 'provider'")

        if eid in seen_ids:
            error(f"embeddings.json: duplicate id '{eid}'")
        seen_ids.add(eid)

        # Source check
        source = emb.get("source")
        if not source:
            warn(f"embeddings.json: {eid} missing 'source'")
        elif not source.startswith("https://"):
            warn(f"embeddings.json: {eid} source is not an https URL: '{source}'")

    print(f"  embeddings.json: {len(embeddings)} entries, {len(seen_ids)} unique IDs")


def validate_pricing(pricing: dict):
    if "updated" not in pricing:
        warn("pricing.json: missing 'updated' date")
        return

    try:
        updated = datetime.strptime(pricing["updated"], "%Y-%m-%d")
    except ValueError:
        error(f"pricing.json: invalid 'updated' date '{pricing['updated']}'")
        return

    age_days = (datetime.now() - updated).days
    if age_days > 7:
        warn(
            f"pricing.json: 'updated' is {age_days}d old — consider running fetch_openrouter_prices.py"
        )

    print(f"  pricing.json: updated {pricing['updated']}")


def validate_routing(routing: dict, model_ids: set[str] = None):
    quick_matrix = routing.get("quick_matrix", [])
    if not quick_matrix:
        warn("routing.json: quick_matrix is empty")
        return

    for item in quick_matrix:
        if "task" not in item:
            error("routing.json: quick_matrix entry missing 'task'")
        if "use" not in item:
            error("routing.json: quick_matrix entry missing 'use'")

        # Validate ID references against models.json
        if model_ids:
            for field in ["use_id", "backup_id", "free_id"]:
                mid = item.get(field)
                if mid and mid not in model_ids:
                    warn(
                        f"routing.json: quick_matrix '{item.get('task', '')}' {field}='{mid}' not in models.json"
                    )

    # Validate king_picks IDs (nested dict: group → category → picks)
    king_picks = routing.get("king_picks", {})
    if model_ids and isinstance(king_picks, dict):
        for group_name, categories in king_picks.items():
            if not isinstance(categories, dict):
                continue
            for cat_name, picks in categories.items():
                if not isinstance(picks, dict):
                    continue
                for pick_key in [
                    "quality_1",
                    "quality_2",
                    "budget_1",
                    "budget_2",
                    "free",
                ]:
                    pick = picks.get(pick_key)
                    if isinstance(pick, dict):
                        mid = pick.get("id")
                        if mid and mid not in model_ids:
                            warn(
                                f"routing.json: king_picks {group_name}.{cat_name}.{pick_key} id='{mid}' not in models.json"
                            )

    print(f"  routing.json: {len(quick_matrix)} quick matrix entries")


def main():
    parser = argparse.ArgumentParser(description="Validate data files")
    parser.add_argument(
        "--strict", action="store_true", help="Fail on stale scores (not just warn)"
    )
    args = parser.parse_args()

    print("Validating data files...")

    benchmarks = load_json(BENCHMARKS_FILE)
    if benchmarks:
        validate_benchmarks(benchmarks)

    models = load_json(MODELS_FILE)
    if models:
        validate_models(models, args.strict)

    embeddings = load_json(EMBEDDINGS_FILE)
    if embeddings:
        validate_embeddings(embeddings)

    pricing = load_json(PRICING_FILE)
    if pricing:
        validate_pricing(pricing)

    routing = load_json(ROUTING_FILE)
    model_ids = {m["id"] for m in models} if models else set()
    if routing:
        validate_routing(routing, model_ids)

    print()

    if warnings:
        print(f"--- WARNINGS ({len(warnings)}) ---")
        for w in warnings:
            print(f"  {w}")
        print()

    if errors:
        print(f"--- ERRORS ({len(errors)}) ---")
        for e in errors:
            print(f"  {e}")
        print()
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        sys.exit(1)
    else:
        print(f"OK: 0 errors, {len(warnings)} warning(s)")


if __name__ == "__main__":
    main()
