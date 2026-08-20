---
gh_issue: 28
gh_type: story
parent: FT-phase-3-litellm-gateway
status: done
phase: 3
spec:
---

# Story: Point LibreChat at the gateway and remove concrete model names

## Problem

`config/librechat/librechat.yaml` names two concrete models — one as the
default a conversation opens on, one for titling. While those names live
outside LiteLLM, swapping a model means editing a caller, which is the
coupling Phase 3 exists to remove.

## Scope

- LibreChat's endpoint `baseURL` becomes the gateway's, its key the
  gateway's master key
- Concrete model names in `librechat.yaml` replaced by aliases
- Model discovery still by `fetch`, now returning the alias list
- A `grep`-based check that no concrete model name appears outside
  `config/litellm/config.yaml`

## Note on the feature's criterion 4

The feature asks that `grep -r` across the whole repo find no concrete
model name outside the LiteLLM config. `docs/PHASES.md` and the test
guide legitimately name models when recording what was measured — a
build log that cannot say which model used 46 GB is worth less. Scope
the check to configuration and code (`config/`, `scripts/`,
`compose.yaml`, `.env.example`) and record the narrowing.

## Out of scope

The gateway itself (`ST-litellm-gateway-service`). Adding models.

## Acceptance criteria

1. The UI model picker lists the four aliases and no concrete model
   name.
2. A two-message conversation through the UI on `general` answers
   coherently, and titling still works.
3. Repointing `fast` at a different pulled model in
   `config/litellm/config.yaml` and restarting only the LiteLLM
   container changes what `fast` answers — with no edit to any LibreChat
   file. This swap is the feature.
4. No concrete model name appears in `config/` (outside
   `config/litellm/config.yaml`), `scripts/`, `compose.yaml`, or
   `.env.example`.
5. `scripts/check phase3` covers criterion 4 and passes, and phases 1
   and 2 still pass in full.
