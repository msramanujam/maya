---
gh_issue: 11
gh_type: story
parent: FT-phase-1-librechat-ollama
status: done
phase: 1
spec:
---

# Story: Wire LibreChat to Ollama as a custom endpoint

## Problem

LibreChat is running but has no model to talk to. It needs an
OpenAI-compatible endpoint pointed at the host's Ollama, with models
discovered rather than hand-listed — and configured so that the Phase 3
move to LiteLLM is a one-line change.

## Scope

- `config/librechat.yaml` with one `endpoints.custom` entry:
  `baseURL: http://host.docker.internal:11434/v1`, dummy API key,
  `models.fetch: true`
- Title generation pointed at `qwen3:0.6b` so conversation titling does
  not block on the 27B
- The config file mounted into the container and referenced by
  `CONFIG_PATH`

## Out of scope

Context-window tuning (`ST-context-window-and-persistence`). Any second
endpoint. LiteLLM.

## Acceptance criteria

1. The model picker in the UI lists both pulled models without any
   manual model entry in config.
2. A single message to the 27B returns a coherent answer.
3. A new conversation gets an auto-generated title, and
   `docker compose logs` shows the title request going to the 0.6b
   model.
4. `docker compose exec librechat curl -fsS http://host.docker.internal:11434/v1/models`
   returns a non-empty list.
5. No API key or secret appears in any committed file.
6. `scripts/check phase1` covers criteria 1 and 4 and passes.
