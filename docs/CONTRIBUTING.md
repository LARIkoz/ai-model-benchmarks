# Contributing

## How to submit new scores

1. Fork the repo and create a branch: `scores/model-name-benchmark`
2. Edit `data/models.json` — add or update the score in the model's `scores` object
3. Every score **must** have:
   - `value` — the numeric score
   - `measured` — date in `YYYY-MM` or `YYYY-MM-DD` format
   - `source` — URL to the leaderboard or paper where the score appears
4. Run `python scripts/validate.py` — fix any errors before submitting
5. Open a PR with a title like `Update: Gemini 3.1 Pro GPQA score (March 2026)`

### Adding a new model

If the model doesn't exist in `data/models.json`:

1. Pick the correct tier based on input pricing:
   - `tier: 1` — >$1/M input
   - `tier: 2` — $0.20-$1/M input
   - `tier: 3` — <$0.20/M input
   - `tier: 0` — free (set `channel` field)
2. Fill in all required fields: `id`, `name`, `provider`, `tier`, `pricing`, `context_length`, `openrouter_id`
3. Add only scores you have sources for — omit the rest
4. Run validate.py

### Required fields for pricing

```json
{
  "input": 5.0,
  "output": 25.0,
  "unit": "per_million_tokens",
  "source": "openrouter",
  "updated": "2026-03-28"
}
```

## How to report errors

Open an issue with:

- Which model/benchmark is wrong
- What the correct value is
- Source URL proving the correct value

Include the date you checked — scores on leaderboards change retroactively.

## Data format requirements

- JSON must be valid (run `python -m json.tool data/models.json` to check)
- IDs must be lowercase, hyphen-separated: `claude-opus-4-6` not `ClaudeOpus46`
- Benchmark IDs must match entries in `data/benchmarks.json`
- No self-reported scores — source must be an independent benchmark
- No scores from provider blog posts unless they link to a public leaderboard

## Review process

1. Automated validation runs on every PR via `.github/workflows/validate.yml` — run `python scripts/validate.py` locally before opening a PR to catch issues early
2. A maintainer checks the source URL is valid and points to the claimed score
3. If the score differs from what the source shows: PR is rejected
4. If score is marked `notes: "estimated"`, it's accepted only if clearly labeled and plausible

## Benchmark additions

To add a new benchmark to tracking:

1. Add an entry to `data/benchmarks.json`
2. Required fields: `id`, `name`, `category`, `what_it_measures`, `saturation`, `contamination_risk`, `volatility`, `lifecycle`
3. Add scores for at least 5 models using the new benchmark ID
4. Open PR with context on why this benchmark is worth tracking

## Code contributions

For scripts (`scripts/`):

- Python 3.10+ required
- No external dependencies beyond `requests` and `json`
- Keep it simple — these are utility scripts, not production code
