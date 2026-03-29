# AI Model Benchmarks 2026 — Бенчмарки AI-моделей

> **Структурированные, машиночитаемые данные об AI-моделях для агентов, пайплайнов и разработчиков. Бенчмарки, цены, возможности, маршрутизация — обновляется автоматически каждый день.**

[![Daily Prices](https://github.com/LARIkoz/ai-model-benchmarks/actions/workflows/daily-prices.yml/badge.svg)](https://github.com/LARIkoz/ai-model-benchmarks/actions/workflows/daily-prices.yml)
[![Validation](https://github.com/LARIkoz/ai-model-benchmarks/actions/workflows/validate.yml/badge.svg)](https://github.com/LARIkoz/ai-model-benchmarks/actions/workflows/validate.yml)
[![Models](https://img.shields.io/badge/models-119-green)](data/models.json)
[![Benchmarks](https://img.shields.io/badge/benchmarks-48-blue)](data/benchmarks.json)
[![Embeddings](https://img.shields.io/badge/embeddings-26-purple)](data/embeddings.json)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

[🇬🇧 English version](README.md)

**119 моделей · 48 бенчмарков · 26 эмбеддингов · 97 профилей возможностей · обновляется автоматически каждый день**

[Открыть портал](https://larikoz.github.io/ai-model-benchmarks/) · [Посмотреть данные](data/) · [Методология](docs/METHODOLOGY.md)

## Для кого это

- **AI-агенты и пайплайны** — структурированный JSON для автоматической маршрутизации моделей, оптимизации затрат и подбора по возможностям
- **Разработчики** — "какая модель подойдёт для моего RAG / code review / классификации при моём бюджете?"
- **AI-инструменты** (LangChain, LiteLLM и др.) — готовые к интеграции таблицы маршрутизации, флаги возможностей и данные о ценах

## Проблема

Таблицы бенчмарков устаревают в день публикации. Цены меняются каждую неделю. Новые модели выходят каждый месяц. Возможности нигде не отслеживаются в структурированном виде. Большинство сравнений показывают один балл на модель без даты, без ссылки на источник — и нет способа узнать, актуальны ли цифры.

## Что это решает

- **Дата актуальности для каждого балла** — каждое значение бенчмарка имеет дату `measured` и ссылку `source`. Любую цифру можно проверить самостоятельно
- **Профили возможностей** — vision, tool calling, reasoning, structured output, max tokens — синхронизируются ежедневно через OpenRouter API (97/119 моделей)
- **Автообновление цен** — загружаются ежедневно из OpenRouter API через GitHub Actions ([посмотреть workflow](.github/workflows/daily-prices.yml))
- **Маршрутизация по задачам** — не просто "лучшая модель", а "лучшая модель для конкретной задачи при вашем бюджете" (25 категорий задач, 4 уровня: quality, budget, free)
- **Жизненный цикл бенчмарков** — какие бенчмарки ещё разделяют модели (активные) и какие стали шумом (насыщенные/мёртвые/загрязнённые)
- **Без самоотчётных баллов** — все данные из [16 независимых источников](docs/METHODOLOGY.md) (Scale AI SEAL, Artificial Analysis, BFCL, LM Arena, LiveBench...)

## Почему этим данным можно доверять

Каждый балл проверяем:

1. **URL источника** — переход на оригинальный лидерборд или статью
2. **Дата замера** — точно известно, когда балл был собран
3. **Автоматическая валидация** — `scripts/validate.py` проверяет схему, выявляет отсутствующие источники, помечает устаревшие баллы
4. **История git** — каждое изменение отслеживается, каждое обновление имеет коммит
5. **CI-пайплайн** — ежедневное обновление цен + валидация PR через GitHub Actions

## Быстрый старт

- **Просмотр данных:** `data/models.json`, `data/embeddings.json`, `data/benchmarks.json`
- **Выбор модели:** `data/routing.json` — лучшие варианты по категориям, матрица быстрых решений
- **Методология:** `docs/METHODOLOGY.md`

## Для агентов и пайплайнов

Каждая модель в `data/models.json` содержит структурированные поля, которые можно сразу использовать в коде:

```json
{
  "id": "claude-opus-4-6",
  "context_length": 1000000,
  "max_output_tokens": 128000,
  "pricing": { "input": 5.0, "output": 25.0 },
  "capabilities": {
    "vision": true,
    "tool_calling": true,
    "reasoning": true,
    "structured_output": true,
    "json_mode": true
  },
  "scores": {
    "swe_v": { "value": 80.8, "measured": "2026-03", "source": "https://..." }
  }
}
```

Используйте `data/routing.json` → `quick_matrix` для автоматического выбора модели:

```python
# Пример: выбрать лучшую модель для задачи
routing = json.load(open("data/routing.json"))
for entry in routing["quick_matrix"]:
    if entry["task"] == "Write/review code":
        print(entry["use"], entry["backup"], entry["free"])
```

## Структура данных

```
data/
  models.json              — 119 моделей: баллы, цены, возможности, метаданные
  manual_capabilities.json — 15 топ-моделей: дата знаний, кэширование, эффективный контекст
  embeddings.json          — 26 моделей эмбеддингов с баллами MTEB и маршрутизацией по задачам
  benchmarks.json          — 48 бенчмарков со статусом жизненного цикла
  routing.json             — Маршрутизация задач: лучшие варианты, FREE-маршрутизация, матрица решений
  pricing.json             — Цены кэширования по провайдерам (обновляется ежедневно)

scripts/
  sync_capabilities.py         — Ежедневно: загрузка возможностей из OpenRouter API
  fetch_openrouter_prices.py   — Ежедневно: загрузка цен из OpenRouter API
  generate_portal.py           — Ежедневно: пересборка портала HTML из JSON
  validate.py                  — CI: валидация схемы, URL источников, актуальность, ссылки маршрутизации
  generate_md.py               — Генерация markdown-таблиц из JSON-данных
```

## Как использовать

### Найти подходящую модель для задачи

Смотрите `data/routing.json`, раздел `quick_matrix`. Примеры записей:

| Задача                     | Использовать        | Запасной        | Бесплатный        |
| -------------------------- | ------------------- | --------------- | ----------------- |
| Написать/проверить код     | Claude Sonnet 4.6   | MiniMax M2.5    | MiniMax M2.5 FREE |
| Сложные рассуждения        | Claude Opus 4.6     | Gemini 3.1 Pro  | Gemini CLI        |
| Пакетная классификация     | Qwen CLI            | MiniMax M2.5    | Оба бесплатно     |
| Длинный документ (>200K)   | Gemini 3.1 Pro (1M) | MiniMax 01 (1M) | Gemini CLI (2M)   |
| Соответствие стандартам ЕС | Mistral Large       | Mistral Medium  | —                 |

Полная таблица маршрутизации: `data/routing.json` → `quick_matrix` (25 категорий задач).

```bash
# Сгенерировать полный markdown-справочник
python scripts/generate_md.py > MODEL_BENCHMARKS.md
```

### Следить за актуальностью цен

Цены обновляются запуском скрипта:

```bash
python scripts/fetch_openrouter_prices.py
```

### Проверить целостность данных

```bash
python scripts/validate.py
```

## Как внести вклад

Pull request'ы приветствуются. Требования:

1. **Обязательна ссылка на источник** — каждый балл должен иметь URL, ведущий на лидерборд или статью
2. **Обязательна дата замера** — минимум формат `YYYY-MM`, предпочтительно `YYYY-MM-DD`
3. **Без самоотчётных баллов** — баллы должны быть из независимых бенчмарков (не из блога самого провайдера)
4. Запустите `python scripts/validate.py` перед отправкой — PR должен пройти валидацию

Полные инструкции: `docs/CONTRIBUTING.md`.

## Расписание обновлений

- **Ежедневно (06:00 UTC):** Цены загружаются из OpenRouter API через [GitHub Action](.github/workflows/daily-prices.yml)
- **При каждом PR:** Валидация схемы через [GitHub Action](.github/workflows/validate.yml)
- **Еженедельно (вручную):** Баллы бенчмарков сверяются с лидербордами, даты актуальности обновляются

## Источники

Баллы взяты из: LM Council, Artificial Analysis, Scale AI SEAL, BFCL V4, BenchLM.ai, RankSaga/Kaggle, Z.ai, MiniMax, OpenRouter official, AIModelsMap, Awesome Agents, MedQA, VALS.ai, FDA, PricePerToken, MTEB Leaderboard, Prem.ai, Mixpeek.

Полный список источников и иерархия доверия: `docs/METHODOLOGY.md`.

## Лицензия

MIT — см. [LICENSE](LICENSE)
