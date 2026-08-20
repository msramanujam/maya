---
gh_issue: 49
gh_type: story
parent: FT-phase-6-browser
status: ready
phase: 6
spec:
---

# Story: Playwright browser as the last resort

## Problem

Search and fetch fail on JavaScript-rendered pages, multi-step
navigation and forms. A real browser covers those — and will be reached
for constantly unless it is positioned as the expensive option it is.

## Scope

- Playwright MCP on the `browser` profile, headless, `maya-internal`
  plus `maya-edge`
- No host filesystem mounts; profile and session state in its own volume
- Tool descriptions that steer the model to `web_fetch` first and say
  plainly when the browser is warranted
- `scripts/check phase6` asserts no host mounts and no published port

## Note on the agent

Tools reach the model only through the agent (bug #43). The agent's tool
list has to include the browser server.

## Out of scope

Credential storage for authenticated sites. Headful browsing.

## Acceptance criteria

1. A JavaScript-rendered page that `web_fetch` returns nothing useful
   for is retrieved correctly through the browser tool.
2. A two-step navigation — enter a term, follow a result — completes and
   returns content from the second page.
3. For a plain article URL, the model still chooses `web_fetch`, not the
   browser, verified by inspecting which tool it called.
4. The browser container has no host mounts and no published port.
5. `scripts/check phase6` covers criterion 4 and passes.
