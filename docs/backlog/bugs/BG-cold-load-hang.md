---
gh_issue: 31
gh_type: bug
parent: FT-phase-3-litellm-gateway
status: done
phase: 3
spec:
---

# Bug: the first message after an idle gap hangs for minutes

## Symptom

A chat that answers in ~3 seconds while the model is warm takes minutes
after a gap. Observed at 270 seconds once, and 78 seconds a few minutes
later. The UI shows no error and no progress — it simply hangs, which
reads as a broken gateway rather than a slow load.

## Cause

Ollama unloads a model after five minutes idle. Reloading the 27B means
reading 31 GB back in. When the file is still in the OS page cache that
takes about 7 seconds; when it is not — after a reboot, or once memory
pressure has evicted it — it is read from SSD, and that is the
multi-minute case.

Not the gateway. Measured warm: 3.33s through LiteLLM against 3.27s
direct to Ollama. Measured cold-from-cache: 6.99s through LiteLLM against
6.33s direct. The gateway costs well under a second.

## Scope

- `OLLAMA_KEEP_ALIVE=-1` in `config/launchd/com.maya.ollama-env.plist`,
  so the model stays resident once loaded
- `docs/PHASES.md` records the measurements and what the memory buys
- `scripts/check` asserts the setting, the way it already asserts the
  context length
- Test guide sets the expectation for a genuinely first load, which is
  still slow — the fix removes the repeat, not the first one

## Out of scope

Preloading a model at boot. Any change to LiteLLM or LibreChat. Reducing
the model's size or context.

## Acceptance criteria

1. `ollama ps` shows `UNTIL` as `Forever` (or equivalent) rather than a
   countdown, after a request through the gateway.
2. A second request more than five minutes after the first answers in
   seconds, with no reload event in Ollama's log between them.
3. `docs/PHASES.md` records warm, cold-cached and cold-disk timings and
   the 31 GB standing cost.
4. `scripts/check phase2` asserts `OLLAMA_KEEP_ALIVE` is set as intended
   and passes.
5. Phases 1, 2 and 3 still pass in full.
