#!/usr/bin/env python3
"""
Generates MODEL_BENCHMARKS.md from data/*.json files.
Output mirrors the format used in ~/.claude/skills/openrouter-api/MODEL_BENCHMARKS.md

Usage:
    python scripts/generate_md.py > MODEL_BENCHMARKS.md
    python scripts/generate_md.py --output MODEL_BENCHMARKS.md
"""

import json
import argparse
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).parent.parent


def load_json(name: str) -> dict | list:
    with open(REPO_ROOT / "data" / f"{name}.json") as f:
        return json.load(f)


def fmt_price(v) -> str:
    if v is None:
        return "varies"
    if v == 0:
        return "$0"
    if v < 0.01:
        return f"${v:.4f}"
    if v < 1:
        return f"${v:.2f}"
    return f"${v:.1f}"


def fmt_score(score_obj: dict | None, key: str = "value") -> str:
    if not score_obj:
        return "—"
    v = score_obj.get(key)
    if v is None:
        return "—"
    if isinstance(v, float) and v < 10:
        return str(round(v, 3))
    return str(v)


def get_score(model: dict, bench: str) -> str:
    return fmt_score(model.get("scores", {}).get(bench))


def generate_tier1_table(models: list[dict]) -> str:
    tier1 = [m for m in models if m.get("tier") == 1]
    lines = [
        "### Tier 1: Frontier (>$1/M input)",
        "",
        "| Model | $/M in→out | Ctx | SWE-V | SWE-Pro | GPQA | HLE | ARC-AGI-2 | Tau2 | Term.B2 | BenchLM |",
        "|-------|-----------|-----|-------|---------|------|-----|-----------|------|---------|---------|",
    ]
    for m in tier1:
        p = m.get("pricing", {})
        inp = fmt_price(p.get("input"))
        out = fmt_price(p.get("output"))
        ctx_raw = m.get("context_length", 0)
        if ctx_raw:
            ctx = (
                f"{ctx_raw // 1000}K"
                if ctx_raw < 1_000_000
                else f"{ctx_raw // 1_000_000}M"
            )
        else:
            ctx = "—"
        line = (
            f"| **{m['name']}** | {inp}→{out} | {ctx} "
            f"| {get_score(m, 'swe_v')} | {get_score(m, 'swe_pro')} "
            f"| {get_score(m, 'gpqa')} | {get_score(m, 'hle')} "
            f"| {get_score(m, 'arc_agi_2')} | {get_score(m, 'tau2')} "
            f"| {get_score(m, 'terminal_bench_2')} | {get_score(m, 'benchlm')} |"
        )
        lines.append(line)
    return "\n".join(lines)


def generate_tier2_table(models: list[dict]) -> str:
    tier2 = [m for m in models if m.get("tier") == 2]
    lines = [
        "### Tier 2: Mid-range ($0.20-$1/M input)",
        "",
        "| Model | $/M in→out | Ctx | SWE-V | SWE-Pro | GPQA | HLE | Tau2 | Best for |",
        "|-------|-----------|-----|-------|---------|------|-----|------|----------|",
    ]
    for m in tier2:
        p = m.get("pricing", {})
        inp = fmt_price(p.get("input"))
        out = fmt_price(p.get("output"))
        ctx_raw = m.get("context_length", 0)
        if ctx_raw:
            ctx = (
                f"{ctx_raw // 1000}K"
                if ctx_raw < 1_000_000
                else f"{ctx_raw // 1_000_000}M"
            )
        else:
            ctx = "—"
        best = ", ".join(m.get("best_for", [])[:2]) or "—"
        line = (
            f"| **{m['name']}** | {inp}→{out} | {ctx} "
            f"| {get_score(m, 'swe_v')} | {get_score(m, 'swe_pro')} "
            f"| {get_score(m, 'gpqa')} | {get_score(m, 'hle')} "
            f"| {get_score(m, 'tau2')} | {best} |"
        )
        lines.append(line)
    return "\n".join(lines)


def generate_tier3_table(models: list[dict]) -> str:
    tier3 = [m for m in models if m.get("tier") == 3]
    lines = [
        "### Tier 3: Budget (<$0.20/M input)",
        "",
        "| Model | $/M in→out | Ctx | Notes |",
        "|-------|-----------|-----|-------|",
    ]
    for m in tier3:
        p = m.get("pricing", {})
        inp = fmt_price(p.get("input"))
        out = fmt_price(p.get("output"))
        ctx_raw = m.get("context_length", 0)
        if ctx_raw:
            ctx = (
                f"{ctx_raw // 1000}K"
                if ctx_raw < 1_000_000
                else f"{ctx_raw // 1_000_000}M"
            )
        else:
            ctx = "—"
        notes = ", ".join(m.get("best_for", [])[:1]) or "—"
        line = f"| **{m['name']}** | {inp}→{out} | {ctx} | {notes} |"
        lines.append(line)
    return "\n".join(lines)


