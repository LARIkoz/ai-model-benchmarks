# Freshness

## Why freshness matters for LLM benchmarks

LLM benchmark data goes stale faster than almost any other technical domain. Three forces drive this:

**1. Model updates without version bumps.** Providers routinely update models behind the same API identifier. A score measured in January may describe a different model than what you're calling in April. OpenRouter tracks some of this, but not all.

**2. Leaderboard retroactive corrections.** Benchmarks like SWE-Bench periodically re-run all evaluations. A model that scored 72% in November may show 74% in March — same model, better measurement methodology. If you're working from cached data, you'll see the wrong score.

**3. Competitive landscape shifts fast.** A "budget king" model at $0.20/M in February may have a better competitor at $0.15/M by March. Routing decisions based on stale data lead to paying more for worse results.

The practical consequence: a benchmark table with no dates is worthless for decision-making. You can't tell if you're reading current data or a six-month-old snapshot.

## What goes stale and what doesn't

### Goes stale quickly (weeks to months)

- **Prices** — providers change pricing without announcement. MiniMax changed prices 3 times in one month. Always fetch fresh from OpenRouter.
- **New model availability** — new models appear on OpenRouter weekly. A routing recommendation may have a better option you haven't seen.
- **LMArena ELO** — human preference scores are volatile. Rank changes with new vote accumulation continuously.
- **LiveBench** — designed to refresh monthly. Stale by definition after 30 days.

### Goes stale moderately (months)

- **SWE-Bench scores** — leaderboard updates roughly monthly. Frontier ceiling has moved significantly over 6 months (from ~65% to ~81% in 2025-2026).
- **GPQA, HLE** — more stable, but new models appear and models get re-evaluated.
- **ARC-AGI-2** — quarterly-ish updates.

### Relatively stable (6-12 months)

- **BFCL** — function calling patterns don't shift as fast as general capability.
- **Benchmark methodology** — which benchmarks are active vs dead changes slowly.
- **Tier classification** — a frontier model doesn't drop to budget without a price cut announcement.

### Never stale

- **Dead benchmarks** — MMLU is dead. It will stay dead.
- **Benchmark definitions** — what SWE-Bench Verified measures doesn't change retroactively.
- **Provider cache mechanics** — Anthropic 90% cache discount is contractual.

## Staleness indicators

In `data/models.json`, each score has a `measured` field. Warning thresholds:

| Volatility                  | Warning threshold | Action                            |
| --------------------------- | ----------------- | --------------------------------- |
| `high` (LMArena, LiveBench) | >14 days          | Treat as approximate              |
| `medium` (ARC-AGI-2, HLE)   | >30 days          | Verify before important decisions |
| `low` (SWE-Bench, GPQA)     | >60 days          | Review during weekly update pass  |

Prices in `data/pricing.json` have a top-level `updated` date. If that's >7 days ago, run `scripts/fetch_openrouter_prices.py` to refresh.

## Auto-update pipeline (planned)

The GitHub Action in `.github/workflows/daily-prices.yml` is not yet deployed. Until then, run `scripts/fetch_openrouter_prices.py` manually to refresh pricing. When deployed, it will:

1. Run at 06:00 UTC daily
2. Call `scripts/fetch_openrouter_prices.py`
3. Fetch `https://openrouter.ai/api/v1/models`
4. Compare against current `data/pricing.json`
5. If prices changed: update file, commit, push
6. If new models detected: open a GitHub issue for manual review

Score updates are intentionally manual — automated score ingestion would silently accept bad data from contaminated leaderboards. A human reviews each score update.

## Handling stale data in your code

If you're using this data in a pipeline:

```python
import json
from datetime import datetime, timedelta

with open("data/models.json") as f:
    models = json.load(f)

# Warn if any score is older than 30 days
threshold = datetime.now() - timedelta(days=30)
for model in models:
    for bench_id, score in model.get("scores", {}).items():
        measured = score.get("measured", "")
        if measured and datetime.strptime(measured[:7], "%Y-%m") < threshold:
            print(f"STALE: {model['id']}.{bench_id} measured {measured}")
```

The `scripts/validate.py` script does this check automatically and prints warnings.
