---
gh_issue: 1
gh_type: epic
parent:
status: proposed
phase: n/a
spec:
---

# Epic: Maya v1 — local self-hosted AI stack

## Problem

There is no local environment that gives a ChatGPT-quality general
interface plus a Codex-style coding agent while running against locally
hosted models. Cloud assistants cannot touch local files, local
documents, or private repositories without sending them off the machine.

## Outcome

A running stack where LibreChat is the interface, LiteLLM is the model
gateway, and MCP supplies filesystem, search, fetch, and browser
capability — with the model itself replaceable without disturbing any of
it. Reachable from the owner's devices over Tailscale, exposed to
nothing else.

## Shape

Seven features, one per build phase, each ending in a stack that can be
started and used on its own:

1. `FT-phase-1-librechat-ollama` — chat with the local model
2. `FT-phase-2-remote-access` — Tailscale, TLS, auth hardening
3. `FT-phase-3-litellm-gateway` — model becomes swappable
4. `FT-phase-4-mcp-filesystem` — tool layer and scoped file access
5. `FT-phase-5-search-fetch` — current information
6. `FT-phase-6-browser` — JS-heavy and interactive pages
7. `FT-phase-7-coding-agent` — Codex-style repo work, model specialization

## Done when

All seven features are done, `scripts/check` passes in full from a cold
start, and the stack is usable from a phone off the local network.
