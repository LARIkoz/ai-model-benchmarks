# ai-model-benchmarks — Plan

## Vision

The first open-source project combining benchmarks + pricing + routing + freshness + portal in one place.
The niche is open: none of the 30+ researched repos does this combination.

## Competitive landscape

| Project               | Stars | What it does                                         | What it lacks                              |
| --------------------- | ----- | ---------------------------------------------------- | ------------------------------------------ |
| chinese-llm-benchmark | 5.7K  | Markdown tables, 359+ models, updates every 1-7 days | No pricing, no routing, no portal, no JSON |
| Wu Long Arena Archive | —     | Daily GitHub Actions, JSON snapshots, REST API       | Arena ELO only, no pricing/routing         |
| DailyBench            | 17    | 4x/day via GH Actions, HELMLite                      | Only 3 models, no pricing, costs $5/day    |
| LiteLLM               | 25K+  | Unified API, auto-updated pricing, routing           | Not a benchmark data product — it's an SDK |
| RouteLLM              | —     | Router model (trains ML)                             | Research project, not a data reference     |
| OpenCompass           | —     | CompassRank visualization                            | Only its own evals, not an aggregator      |
| Artificial Analysis   | —     | Independent measurements + Stirrup harness           | Closed-source, not community-driven        |

**Our gap:** benchmarks + pricing + routing + freshness + portal + auto-update. Nobody combines all of this.

## Architecture

```
data/*.json  (source of truth)
    ↓ generate_md.py
MODEL_BENCHMARKS.md  (generated reference, commit to repo)
    ↓ portal reads JSON
https://<org>.github.io/ai-model-benchmarks/  (GitHub Pages portal)
```

## Data files (v1 DONE)

- [x] `data/models.json` — 104 models, per-score dates
- [x] `data/benchmarks.json` — 35 benchmarks with lifecycle status
- [x] `data/embeddings.json` — 26 embedding models
- [x] `data/routing.json` — KING + FREE + embedding routing + quick matrix
- [x] `data/pricing.json` — cache pricing

## Scripts (v1 DONE)

- [x] `scripts/validate.py` — schema check, duplicates, freshness warnings
- [x] `scripts/fetch_openrouter_prices.py` — daily price sync
- [x] `scripts/generate_md.py` — JSON → Markdown

## Docs (v1 DONE)

- [x] README.md, CHANGELOG.md, LICENSE (MIT)
- [x] docs/METHODOLOGY.md, CONTRIBUTING.md, FRESHNESS.md

## CI/CD (BLOCKED — needs workflow scope PAT)

- [ ] `.github/workflows/daily-prices.yml` — daily OpenRouter API price fetch
- [ ] `.github/workflows/validate.yml` — PR validation on push

## TODO v1.1

### Portal

- [ ] Move benchmark HTML portal to `portal/index.html`
- [ ] Portal reads `data/*.json` directly (fetch from raw GitHub or local)
- [ ] Enable GitHub Pages on repo
- [ ] Cross-link with other portals if applicable

### Auto-update expansion

- [ ] `scripts/fetch_mteb.py` — scrape MTEB leaderboard (HuggingFace API)
- [ ] `scripts/fetch_swebench.py` — scrape SWE-Bench leaderboard
- [ ] `scripts/fetch_arena.py` — fetch LM Arena ELO (following Wu Long pattern)
- [ ] `scripts/canary.py` — daily ping all endpoints, 404 = deprecated
- [ ] History snapshots: `data/history/YYYY-MM-DD/` (following Wu Long pattern)

### Data quality

- [ ] Contamination tracking: add `contamination` field to `benchmarks.json`
  - Schema: `{status: "clean"|"suspected"|"confirmed", method: "...", checked: "date"}`
- [ ] Deprecation tracking: add `deprecated` field to `models.json`
- [ ] Silent update detection: hash response format, alert on change

### REST API (v2, stretch)

- [ ] Simple JSON API via GitHub Pages (static files)
- [ ] Or Cloudflare Worker / Vercel edge function
- [ ] Following Wu Long api pattern

## Decisions

1. **MD primary, JSON backing** — humans read MD, automation reads JSON
2. **GitHub Pages portal** — not HF Spaces (full control)
3. **PR contributions with source link** — not email (better for open-source)
4. **Daily price updates** — sufficient (not 4x/day like DailyBench)
5. **Per-score dates** — our killer feature, nobody else does this
6. **Contamination field** — add as metadata, not as a blocker
