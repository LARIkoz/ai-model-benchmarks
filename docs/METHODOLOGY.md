# Methodology

## Where scores come from

All scores are sourced from independent third-party benchmarks. We do not accept self-reported scores from model providers.

### Primary sources (in trust order)

1. **Scale AI SEAL** — `scale.com/leaderboard` — SWE-Bench Verified, SWE-Bench Pro, Legal/Finance domain
2. **Artificial Analysis** — `artificial-analysis.com` — GPQA, comprehensive model comparison
3. **Humanity's Last Exam** — `lastexam.ai` — HLE scores
4. **ARC Prize** — `arcprize.org` — ARC-AGI-2 scores
5. **BFCL (Berkeley)** — `gorilla.cs.berkeley.edu` — Function calling benchmark
6. **BenchLM** — `benchlm.ai` — Aggregate benchmark score
7. **LM Arena** — `lmarena.ai` — Human preference ELO
8. **Tau-Bench** — Multi-turn tool use
9. **LiveBench** — `livebench.ai` — Monthly fresh evaluation
10. **Zyte** — `zyte.com/blog` — Web scraper code quality (ROUGE-1)
11. **Promon** — Assembly deobfuscation benchmark (2025)
12. **JsDeObsBench** — CCS 2025, JS deobfuscation
13. **FuzzingLabs** — Android APK reverse engineering (2025)
14. **VALS.ai** — Medical AI bias testing
15. **MTEB Leaderboard** — Embedding model evaluation
16. **OpenRouter API** — `/api/v1/models` — Pricing (fetched daily)

## What "verified" means

A score is "verified" when:

- It comes from one of the 16 sources listed above
- The `source` field in the JSON points to the specific leaderboard or paper
- The `measured` date reflects when the score was actually collected (not when we added it)

Scores marked with `notes: "estimated"` or `notes: "extrapolated"` are NOT verified. They are reasonable estimates based on model generation progression, clearly labeled.

## How freshness works

Every score in `data/models.json` has a `measured` field:

- Format: `YYYY-MM` minimum, `YYYY-MM-DD` when available
- This is the date the score was **measured**, not when it was added to this repo
- Scores without a `measured` date are invalid — they will be flagged by `validate.py`

The `data/benchmarks.json` `volatility` field tells you how fast scores change:

- `low` — stable for months (SWE-Bench, GPQA)
- `medium` — can shift quarterly (ARC-AGI-2, HLE)
- `high` — changes frequently (LMArena ELO, LiveBench)

Rule of thumb: if `measured` is >30 days ago and `volatility` is `high`, treat with skepticism.

## Benchmark lifecycle

| Status      | Meaning                                                        |
| ----------- | -------------------------------------------------------------- |
| `planned`   | Benchmark tracked in registry but no scores collected yet.     |
| `active`    | Meaningful separation between models, worth tracking           |
| `saturated` | Frontier models all score 90%+, no separation                  |
| `dead`      | Saturated AND contaminated AND replaced by better alternatives |

Dead benchmarks are kept in `data/benchmarks.json` for historical context but are never cited in routing recommendations.

**Currently dead:** MMLU, HumanEval, BBH, DROP, MGSM, GSM8K, MATH base, HellaSwag

## Contamination awareness

`contamination_risk` in `data/benchmarks.json` reflects:

- `low` — questions generated fresh (LiveBench, HLE), or from novel problems models haven't seen
- `medium` — questions potentially leaked through training data, but evidence is unclear
- `high` — questions almost certainly in frontier model training sets (MMLU, HumanEval)

High contamination + saturated = dead benchmark.

## How to read the data

### models.json

- `tier: 1` — Frontier (>$1/M input)
- `tier: 2` — Mid-range ($0.20-$1/M input)
- `tier: 3` — Budget (<$0.20/M input)
- `tier: 0` — FREE (OpenRouter free, CLI tools)

Scores for a model are omitted if not available (never `null` in scores object — missing key = no data).

### embeddings.json

`mteb_overall` is the average across 56+ MTEB tasks. For RAG specifically, use `mteb_retrieval` (NDCG@10). Overall ≠ retrieval quality.

### routing.json

`king_picks` gives the single best option per category. Always check `budget_1` before assuming you need the `quality_1` pick — budget models often score within 5% at 10x lower cost.

## Updating scores

Update schedule:

- **Daily (manual, automation planned):** prices via fetch script
- **Weekly (manual):** check major leaderboards for score changes
- **On model release:** add to appropriate tier within 48 hours

Full revalidation policy: every score is verified against current leaderboard state each week. Incremental "only check new models" is explicitly rejected — leaderboards backfill and correct older scores.
