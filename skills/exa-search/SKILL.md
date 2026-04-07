---
name: exa-search
description: >
  Use this skill whenever you need to search the web for up-to-date information, documentation,
  code examples, news, research papers, or any content that may not be in your training data.
  Trigger on phrases like "search for", "look up", "find info about", "web search", "搜索", "查一下",
  "查找", "搜一搜", "找一下", "最新", "看看网上", or when the user asks about recent events,
  current library versions, API docs, or anything requiring live web data. Always prefer this
  skill over guessing when real-world, up-to-date information is needed.
---

# Exa Web Search

Use this skill to search the web via the [Exa API](https://exa.ai) using `curl`. No Node.js or Python needed — just shell.

## Quick Start

```bash
curl -s -X POST 'https://api.exa.ai/search' \
  -H 'x-api-key: 69b2e0ee-f92a-48ab-9233-cc8a750a1e50' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "YOUR QUERY HERE",
    "type": "auto",
    "num_results": 10,
    "contents": {
      "highlights": {
        "max_characters": 4000
      }
    }
  }'
```

## Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `type` | `"auto"` | Default. Use `"fast"` for speed, `"deep"` for thorough research |
| `num_results` | `5–10` | Reduce for faster responses |
| `contents.highlights.max_characters` | `4000` | Key excerpts. Switch to `"text"` for full page content |

## Common Search Patterns

### General web search (default)

```bash
curl -s -X POST 'https://api.exa.ai/search' \
  -H 'x-api-key: 69b2e0ee-f92a-48ab-9233-cc8a750a1e50' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Next.js 15 app router data fetching",
    "type": "auto",
    "num_results": 5,
    "contents": {
      "highlights": { "max_characters": 4000 }
    }
  }'
```

### Full page text (for code/docs you need in full)

```bash
curl -s -X POST 'https://api.exa.ai/search' \
  -H 'x-api-key: 69b2e0ee-f92a-48ab-9233-cc8a750a1e50' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "Prisma schema relations one-to-many",
    "type": "auto",
    "num_results": 3,
    "contents": {
      "text": { "max_characters": 20000 }
    }
  }'
```

### News / recent events

```bash
curl -s -X POST 'https://api.exa.ai/search' \
  -H 'x-api-key: 69b2e0ee-f92a-48ab-9233-cc8a750a1e50' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "OpenAI GPT-5 release",
    "type": "auto",
    "category": "news",
    "num_results": 5,
    "contents": {
      "highlights": { "max_characters": 4000 }
    }
  }'
```

### Deep research (thorough, slower)

```bash
curl -s -X POST 'https://api.exa.ai/search' \
  -H 'x-api-key: 69b2e0ee-f92a-48ab-9233-cc8a750a1e50' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "vector database comparison 2025 performance benchmarks",
    "type": "deep",
    "num_results": 10,
    "contents": {
      "highlights": { "max_characters": 4000 }
    }
  }'
```

### Fetch content from known URLs

```bash
curl -s -X POST 'https://api.exa.ai/contents' \
  -H 'x-api-key: 69b2e0ee-f92a-48ab-9233-cc8a750a1e50' \
  -H 'Content-Type: application/json' \
  -d '{
    "urls": ["https://docs.example.com/api"],
    "text": { "max_characters": 20000 }
  }'
```

## Reading Results

The response is JSON. Key fields per result:

```
.results[].title       — page title
.results[].url         — source URL
.results[].highlights  — relevant excerpts (array of strings)
.results[].text        — full text (only if you requested "text" contents)
.results[].publishedDate — ISO date string
```

Pretty-print with `jq`:

```bash
curl -s ... | jq '.results[] | {title, url, highlights}'
```

Extract just titles and URLs:

```bash
curl -s ... | jq -r '.results[] | "\(.title)\n\(.url)\n"'
```

## Domain Filtering (optional)

Focus on authoritative sources when needed:

```json
{
  "query": "...",
  "includeDomains": ["github.com", "docs.python.org"],
  "excludeDomains": ["pinterest.com", "quora.com"]
}
```

## Environment Variable (recommended)

To avoid hardcoding the key in commands:

```bash
export EXA_API_KEY="69b2e0ee-f92a-48ab-9233-cc8a750a1e50"

curl -s -X POST 'https://api.exa.ai/search' \
  -H "x-api-key: $EXA_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{ "query": "...", "type": "auto", "num_results": 5, "contents": {"highlights": {"max_characters": 4000}} }'
```

## Common Mistakes to Avoid

- ❌ `"livecrawl": "preferred"` → deprecated, use `"maxAgeHours": 0` instead
- ❌ `"useAutoprompt": true` → deprecated, remove it
- ❌ `"highlights"` at top level of `/search` → must be inside `"contents": { ... }`
- ❌ `"includeUrls"` → doesn't exist, use `"includeDomains"`
- ❌ Both `"text"` and `"highlights"` in same request → pick one
