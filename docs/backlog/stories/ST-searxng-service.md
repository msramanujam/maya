---
gh_issue: 45
gh_type: story
parent: FT-phase-5-search-fetch
status: in-progress
phase: 5
spec:
---

# Story: SearXNG on the web profile

## Problem

The model's knowledge ends at training time. Discovery needs a search
engine that answers to the stack rather than to a vendor, and that does
not require an API key.

## Scope

- SearXNG on the `web` profile, `maya-internal` plus `maya-edge` (it
  must reach the internet), no published port
- JSON output enabled — off by default in SearXNG, and the whole point
  here
- Settings and a generated secret in `config/searxng/`, secret from
  `.env`
- `scripts/check phase5` asserts JSON search works internally and that
  nothing is published

## Out of scope

The MCP tools themselves (`ST-web-search-fetch-tools`). Result caching.

## Acceptance criteria

1. A JSON search from a container on `maya-internal` returns results
   with titles and URLs.
2. SearXNG publishes no host port.
3. The instance secret is in `.env`, not in any committed file.
4. `scripts/check phase5` covers criteria 1 and 2 and passes.
