#!/usr/bin/env python3
"""
Генератор index.html из data/*.json.
Заменяет JS-блоки данных в HTML, сохраняя всю разметку и CSS без изменений.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
HTML_PATH = ROOT / "index.html"
DATA_DIR = ROOT / "data"

# JS-строка для пустого значения — em-dash
DASH = '"\u2014"'

DRY_RUN = "--dry-run" in sys.argv


def fmt_ctx(ctx_len: int | None) -> str:
    if not ctx_len:
        return "?"
    if ctx_len >= 1_000_000:
        n = ctx_len // 1_000_000
        return f"{n}M"
    if ctx_len >= 1000:
        n = ctx_len // 1000
        return f"{n}K"
    return str(ctx_len)


def fmt_score(v) -> str:
    if v is None:
        return "null"
    return str(v)


def fmt_score_obj(entry) -> str:
    """Преобразует score-объект из models.json в JS-объект с метаданными."""
    if entry is None:
        return "null"
    if isinstance(entry, dict):
        val = entry.get("value")
        if val is None:
            return "null"
        measured = entry.get("measured") or ""
        source = entry.get("source") or ""
        # Экранируем строки через json.dumps
        d_str = json.dumps(measured)
        s_str = json.dumps(source)
        return f"{{v:{val},d:{d_str},s:{s_str}}}"
    # backward compat: plain number
    return str(entry)


def fmt_str(s) -> str:
    if s is None:
        return "null"
    # Use json.dumps for safe JS string escaping (handles newlines, quotes, </script>, unicode)
    return json.dumps(s, ensure_ascii=False)


def fmt_num(v) -> str:
    if v is None:
        return "null"
    return str(v)


def tier_str(tier: int) -> str:
    if tier == 0:
        return "free"
    return str(tier)


def pick_label(entry: dict | None) -> str:
    """Формирует строку вида 'Name (score%, $price)' из king_picks entry."""
    if not entry:
        return '"—"'
    name = entry.get("name", "")
    score = entry.get("score")
    price = entry.get("price")
    parts = []
    if score is not None:
        parts.append(f"{score}%")
    if price is not None and price > 0:
        parts.append(f"${price}")
    label = name + (f" ({', '.join(parts)})" if parts else "")
    return fmt_str(label)


def key_to_label(key: str) -> str:
    """Преобразует snake_case ключ в читаемый заголовок."""
    return key.replace("_", " ").title()


def bench_label(bench: str | None) -> str:
    if not bench:
        return '"practical"'
    # Стандартные названия бенчмарков
    mapping = {
        "swe_v": "SWE-V",
        "swe_pro": "SWE-Pro",
        "gpqa": "GPQA",
        "hle": "HLE",
        "arc_agi_2": "ARC-AGI-2",
        "tau2": "TAU2",
        "benchlm": "BenchLM",
        "terminal_bench_2": "Terminal-B2",
        "scicode": "SciCode",
        "aime_2025": "AIME 2025",
        "grind": "Grind",
        "bfcl": "BFCL",
        "ifbench": "IFBench",
        "simpleqa": "SimpleQA",
        "mmmu": "MMMU",
        "video_mme": "Video-MME",
        "usmle": "USMLE",
        "zyte": "Zyte",
        "seal": "SEAL",
    }
    return fmt_str(mapping.get(bench, bench.upper()))


# ─── Генераторы JS-блоков ─────────────────────────────────────────────────────


def gen_models(models: list) -> str:
    lines = []
    for m in models:
        s = m.get("scores", {})

        def sc(k):
            """Возвращает полный score-объект (dict) или None."""
            v = s.get(k)
            if v is None:
                return None
            if isinstance(v, dict):
                return v if v.get("value") is not None else None
            return None

        best = m.get("best_for", [])
        best_str = ", ".join(best) if best else ""

        # Capability flags
        caps = m.get("capabilities", {})
        cap_flags = []
        if caps.get("vision"):
            cap_flags.append("V")
        if caps.get("tool_calling"):
            cap_flags.append("T")
        if caps.get("reasoning"):
            cap_flags.append("R")
        if caps.get("structured_output"):
            cap_flags.append("S")
        if caps.get("audio_input"):
            cap_flags.append("A")
        if caps.get("image_output"):
            cap_flags.append("I")
        cap_str = "".join(cap_flags)

        max_out = m.get("max_output_tokens")
        max_out_str = fmt_ctx(max_out) if max_out else ""

        lines.append(
            "        {"
            f'tier: "{tier_str(m["tier"])}", '
            f"name: {fmt_str(m['name'])}, "
            f"priceIn: {fmt_num(m.get('pricing', {}).get('input'))}, "
            f"priceOut: {fmt_num(m.get('pricing', {}).get('output'))}, "
            f'ctx: "{fmt_ctx(m.get("context_length"))}", '
            f'maxOut: "{max_out_str}", '
            f'caps: "{cap_str}", '
            f"swe_v: {fmt_score_obj(sc('swe_v'))}, "
            f"swe_pro: {fmt_score_obj(sc('swe_pro'))}, "
            f"gpqa: {fmt_score_obj(sc('gpqa'))}, "
            f"hle: {fmt_score_obj(sc('hle'))}, "
            f"arc: {fmt_score_obj(sc('arc_agi_2'))}, "
            f"tau2: {fmt_score_obj(sc('tau2'))}, "
            f"benchlm: {fmt_score_obj(sc('benchlm'))}, "
            f"best: {fmt_str(best_str)}"
            "},"
        )
    return "[\n" + "\n".join(lines) + "\n      ]"


# Маппинг категорий king_picks → буква + заголовок KING_GROUPS
KING_CAT_META = {
    "coding": ("A", "Coding & Software Engineering"),
    "reasoning": ("B", "Reasoning & Knowledge"),
    "tools_and_agents": ("C", "Tools & Agents"),
    "content_and_communication": ("D", "Content & Communication"),
    "multimodal": ("E", "Multimodal"),
    "domain_and_infrastructure": ("F", "Domain & Infrastructure"),
    "web_scraping": ("G", "Web Scraping & Data"),
    "reverse_engineering": ("H", "Reverse Engineering"),
    "medical": ("I", "Medical & Scientific"),
    "data_analysis": ("J", "Data Analysis"),
    "writing_naturalness": ("K", "Writing & Naturalness"),
    "local_models": ("L", "Local / Self-Hosted"),
    "audio_speech": ("M", "Audio & Speech"),
    "video_understanding": ("N", "Video Understanding"),
}

# Маппинг entry key → читаемое cat name (чтобы совпадало с текущим HTML)
ENTRY_CAT_NAMES = {
    "coding_general_swe_v": "Coding general",
    "coding_uncontaminated_swe_pro": "Coding uncontaminated",
    "code_generation": "Code generation",
    "scientific_coding_scicode": "Scientific coding",
    "agentic_coding_terminal_b2": "Agentic coding",
    "code_review_practical": "Code review",
    "graduate_science_gpqa": "Graduate science",
    "hardest_reasoning_hle": "Hardest reasoning",
    "abstract_reasoning_arc_agi_2": "Abstract reasoning",
    "math_competition_aime_2025": "Math competition",
    "adaptive_reasoning_grind": "Adaptive reasoning",
    "function_calling_bfcl": "Function calling",
    "multi_turn_tools_tau2": "Multi-turn tools",
    "instruction_following_ifbench": "Instruction following",
    "hallucination_resistance_simpleqa": "Hallucination resistance",
    "vision_mmmu": "Vision (MMMU)",
    "video_input": "Video input",
    "legal_finance_seal": "Legal / finance",
    "long_context_over_200k": "Long context >200K",
    "scraper_code_gen_zyte": "Scraper code gen",
    "saas_api_reverse_engineering": "SaaS API RE",
    "js_deobfuscation": "JS deobfuscation",
    "assembly_deobfuscation": "Assembly / binary RE",
    "medical_qa_usmle": "Medical QA",
    "biomedical_literature": "Biomedical literature",
    "marketing_analytics": "Marketing analytics",
    "financial_analysis": "Financial analysis",
    "natural_copywriting": "Natural copywriting",
    "academic_writing": "Academic writing",
    "local_16gb_plus": "Local 16GB+",
    "local_8gb": "Local 8GB",
    "transcription_accuracy": "Transcription accuracy",
    "speaker_diarization": "Speaker diarization",
    "video_content_recognition": "Video content recognition",
    "video_qa": "Video QA",
}


def gen_king_groups(king_picks: dict) -> str:
    groups = []
    for cat_key, entries in king_picks.items():
        meta = KING_CAT_META.get(cat_key)
        if not meta:
            letter = chr(ord("A") + list(king_picks.keys()).index(cat_key))
            title = key_to_label(cat_key)
        else:
            letter, title = meta

        rows = []
        for entry_key, entry in entries.items():
            cat_label = ENTRY_CAT_NAMES.get(entry_key, key_to_label(entry_key))
            bench = entry.get("bench")
            q1 = entry.get("quality_1")
            q2 = entry.get("quality_2")
            b1 = entry.get("budget_1")
            b2 = entry.get("budget_2")
            free = entry.get("free")

            free_str = pick_label(free) if free else DASH
            b1_str = pick_label(b1) if b1 else DASH
            b2_str = pick_label(b2) if b2 else DASH

            rows.append(
                "            {"
                f"cat: {fmt_str(cat_label)}, "
                f"benchKey: {fmt_str(bench) if bench else 'null'}, "
                f"bench: {bench_label(bench)}, "
                f"q1: {pick_label(q1)}, "
                f"q2: {pick_label(q2)}, "
                f"b1: {b1_str}, "
                f"b2: {b2_str}, "
                f"free: {free_str}"
                "},"
            )

        groups.append(
            "        {\n"
            f'          letter: "{letter}",\n'
            f"          title: {fmt_str(title)},\n"
            "          rows: [\n" + "\n".join(rows) + "\n"
            "          ],\n"
            "        },"
        )

    return "[\n" + "\n".join(groups) + "\n      ]"


def gen_matrix(quick_matrix: list) -> str:
    lines = []
    for item in quick_matrix:
        lines.append(
            "        {"
            f"task: {fmt_str(item.get('task'))}, "
            f"pick: {fmt_str(item.get('use'))}, "
            f"backup: {fmt_str(item.get('backup'))}, "
            f"free: {fmt_str(item.get('free'))}"
            "},"
        )
    return "[\n" + "\n".join(lines) + "\n      ]"


FREE_TASK_NAMES = {
    "code_generation": "Code generation",
    "code_review": "Code review",
    "niche_classification": "Niche classification",
    "app_dna_categorization": "App DNA / categorization",
    "consilium_second_opinion": "Consilium (2nd opinion)",
    "reasoning_architecture": "Reasoning / architecture",
    "long_document_analysis": "Long document analysis",
    "batch_general_1000_plus": "Batch general (1000+ items)",
    "vision_screenshots": "Vision / screenshots",
    "writing_copywriting": "Writing / copywriting",
    "multilingual": "Multilingual",
    "tool_calling": "Tool calling",
    "research": "Research",
    "uncensored_no_filter": "Uncensored / no filter",
    "edge_mobile_iot": "Edge / mobile / IoT",
    "thinking_cot": "Thinking / CoT",
    "embeddings": "Embeddings",
}


def gen_free_routing(free_routing: dict) -> str:
    lines = []
    for key, entry in free_routing.items():
        task = FREE_TASK_NAMES.get(key, key_to_label(key))
        cli_list = entry.get("free_cli", [])
        cli_str = ", ".join(cli_list) if cli_list else "—"
        lines.append(
            "        {"
            f"task: {fmt_str(task)}, "
            f"best: {fmt_str(entry.get('best_free_or'))}, "
            f"backup: {fmt_str(entry.get('backup_free_or'))}, "
            f"cli: {fmt_str(cli_str)}"
            "},"
        )
    return "[\n" + "\n".join(lines) + "\n      ]"


EMB_TASK_NAMES = {
    "rag_english_under_8k_chunks": "RAG (English, <8K chunks)",
    "rag_accuracy_critical": "RAG (accuracy-critical)",
    "rag_multilingual_russian": "RAG (multilingual / Russian)",
    "code_search_codebase_rag": "Code search / codebase RAG",
    "long_docs_over_8k_tokens": "Long docs (>8K tokens)",
    "ultra_long_over_32k_books": "Ultra-long (>32K, books)",
    "image_text_multimodal": "Image+text (multimodal)",
    "bulk_indexing_100k_plus": "Bulk indexing (100K+ docs)",
    "classification_clustering": "Classification / clustering",
    "semantic_search_saas": "Semantic search (SaaS)",
    "enterprise_noisy_ocr": "Enterprise (noisy OCR)",
    "edge_mobile_on_device": "Edge / mobile (on-device)",
    "privacy_first_no_cloud": "Privacy-first (no cloud)",
    "prototype_mvp": "Prototype / MVP",
    "domain_tuned_legal_medical": "Domain-tuned (legal/medical)",
}


def gen_emb_use_cases(embedding_routing: dict) -> str:
    lines = []
    for key, entry in embedding_routing.items():
        task = EMB_TASK_NAMES.get(key, key_to_label(key))
        lines.append(
            "        {"
            f"task: {fmt_str(task)}, "
            f"best: {fmt_str(entry.get('best'))}, "
            f"budget: {fmt_str(entry.get('budget'))}, "
            f"free: {fmt_str(entry.get('free'))}"
            "},"
        )
    return "[\n" + "\n".join(lines) + "\n      ]"


def gen_cache_providers(providers: list) -> str:
    lines = []
    for p in providers:
        disc = p.get("cache_read_discount", "—")
        # Заменяем дефис на en-dash для единообразия с HTML
        disc = disc.replace("-", "–")
        write = p.get("cache_write_multiplier") or "—"
        mech = p.get("mechanism", "—")
        # Сокращаем механизм если нужно
        if p.get("cache_storage"):
            mech = f"Automatic, storage free"
        lines.append(
            "        {"
            f"provider: {fmt_str(p['provider'])}, "
            f"disc: {fmt_str(disc)}, "
            f"write: {fmt_str(write)}, "
            f"mech: {fmt_str(mech)}"
            "},"
        )
    return "[\n" + "\n".join(lines) + "\n      ]"


def gen_cache_models(models: list) -> str:
    lines = []
    for m in models:
        note = m.get("note") or ""
        # Добавляем звезду к первой записи Anthropic как в оригинале
        lines.append(
            "        {"
            f"model: {fmt_str(m['model'])}, "
            f"input: {fmt_num(m.get('input_per_m'))}, "
            f"cached: {fmt_num(m.get('cached_per_m'))}, "
            f"disc: {fmt_str(m.get('discount'))}, "
            f"note: {fmt_str(note)}"
            "},"
        )
    return "[\n" + "\n".join(lines) + "\n      ]"


# ─── Замена JS-блоков ─────────────────────────────────────────────────────────


def find_block_end(html: str, start_idx: int, open_char: str, close_char: str) -> int:
    """
    Находит позицию закрывающего символа блока с учётом вложенности.
    Учитывает строки (одинарные и двойные кавычки) и template literals.
    """
    depth = 0
    i = start_idx
    in_single = False
    in_double = False
    in_template = False

    while i < len(html):
        c = html[i]

        if in_single:
            if c == "\\" and i + 1 < len(html):
                i += 2
                continue
            if c == "'":
                in_single = False
            i += 1
            continue

        if in_double:
            if c == "\\" and i + 1 < len(html):
                i += 2
                continue
            if c == '"':
                in_double = False
            i += 1
            continue

        if in_template:
            if c == "\\" and i + 1 < len(html):
                i += 2
                continue
            if c == "`":
                in_template = False
            i += 1
            continue

        if c == "'":
            in_single = True
        elif c == '"':
            in_double = True
        elif c == "`":
            in_template = True
        elif c == open_char:
            depth += 1
        elif c == close_char:
            depth -= 1
            if depth == 0:
                return i

        i += 1

    raise ValueError(
        f"Не найден закрывающий символ '{close_char}' начиная с позиции {start_idx}"
    )


def replace_js_block(
    html: str, var_name: str, new_data: str, is_array: bool = True
) -> str:
    open_char = "[" if is_array else "{"
    close_char = "]" if is_array else "}"
    marker = f"const {var_name} = {open_char}"

    idx = html.find(marker)
    if idx == -1:
        raise ValueError(f"Маркер не найден: {marker!r}")

    block_start = idx + len(f"const {var_name} = ")
    end_idx = find_block_end(html, block_start, open_char, close_char)

    # Проверяем, что сразу после закрывающего символа идёт ";"
    after = html[end_idx + 1 : end_idx + 2]
    suffix = ";" if after == ";" else ""
    end_consume = end_idx + 1 + (1 if suffix else 0)

    return html[:idx] + f"const {var_name} = {new_data};" + html[end_consume:]


def replace_string_const(html: str, var_name: str, value: str) -> str:
    """Заменяет const VAR = "...";"""
    pattern = re.compile(rf'(const {re.escape(var_name)} = )"[^"]*"')
    if not pattern.search(html):
        raise ValueError(f"Паттерн const {var_name} не найден")
    return pattern.sub(rf'\g<1>"{value}"', html)


def replace_hero_stat(html: str, label: str, new_val: str) -> str:
    """Заменяет hero-stat-num для конкретного label (any current value)."""
    pattern = re.compile(
        rf'(<span class="hero-stat-num">)\s*\d+\s*(</span>\s*<span class="hero-stat-label">\s*{re.escape(label)}\s*</span>)',
        re.DOTALL,
    )
    if not pattern.search(html):
        print(f"  WARN: Hero stat not found for label {label!r} — skipping")
        return html
    return pattern.sub(rf"\g<1>{new_val}\g<2>", html)


def replace_hero_subtitle(html: str, model_count: int, bench_count: int) -> str:
    pattern = re.compile(r"(\d+) models × \d+\+ categories\s*× \d+ benchmarks")
    # Считаем категории из KING_GROUPS
    repl = rf"{model_count} models × 55+ categories × {bench_count} benchmarks"
    new = pattern.sub(repl, html)
    return new


def replace_verified_badge(html: str, today: str) -> str:
    """Заменяет строку в verified-badge."""
    pattern = re.compile(
        r"(✓ Verified )\d{4}-\d{2}-\d{2}( \(v\d+\) · Next update: )\d{4}-\d{2}-\d{2}"
    )
    # Вычисляем next update +7 дней
    from datetime import timedelta

    today_dt = date.fromisoformat(today)
    next_dt = today_dt + timedelta(days=7)
    new = html
    # Найдём все верифицированные упоминания
    pattern2 = re.compile(r"✓ Verified \d{4}-\d{2}-\d{2}")
    new = pattern2.sub(f"✓ Verified {today}", new)
    pattern3 = re.compile(r"Next update: \d{4}-\d{2}-\d{2}")
    new = pattern3.sub(f"Next update: {next_dt.isoformat()}", new)
    return new


def replace_section_verified(html: str, today: str) -> str:
    """Заменяет 'Verified YYYY-MM-DD.' в тексте секций."""
    pattern = re.compile(r"(Verified )\d{4}-\d{2}-\d{2}(\.)")
    return pattern.sub(rf"\g<1>{today}\g<2>", html)


# ─── Main ─────────────────────────────────────────────────────────────────────


def main():
    today = date.today().isoformat()

    models = json.loads((DATA_DIR / "models.json").read_text())
    routing = json.loads((DATA_DIR / "routing.json").read_text())
    pricing = json.loads((DATA_DIR / "pricing.json").read_text())
    benchmarks = json.loads((DATA_DIR / "benchmarks.json").read_text())

    html = HTML_PATH.read_text(encoding="utf-8")

    # 1. VERIFIED date constant
    html = replace_string_const(html, "VERIFIED", today)

    # 2. MODELS
    html = replace_js_block(html, "MODELS", gen_models(models), is_array=True)

    # 3. KING_GROUPS
    html = replace_js_block(
        html, "KING_GROUPS", gen_king_groups(routing["king_picks"]), is_array=True
    )

    # 4. MATRIX
    html = replace_js_block(
        html, "MATRIX", gen_matrix(routing["quick_matrix"]), is_array=True
    )

    # 5. FREE_ROUTING
    html = replace_js_block(
        html, "FREE_ROUTING", gen_free_routing(routing["free_routing"]), is_array=True
    )

    # 6. EMB_USE_CASES
    html = replace_js_block(
        html,
        "EMB_USE_CASES",
        gen_emb_use_cases(routing["embedding_routing"]),
        is_array=True,
    )

    # 7. CACHE_PROVIDERS
    html = replace_js_block(
        html,
        "CACHE_PROVIDERS",
        gen_cache_providers(pricing["cache_pricing_by_provider"]),
        is_array=True,
    )

    # 8. CACHE_MODELS
    html = replace_js_block(
        html,
        "CACHE_MODELS",
        gen_cache_models(pricing["key_models_cache_pricing"]),
        is_array=True,
    )

    # 9. Hero stats
    model_count = len(models)
    bench_count = len(benchmarks)

    html = replace_hero_subtitle(html, model_count, bench_count)
    html = replace_hero_stat(html, "models", str(model_count))
    html = replace_hero_stat(html, "benchmarks", str(bench_count))
    html = replace_verified_badge(html, today)
    html = replace_section_verified(html, today)

    if DRY_RUN:
        print(
            f"[dry-run] Без записи. Модели: {model_count}, бенчмарки: {bench_count}, дата: {today}"
        )
        print(f"[dry-run] Размер HTML: {len(html)} символов")
        return

    HTML_PATH.write_text(html, encoding="utf-8")
    print(
        f"index.html обновлён. Модели: {model_count}, бенчмарки: {bench_count}, дата: {today}"
    )

    # Generate llms-full.txt (AI agent discovery file)
    generate_llms_full(models, routing, today)


def generate_llms_full(models: list, routing: dict, today: str):
    """Generate llms-full.txt with routing table and model summary for AI agents."""
    lines = []
    lines.append("# AI Model Benchmarks 2026 — Full Data for AI Agents")
    lines.append(f"# Updated: {today}")
    lines.append("")
    lines.append("This file contains the complete routing table and model summary.")
    lines.append("For full JSON data, fetch these URLs directly:")
    lines.append(
        "- Models: https://larikoz.github.io/ai-model-benchmarks/data/models.json"
    )
    lines.append(
        "- Routing: https://larikoz.github.io/ai-model-benchmarks/data/routing.json"
    )
    lines.append(
        "- Embeddings: https://larikoz.github.io/ai-model-benchmarks/data/embeddings.json"
    )
    lines.append("")

    # Quick matrix
    lines.append("## Quick Decision Matrix (25 tasks)")
    lines.append("")
    lines.append("| Task | Best Model | Backup | Free |")
    lines.append("|------|-----------|--------|------|")
    for item in routing.get("quick_matrix", []):
        lines.append(
            f"| {item['task']} | {item['use']} | {item.get('backup', '—')} | {item.get('free', '—')} |"
        )

    lines.append("")
    lines.append(f"## All {len(models)} Models — Summary")
    lines.append("")
    lines.append(
        "| Model | Provider | Tier | Context | Max Out | $/M in | $/M out | Caps | Best For |"
    )
    lines.append(
        "|-------|----------|------|---------|---------|--------|---------|------|----------|"
    )
    for m in models:
        tier = {0: "FREE", 1: "T1", 2: "T2", 3: "T3"}.get(m["tier"], "?")
        ctx = m.get("context_length", "?")
        if isinstance(ctx, int):
            ctx = f"{ctx // 1000}K" if ctx < 1_000_000 else f"{ctx // 1_000_000}M"
        max_out = m.get("max_output_tokens", "—")
        if isinstance(max_out, int):
            max_out = f"{max_out // 1000}K"
        price_in = m.get("pricing", {}).get("input", "—")
        price_out = m.get("pricing", {}).get("output", "—")
        caps = m.get("capabilities", {})
        cap_flags = []
        if caps.get("vision"):
            cap_flags.append("V")
        if caps.get("tool_calling"):
            cap_flags.append("T")
        if caps.get("reasoning"):
            cap_flags.append("R")
        if caps.get("structured_output"):
            cap_flags.append("S")
        cap_str = "".join(cap_flags) or "—"
        best = ", ".join(m.get("best_for", [])) or "—"
        if len(best) > 50:
            best = best[:47] + "..."
        lines.append(
            f"| {m['name']} | {m['provider']} | {tier} | {ctx} | {max_out} | {price_in} | {price_out} | {cap_str} | {best} |"
        )

    lines.append("")
    lines.append("## Capability Legend")
    lines.append("V=Vision, T=Tool Calling, R=Reasoning, S=Structured Output")

    llms_full_path = ROOT / "llms-full.txt"
    llms_full_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"llms-full.txt обновлён. {len(models)} models, {len(lines)} lines")


if __name__ == "__main__":
    main()