def generate_free_table(models: list[dict]) -> str:
    free_or = [
        m
        for m in models
        if m.get("tier") == 0 and m.get("channel") == "openrouter_free"
    ]
    free_cli = [
        m
        for m in models
        if m.get("tier") == 0 and m.get("channel") != "openrouter_free"
    ]

    lines = ["### Tier FREE ($0)", ""]
    if free_or:
        lines += [
            "**OpenRouter FREE models**",
            "",
            "| Model | OR ID | Ctx | Best for |",
            "|-------|-------|-----|----------|",
        ]
        for m in free_or:
            or_id = m.get("openrouter_id", "—")
            ctx_raw = m.get("context_length", 0)
            ctx = f"{ctx_raw // 1000}K" if ctx_raw else "—"
            best = ", ".join(m.get("best_for", [])[:1]) or "—"
            lines.append(f"| **{m['name']}** | `{or_id}` | {ctx} | {best} |")

    if free_cli:
        lines += [
            "",
            "**FREE CLI (subscription-powered)**",
            "",
            "| Model | Channel | Ctx | Best for |",
            "|-------|---------|-----|----------|",
        ]
        for m in free_cli:
            channel = m.get("channel", "—")
            ctx_raw = m.get("context_length", 0)
            ctx = f"{ctx_raw // 1000}K" if ctx_raw else "—"
            best = ", ".join(m.get("best_for", [])[:1]) or "—"
            lines.append(f"| **{m['name']}** | {channel} | {ctx} | {best} |")

    return "\n".join(lines)


def generate_quick_matrix(routing: dict) -> str:
    matrix = routing.get("quick_matrix", [])
    lines = [
        "## Quick Decision Matrix",
        "",
        "| If task... | Use | Backup | Free |",
        "|------------|-----|--------|------|",
    ]
    for row in matrix:
        task = row.get("task", "—")
        use = row.get("use", "—")
        backup = row.get("backup", "—") or "—"
        free = row.get("free", "—") or "—"
        lines.append(f"| {task} | **{use}** | {backup} | {free} |")
    return "\n".join(lines)


def generate_embeddings_table(embeddings: list[dict]) -> str:
    lines = [
        "## Embedding Models",
        "",
        "| Model | OR ID | MTEB | Retrieval | Dims | Ctx | $/M | License | Best for |",
        "|-------|-------|------|-----------|------|-----|-----|---------|----------|",
    ]
    for e in embeddings:
        or_id = e.get("openrouter_id") or "—"
        mteb = e.get("mteb_overall")
        ret = e.get("mteb_retrieval")
        dims = e.get("dimensions")
        ctx_raw = e.get("context_length", 0)
        price = e.get("pricing_per_million_tokens")
        license_ = e.get("license", "—")
        best = ", ".join(e.get("best_for", [])[:2]) or "—"

        ctx = f"{ctx_raw // 1000}K" if ctx_raw else "—"
        mteb_s = str(mteb) if mteb is not None else "—"
        ret_s = str(ret) if ret is not None else "—"
        dims_s = str(dims) if dims is not None else "—"
        price_s = f"${price}" if price is not None else "—"
        if price == 0:
            price_s = "**FREE**"

        line = (
            f"| **{e['name']}** | `{or_id}` | {mteb_s} | {ret_s} | {dims_s} | {ctx} "
            f"| {price_s} | {license_} | {best} |"
        )
        lines.append(line)
    return "\n".join(lines)


def generate_cache_pricing(pricing: dict) -> str:
    rows = pricing.get("key_models_cache_pricing", [])
    lines = [
        "## Cache Pricing",
        "",
        "| Model | Input $/M | Cached $/M | Discount |",
        "|-------|-----------|-----------|----------|",
    ]
    for row in rows:
        inp = fmt_price(row.get("input_per_m"))
        cached = fmt_price(row.get("cached_per_m"))
        discount = row.get("discount", "—")
        lines.append(f"| **{row['model']}** | {inp} | **{cached}** | {discount} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate MODEL_BENCHMARKS.md from JSON data"
    )
    parser.add_argument(
        "--output", "-o", default="-", help="Output file (default: stdout)"
    )
    args = parser.parse_args()

    models = load_json("models")
    embeddings = load_json("embeddings")
    routing = load_json("routing")
    pricing = load_json("pricing")
    today = date.today().isoformat()

    sections = [
        f"# Model Benchmarks — Generated Reference ({today})",
        "",
        f"> Auto-generated from data/*.json. Edit source files, not this document.",
        f"> Verified: {today}. Sources: see docs/METHODOLOGY.md",
        "",
        "---",
        "",
        "## MEGA-TABLE: All Models",
        "",
        generate_tier1_table(models),
        "",
        generate_tier2_table(models),
        "",
        generate_tier3_table(models),
        "",
        generate_free_table(models),
        "",
        "---",
        "",
        generate_embeddings_table(embeddings),
        "",
        "---",
        "",
        generate_cache_pricing(pricing),
        "",
        "---",
        "",
        generate_quick_matrix(routing),
    ]

    output = "\n".join(sections)

    if args.output == "-":
        print(output)
    else:
        out_path = Path(args.output)
        out_path.write_text(output)
        print(f"Written to {out_path}", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
