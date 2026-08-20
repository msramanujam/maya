---
gh_issue: 27
gh_type: story
parent: FT-phase-3-litellm-gateway
status: done
phase: 3
spec:
---

# Story: LiteLLM on the gateway profile, serving four aliases

## Problem

Every consumer of a model — LibreChat now, MCP agents and the coding
agent later — currently addresses inference directly. A gateway gives
them one endpoint and one vocabulary, so swapping the model behind an
alias stops being a change to every caller.

## Scope

- LiteLLM container on the `gateway` profile, no published port
- `config/litellm/config.yaml` mapping `general`, `fast`, `coding` and
  `reasoning` to concrete models, mounted read-only
- Per-alias defaults — context, temperature, timeout — held here rather
  than in any caller
- `LITELLM_MASTER_KEY` in `.env`, shape only in `.env.example`
- `scripts/maya` default profile set gains `gateway`

## Note for implementation

LiteLLM reaches Ollama on the host, so like LibreChat it needs
`maya-edge` — the only network with a route off the host — even though
it publishes nothing. `maya-internal` alone has no gateway and
`host.docker.internal` will not resolve. Membership is not permission to
publish; exactly one service publishes and it is Caddy.

## Out of scope

Repointing LibreChat (`ST-librechat-via-litellm`). LiteLLM's database,
virtual keys, usage tracking and budgets — all deferred in
`docs/PHASES.md` until something needs them. vLLM.

## Acceptance criteria

1. `GET /v1/models` against LiteLLM from a container on `maya-internal`
   lists exactly `general`, `fast`, `coding`, `reasoning` — no more.
2. A chat completion through the `general` alias returns a coherent
   answer, and one through `fast` does too.
3. `docker compose ps --format '{{.Names}} {{.Publishers}}'` shows
   LiteLLM publishing nothing.
4. The master key appears in no committed file; `.env.example` carries
   its name and how to generate it.
5. `scripts/check phase3` covers criteria 1 and 3 and passes, and
   phases 1 and 2 still pass in full.
