---
gh_issue: 12
gh_type: story
parent: FT-phase-1-librechat-ollama
status: ready
phase: 1
spec:
---

# Story: Context window and conversation persistence

## Problem

Ollama defaults the context window far below the model's 262k, so long
conversations silently lose their beginning. And a chat interface that
forgets everything on restart is not usable. Both need to be set
deliberately and proven.

## Scope

- Set `num_ctx` explicitly (start at 32k) via the endpoint's parameters
- Measure and record the resident memory cost at that setting in
  `docs/PHASES.md`, so raising it later is an informed decision
- Prove conversation persistence across a full stack restart
- Write `docs/test-guide/FT-phase-1-librechat-ollama.md`

## Out of scope

Raising context beyond the chosen starting value. Summarization or
context-compaction strategies.

## Acceptance criteria

1. `ollama ps` shows the model loaded with the configured context size,
   not the default.
2. A conversation exceeding the old default context still answers a
   question about its own opening message correctly.
3. `docs/PHASES.md` records the chosen `num_ctx` and the measured memory
   cost from `ollama ps`.
4. After `./scripts/maya down` and `up`, a prior conversation is still
   listed in the sidebar and its full history is readable.
5. `docs/test-guide/FT-phase-1-librechat-ollama.md` exists and its steps
   can be followed start to finish by someone who has not read this repo.
6. `scripts/check phase1` passes in full.
