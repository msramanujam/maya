---
gh_issue: 7
gh_type: feature
parent: EP-maya-v1
status: ready
phase: 6
spec:
---

# Feature: Phase 6 — Interactive browser

## Problem

Search and fetch fail on JavaScript-rendered pages, multi-step
navigation, forms, and authenticated applications. A real browser covers
those — and will be over-used for everything else unless it is
deliberately positioned as the last resort.

## Scope

- Playwright MCP (profile `browser`), headless, on `maya-internal`
- No host filesystem mounts; session state in its own volume
- Tool description and system prompt steering the model to search/fetch
  first

## Out of scope

Credential storage for authenticated sites. Headful/visible browsing.

## Acceptance criteria

1. A JavaScript-rendered page that `web_fetch` returns empty for is
   retrieved correctly through the browser tool.
2. A two-step navigation (enter a term, follow a result) completes and
   returns content from the second page.
3. For a plain article URL, the model still chooses `web_fetch`, not the
   browser — verified by inspecting which tool it called.
4. The Playwright container has no host mounts and no published port.
5. `scripts/check phase6` passes and covers criterion 4.
