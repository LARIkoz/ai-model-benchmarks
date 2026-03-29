# AI Model Benchmarks 2026

> **Community-driven reference for AI model selection: benchmarks, pricing, routing, embeddings**

[![Last Update](https://img.shields.io/badge/last_update-2026--03--29-blue)](CHANGELOG.md)
[![Models](https://img.shields.io/badge/models-104-green)](data/models.json)
[![Embeddings](https://img.shields.io/badge/embeddings-26-purple)](data/embeddings.json)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

## What makes this different

Most benchmark tables show one score per model, measured at some unknown date. This repo tracks:

- **Per-score freshness dates** — every benchmark value has a `measured` field showing when it was collected
- **Auto-updated pricing** — script fetches current prices from OpenRouter API (daily GitHub Action planned)
- **Task routing recommendations** — not just "best model" but "best model for your specific task at your budget"
- **Benchmark lifecycle** — active vs saturated vs dead benchmarks, contamination risk, volatility

## Quick start

- **Browse the data:** `data/models.json`, `data/embeddings.json`, `data/benchmarks.json`
- **Find the right model:** `data/routing.json` — KING picks by category, quick decision matrix
- **Understand the methodology:** `docs/METHODOLOGY.md`

## Data structure

```
data/
  models.json       — 104 chat/completion models with scores, pricing, metadata
  embeddings.json   — 26 embedding models with MTEB scores and use-case routing
  benchmarks.json   — Registry of all tracked benchmarks with lifecycle status
  routing.json      — Task routing: KING picks, FREE routing, quick decision matrix
  pricing.json      — Cache pricing by provider (updated via script)

docs/
  METHODOLOGY.md    — Sources, freshness policy, benchmark lifecycle
  CONTRIBUTING.md   — How to submit scores and report errors
  FRESHNESS.md      — Why freshness matters, staleness indicators

scripts/
  fetch_openrouter_prices.py  — Fetches current prices, detects changes
  validate.py                 — Schema validation, duplicate check, freshness warnings
  generate_md.py              — Generates markdown tables from JSON data
```

## How to use

### Find the right model for a task

Check `data/routing.json`, section `quick_matrix`. Example entries:

| Task                  | Use                 | Backup          | Free              |
| --------------------- | ------------------- | --------------- | ----------------- |
| Write/review code     | Claude Sonnet 4.6   | MiniMax M2.5    | MiniMax M2.5 FREE |
| Complex reasoning     | Claude Opus 4.6     | Gemini 3.1 Pro  | Gemini CLI        |
| Batch classification  | Qwen CLI            | MiniMax M2.5    | Both free         |
| Long document (>200K) | Gemini 3.1 Pro (1M) | MiniMax 01 (1M) | Gemini CLI (2M)   |
| EU compliance         | Mistral Large       | Mistral Medium  | —                 |

Full routing table: `data/routing.json` → `quick_matrix` (25 task categories).

```bash
# Generate the full markdown reference
python scripts/generate_md.py > MODEL_BENCHMARKS.md
```

### Stay current on pricing

Pricing is updated by running the fetch script:

```bash
python scripts/fetch_openrouter_prices.py
```

### Validate data integrity

```bash
python scripts/validate.py
```

## How to contribute

Pull requests welcome. Requirements:

1. **Source link required** — every score must have a `source` URL pointing to the leaderboard or paper
2. **Measured date required** — use `YYYY-MM` format minimum, `YYYY-MM-DD` preferred
3. **No self-reported scores** — scores must come from independent benchmarking (not the model provider's own blog)
4. Run `python scripts/validate.py` before submitting — PRs should pass validation before submission

See `docs/CONTRIBUTING.md` for full guidelines.

## Planned update schedule

- **Daily (planned — 06:00 UTC):** Prices fetched from OpenRouter API via GitHub Action, `data/pricing.json` updated
- **Weekly (manual):** Benchmark scores reviewed against leaderboards, freshness dates updated
- **On PR (planned):** Schema validation via GitHub Action

> **Note:** GitHub Actions workflows for daily price updates and PR validation are not yet deployed. Until CI is active, run `python scripts/fetch_openrouter_prices.py` and `python scripts/validate.py` manually before submitting a PR.

## Sources

Scores come from: LM Council, Artificial Analysis, Scale AI SEAL, BFCL V4, BenchLM.ai, RankSaga/Kaggle, Z.ai, MiniMax, OpenRouter official, AIModelsMap, Awesome Agents, MedQA, VALS.ai, FDA, PricePerToken, MTEB Leaderboard, Prem.ai, Mixpeek.

See `docs/METHODOLOGY.md` for full source list and trust hierarchy.

## License

MIT — see [LICENSE](LICENSE)
