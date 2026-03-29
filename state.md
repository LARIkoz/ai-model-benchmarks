## Handoff — 2026-03-29

### Phase: v1.0 PASS — ready for portal + public launch

### Status

- Codex R6: **9/10 PASS** (6 review rounds, 2 reviewers)
- Repo: https://github.com/LARIkoz/ai-model-benchmarks (private)
- Validation: 0 errors, 4 warnings (LM Arena staleness — legitimate)

### Сделано

- Created `ai-model-benchmarks` repo from scratch
- 104 models, 43 benchmarks, 26 embeddings — all with per-score dates + source URLs
- routing.json: KING picks (atomic objects), FREE routing, embedding routing, quick matrix
- validate.py: schema check, freshness, source URLs (https://), routing ID refs, benchmark URLs
- fetch_openrouter_prices.py: auto-fetch prices + cache pricing update
- generate_md.py: JSON → Markdown generation
- Docs: README, METHODOLOGY, CONTRIBUTING, FRESHNESS, CHANGELOG, PLAN, LICENSE
- 6 review rounds (Codex + Gemini): 7→7→6/8→8→8/8→9 PASS
- MODEL_BENCHMARKS.md skill updated: FREE tier 27 models, FREE routing, embedding use-cases
- Portal model-benchmarks.html updated in LARIkoz/portals (FREE routing + emb routing sections)
- Gemini CLI skill updated: added `-C` flag gotcha
- Skills synced to claude-setup

### Открытые задачи

- [ ] Portal: move model-benchmarks.html into ai-model-benchmarks repo (GitHub Pages)
- [ ] CI: push workflows via web UI (OAuth scope blocks git push)
- [ ] Public launch: make repo public (needs double confirmation)
- [ ] v2: Model Capability Profiles (per-model spec sheets)
- [ ] Vibe coding portal: principles as TOC (not footer), handoff block dedupe

### Решения

- MD primary + JSON backing (not JSON-only) → Why: chinese-llm-benchmark proves MD works for community
- Per-score dates = killer feature → Why: nobody else does this
- Routing warn not error → Why: legitimate null IDs for combined picks and CLI tools
- Fake URLs → null (honest) → Why: placeholder arxiv IDs undermine trust
- No CI for v1.0 → Why: manual validation sufficient, honest disclosure in docs

### Blockers

- GitHub Actions: OAuth scope needs `workflow` permission. Workaround: push via web UI or PAT
