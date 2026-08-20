---
gh_issue: 52
gh_type: story
parent: FT-phase-7-coding-agent
status: done
phase: 7
spec:
---

# Story: Point the coding alias at a coding model

## Problem

`coding` has pointed at the general model since Phase 3, with a colder
temperature. The alias existed so callers could be written against it
before there was anything different behind it. Now there is.

## Scope

- Pull a coding-specialized model
- Repoint the `coding` alias at it in `config/litellm/config.yaml`
- Prove the swap changes which model serves `coding`, with no edit
  outside that file
- Prove `general` is untouched

## Out of scope

Changing `general`, `fast` or `reasoning`. Any change to the agent
container.

## Acceptance criteria

1. `coding` requests load the coding model, observable in `ollama ps`.
2. `general` requests still load the general model.
3. The only file changed is `config/litellm/config.yaml`, and only
   LiteLLM restarts.
4. The chat agent's behaviour is unchanged.
5. `scripts/check phase7` asserts `coding` and `general` resolve to
   different models and passes.
