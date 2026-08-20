---
gh_issue: 51
gh_type: story
parent: FT-phase-7-coding-agent
status: done
phase: 7
spec:
---

# Story: Coding agent container, confined to declared repositories

## The deferred decision, decided

The feature left the agent open — OpenHands, Aider or Continue — to be
chosen on evidence at the start of this phase. It is Aider, and mostly
not on preference:

- **OpenHands** spawns per-session runtime containers and needs the
  Docker socket to do it. "No container gets the Docker socket" is a
  hard rule in CLAUDE.md, and working around it would mean giving a
  model-driven agent the ability to start privileged containers on the
  host. Ruled out on the rule, not on merit.
- **Continue** is an IDE extension. It does not fit "a container pointed
  at LiteLLM", and its execution model is the editor's, not the stack's.
- **Aider** is a process that reads a repository, edits files, runs a
  test command and iterates. It speaks OpenAI-compatible HTTP, so it
  points at the gateway with no adapter, and it needs nothing but the
  repository it was given.

Supporting evidence from Phases 4-6: the model chose tools correctly and
unprompted once they were actually offered — the time tool, the
filesystem tool and the extractor were each selected for the right
question. That makes an agent that drives tools a reasonable bet rather
than a hopeful one.

## Scope

- Aider on the `coding` profile, pointed at `http://maya-litellm:4000/v1`
  using the `coding` alias
- Exactly one mount: a scratch repository, read-write. Nothing else —
  not `/documents`, not `/projects`, not the home directory
- No Docker socket, no published port
- `scripts/check phase7` asserts the confinement and that the agent can
  reach the gateway

## Out of scope

Model specialization (`ST-coding-model-specialization`). Access to the
chat agent's mounts. Any Docker socket access, in any form.

## Acceptance criteria

1. Given a scratch repository and a description of a change, the agent
   reads the code, edits it, runs the tests and iterates on at least one
   failure without human intervention.
2. Asked to read a path outside its mount, it fails.
3. The container has no Docker socket and no published port.
4. `scripts/check phase7` covers criteria 2 and 3 and passes.
