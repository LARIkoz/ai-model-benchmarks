# Changelog

## [1.0.0] — 2026-03-29

### Initial release

- **70+ chat/completion models** across Tier 1 (frontier), Tier 2 (mid-range), Tier 3 (budget), and FREE tiers
- **25+ embedding models** with MTEB overall and retrieval scores
- **33 benchmark categories** across coding, reasoning, tool calling, content, multimodal, domain, web scraping, reverse engineering, medical, and embeddings
- **Per-score freshness dates** — every benchmark value tracks when it was measured and from which source
- **Task routing (KING picks)** — best model per category at Quality, Budget, and Free price points
- **FREE routing table** — which free model for which task (OpenRouter free + CLI tools)
- **Embedding routing** — use-case decision tree for embedding model selection
- **Quick Decision Matrix** — one-line lookups: "I need X → use Y"
- **Cache pricing table** — per-provider cache discounts (Anthropic 90%, Google 90%, OpenAI 75-90%, etc.)
- **Benchmark lifecycle registry** — active vs saturated vs dead benchmarks with contamination risk ratings
- **GitHub Actions** — daily price updates, PR validation
- **Scripts** — fetch prices, validate schema, generate markdown
