## Handoff — 2026-03-29 (session 3 DEEP)

### Phase: v1.1 shipped. Capabilities + tooltips + benchmarks + PRs. Deep research running for 13 empty categories.

### ⚠️ Running / stopped

- Deep research agent completed (13 empty benchmark categories) — results NOT yet applied
- 3 awesome-list PRs submitted, awaiting merge
- PR #4 (aishwaryanr) fork still pending on GitHub
- Growth strategy research completed → saved to memory

---

## 1. WHAT WAS DONE (session 3)

### 1.1 GitHub Profile

- Cleaned: removed bio, blog, Discord. Kept name + Twitter

### 1.2 SEO & Discovery

- Removed noindex/nofollow from portal (was blocking ALL search engines)
- Added Schema.org JSON-LD, OG/Twitter meta, canonical
- Added llms.txt (step-by-step guide for AI agents)
- Added llms-full.txt (auto-generated daily, complete routing + 119 models)
- Added CITATION.cff, robots.txt, sitemap.xml (with data URLs)
- Added data/README.md (full JSON schema docs)

### 1.3 Capability Sync

- New script: sync_capabilities.py (daily CI from OpenRouter)
- Fixed 27 broken openrouter_ids (dots vs dashes)
- 97/119 models have structured capabilities
- Capability filter buttons in portal (Vision, Tools, Reasoning, Structured)

### 1.4 Manual Capabilities

- manual_capabilities.json: 15 top models (knowledge_cutoff, caching, effective_context)
- Staleness tracking: validate.py warns >90d

### 1.5 Score Tooltips

- Every score in mega-table clickable → popup with benchmark desc + date + source
- KING section bench names clickable with description + leaderboard link
- BENCH_META: 39 entries covering all benchmarks in portal

### 1.6 Benchmark Audit

- All 48→55 benchmarks have description + URL (15 missing URLs filled, 7 new benchmarks added)
- Affiliation tracking: creator, risk level (high/medium/low) for 14 benchmarks
- LIVE_BENCHMARKS now generated from benchmarks.json (was hardcoded)
- Dead benchmarks rendered as cards (was plain text list)
- 9 routing categories assigned formal benchmarks (22→13 empty)
- "practical" → "expert eval" for categories without formal benchmark

### 1.7 URL Audit

- canary.py found 23 broken URLs
- Fixed 12 benchmark URLs + 47 model source URLs = 59 total
- Root causes: domain changes, repo moves, anti-bot 403s

### 1.8 Portal Rebuild

- All tables unified to bench-table style
- Portal regenerated from data/\*.json (no more hardcoded data)
- CI: sync_capabilities → fetch_prices → generate_portal → validate → commit

### 1.9 Review Cycles (5 rounds)

- R1: 15 issues (2 critical: XSS, CI no validation)
- R2: docs contradictions
- R3: column sort typo
- R4: validation enforcement (warn→error)
- R5: 9/10 PASS

### 1.10 Auto-scrapers

- fetch_lmarena.py, fetch_swebench.py, canary.py

### 1.11 README & Positioning

- Agent-first: "structured JSON for agents, pipelines, developers"
- Russian README (README_ru.md)
- "For agents and pipelines" section with JSON example + Python snippet

### 1.12 PR Campaign

- 3 awesome-list PRs submitted:
  - Hannibal046/Awesome-LLM #409 (LLM Leaderboard section)
  - Shubhamsaboo/awesome-llm-apps #653 (LLM Optimization Tools)
  - steven2358/awesome-generative-ai #506 (Leaderboards)
- v1.1 GitHub Release created
- Growth strategy saved to memory (1000 stars in 12-16 weeks plan)

### 1.13 MODEL_BENCHMARKS.md Skill

- Now references repo as source of truth
- Sync protocol: generate_md.py → skill
- Pipeline-specific routing stays in skill (not public)

## 2. BLOCKERS

- 13 routing categories still without formal benchmark (deep research completed, results not applied)
- PR #4 fork pending on GitHub (aishwaryanr)

## 3. DECISIONS + REJECTED

- Portal tables: unified bench-table (not separate styles per section)
- Capabilities: two-layer (auto OpenRouter + manual top-15) vs one layer
- Score tooltips: click popup (like immune portal PMID) vs hover tooltip
- "practical" label → "expert eval" (honest about no benchmark)
- MODEL_BENCHMARKS.md: repo = source of truth, skill = snapshot + pipeline routing
- Growth: HN Show HN = highest ROI (300-400 stars), awesome-lists = long-tail

## 4. NEXT SESSION PLAN

1. Apply deep research results for 13 empty benchmark categories
2. Check awesome-list PR merge status
3. Submit PR #4 (aishwaryanr) when fork ready
4. Prepare HN "Show HN" post (Tuesday Apr 1, 8am PT)
5. Full portal audit (5 review cycles on content quality)
6. Update MODEL_BENCHMARKS.md skill from repo data

## 5. DATA STATE

- 119 models, 55 benchmarks, 26 embeddings
- 97/119 capability profiles (auto)
- 15/119 manual capabilities
- 48/55 benchmarks with URLs (7 new, need URLs verified)
- 14/55 with affiliation tracking

## 6. FILES CHANGED

| File                                                | Change                                                  |
| --------------------------------------------------- | ------------------------------------------------------- |
| index.html                                          | Portal rebuild, tooltips, caps filter, bench cards      |
| scripts/sync_capabilities.py                        | New: capability sync                                    |
| scripts/generate_portal.py                          | Score objects, LIVE_BENCHMARKS, benchKey, llms-full.txt |
| scripts/validate.py                                 | Enforce source URLs, routing IDs, score type guard      |
| scripts/fetch_lmarena.py                            | New: LM Arena scraper                                   |
| scripts/fetch_swebench.py                           | New: SWE-Bench scraper                                  |
| scripts/canary.py                                   | New: URL health check                                   |
| .github/workflows/daily-prices.yml                  | +sync_capabilities, +validate, +generate_portal, +dedup |
| data/models.json                                    | Capabilities, fixed openrouter_ids, fixed source URLs   |
| data/benchmarks.json                                | 48→55, descriptions, URLs, affiliations                 |
| data/routing.json                                   | 9 bench assignments                                     |
| data/manual_capabilities.json                       | New: 15 top models                                      |
| data/README.md                                      | New: JSON schema docs                                   |
| README.md                                           | JTBD, agent-first, Python example, RU link              |
| README_ru.md                                        | New: Russian translation                                |
| llms.txt                                            | Agent guide rewrite                                     |
| llms-full.txt                                       | New: auto-generated daily                               |
| CITATION.cff                                        | New                                                     |
| robots.txt, sitemap.xml                             | New                                                     |
| docs/FRESHNESS.md                                   | CI = active                                             |
| docs/CONTRIBUTING.md                                | CI = active                                             |
| docs/METHODOLOGY.md                                 | daily = automated                                       |
| PLAN.md                                             | v1.1 complete, v1.2 roadmap                             |
| ~/.claude/skills/openrouter-api/MODEL_BENCHMARKS.md | Repo = source of truth                                  |
