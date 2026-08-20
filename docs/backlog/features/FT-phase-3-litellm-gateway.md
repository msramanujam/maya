---
gh_issue: 4
gh_type: feature
parent: EP-maya-v1
status: proposed
phase: 3
spec:
---

# Feature: Phase 3 — LiteLLM gateway and logical model names

## Problem

LibreChat is wired directly to one inference server. Every later
component — MCP agents, the coding agent — would inherit that coupling.
A gateway makes the model a swappable detail and gives everything one
endpoint to point at.

## Scope

- LiteLLM container (profile `gateway`) on `maya-internal`, no published
  port
- `config/litellm/config.yaml` mapping aliases to concrete models:
  `general`, `fast`, `coding`, `reasoning`
- Per-alias defaults (context, temperature, timeout) held in LiteLLM,
  not in LibreChat
- Master key in `.env`
- LibreChat repointed at `http://litellm:4000/v1`

## Out of scope

LiteLLM's own database, virtual keys, usage tracking, budgets — deferred
until something actually needs them (see docs/PHASES.md). vLLM as a
second backend.

## Acceptance criteria

1. `curl` to LiteLLM `/v1/models` from inside `maya-internal` lists
   exactly the four aliases.
2. A chat in the UI against `general` returns a coherent answer.
3. Repointing `fast` at a different pulled model and restarting only the
   LiteLLM container changes the UI's behavior with **zero edits to
   LibreChat config** — this swap is the feature.
4. `grep -r` across the repo finds no concrete model name outside
   `config/litellm/config.yaml`.
5. LiteLLM has no published host port.
6. `scripts/check phase3` passes and covers criteria 1, 4, 5.
