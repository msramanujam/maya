---
gh_issue: 2
gh_type: feature
parent: EP-maya-v1
status: done
phase: 1
spec:
---

# Feature: Phase 1 — LibreChat + Ollama

## Problem

Nothing exists yet. The first useful thing is a persistent, multi-turn
chat interface talking to the model already running on this machine.

## Architecture

    Browser -> LibreChat (container) -> host Ollama -> Qwen3.8-27B

Ollama stays on the host: Docker on macOS has no GPU passthrough, so a
containerized Ollama loses Metal.

## Scope

- Repo scaffold: `compose.yaml` (profile `core`), `.env.example`,
  `scripts/maya` wrapper, `.gitignore` entries for state
- Ollama host bind changed so containers can reach it
- MongoDB for conversation persistence, no published port
- LibreChat as a custom OpenAI-compatible endpoint against Ollama
- Deliberate context-window setting, with its memory cost recorded

## Out of scope

LiteLLM, MCP, search, browser, coding agent, TLS, remote access. Phase 1
publishes on `127.0.0.1` only.

## Acceptance criteria

1. `curl http://localhost:11434/api/tags` from the host lists both models.
2. `docker compose exec librechat curl -fsS http://host.docker.internal:11434/v1/models`
   returns a non-empty model list — this is the check that catches the
   loopback-bind problem.
3. The LibreChat UI at `http://127.0.0.1:3080` lists the Ollama models in
   its model picker without manual entry.
4. A two-message conversation where the second message references the
   first gets a coherent answer.
5. After `docker compose down` and up, that conversation is still listed
   and readable.
6. `docker compose ps --format '{{.Publishers}}'` shows no port bound to
   `0.0.0.0`.
7. `scripts/check phase1` passes and covers criteria 1, 2, 3, 6.

## Stories

- `ST-ollama-host-bind`
- `ST-compose-core-librechat-mongo`
- `ST-librechat-ollama-endpoint`
- `ST-context-window-and-persistence`
