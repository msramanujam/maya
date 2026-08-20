---
gh_issue: 6
gh_type: feature
parent: EP-maya-v1
status: ready
phase: 5
spec:
---

# Feature: Phase 5 — Internet search and page fetch

## Problem

The model's knowledge is frozen at training time and it cannot read a
page. It needs discovery and retrieval as two distinct capabilities —
merging them makes the model fetch ten pages when it needed one search.

## Scope

- SearXNG (profile `web`) on `maya-internal`, no published port, JSON
  output enabled
- `web_search(query)` — discovery: titles, URLs, snippets
- `web_fetch(url)` — retrieval: extracted article text, boilerplate
  stripped, response size capped

## Out of scope

Browser automation (Phase 6). Caching or a search index of results.

## Acceptance criteria

1. A question that training data cannot answer is answered correctly,
   with the model visibly calling `web_search`, choosing a URL, calling
   `web_fetch`, and citing it.
2. A `web_fetch` response contains no HTML tags and no navigation
   boilerplate.
3. A `web_fetch` of a very large page returns a truncated response
   within the configured cap rather than flooding the context.
4. SearXNG has no published host port and returns JSON on its internal
   address.
5. `scripts/check phase5` passes and covers criteria 2 and 4.
