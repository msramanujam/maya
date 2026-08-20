---
gh_issue: 46
gh_type: story
parent: FT-phase-5-search-fetch
status: ready
phase: 5
spec:
---

# Story: web_search and web_fetch as separate tools

## Problem

Discovery and retrieval are different jobs. A single tool that searches
and then fetches everything it found makes the model read ten pages when
it needed one — and floods the context doing it.

## Scope

- `web_search(query)` — titles, URLs, snippets, from SearXNG
- `web_fetch(url)` — article text with boilerplate stripped, capped
- Both in an MCP server of ours, attached to the Maya agent
- `scripts/check phase5` asserts extraction quality and the cap

## Note on the agent

Tools reach the model only through the agent (bug #43). Adding a server
is therefore not enough — the agent's tool list has to include it, and
that is a UI action.

## Out of scope

Browser automation (Phase 6). Caching.

## Acceptance criteria

1. `web_search` returns titles, URLs and snippets for a query.
2. `web_fetch` of an article returns readable text containing no HTML
   tags and no navigation boilerplate.
3. `web_fetch` of a very large page returns a truncated response within
   the cap rather than flooding the context.
4. A question training data cannot answer is answered correctly, with
   the model visibly searching, choosing a URL, fetching it, and citing
   it.
5. `scripts/check phase5` covers criteria 2 and 3 and passes.
