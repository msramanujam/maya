---
gh_issue: 8
gh_type: feature
parent: EP-maya-v1
status: proposed
phase: 7
spec:
---

# Feature: Phase 7 — Coding agent and model specialization

## Problem

The Codex half of the goal: an agent that inspects a repository, edits
files, runs builds and tests, and iterates on failures — kept logically
separate from the general chat agent even though both use the same model
backend.

## Scope

- A coding agent container (profile `coding`) pointed at LiteLLM
- Explicitly mounted repositories only; shell and execution confined to
  that container
- Model specialization: repoint the `coding` alias in LiteLLM at a
  coding-specialized model, leaving `general` untouched

## Deferred decision

The agent itself — OpenHands, Aider, or Continue — is chosen at the
start of this feature, not before. The choice depends on how the model
performed at tool selection in Phases 4-6: if it was unreliable, the
autonomous-loop option is the wrong bet and a supervised agent wins.
Record the decision and its evidence in docs/PHASES.md.

## Out of scope

Giving the coding agent access to the chat agent's mounts. Any Docker
socket access.

## Acceptance criteria

1. Given a scratch repository and a natural-language description, the
   agent reads the code, makes the change, runs the test suite, and
   iterates on at least one failure without human intervention.
2. The agent cannot read or write any path outside its declared mounts —
   verified by asking it to read a file outside them and confirming it
   fails.
3. Repointing the `coding` alias changes which model the agent uses with
   no edit outside `config/litellm/config.yaml`.
4. The general chat agent's behavior is unchanged by everything in this
   feature.
5. The coding container has no Docker socket and no published port.
6. `scripts/check phase7` passes and covers criteria 2 and 5.
