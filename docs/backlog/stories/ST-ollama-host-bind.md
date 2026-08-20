---
gh_issue: 9
gh_type: story
parent: FT-phase-1-librechat-ollama
status: ready
phase: 1
spec:
---

# Story: Make host Ollama reachable from containers

## Problem

Ollama listens on `127.0.0.1:11434`. Containers reaching it via
`host.docker.internal` get connection-refused, because a loopback-bound
listener rejects connections arriving on any other interface. Every
later phase depends on this working, so it goes first.

## Scope

- Change the bind: `launchctl setenv OLLAMA_HOST 0.0.0.0:11434`, then
  **restart the Ollama app** — a launchctl variable does not reach an
  already-running process.
- Document the change and how to revert it in `docs/PHASES.md`.
- Add the container-to-host reachability check to `scripts/check`.

## Security note

Binding `0.0.0.0` also exposes 11434 to the LAN. This window closes in
Phase 2, when the bind is narrowed to the tailnet address plus the
container bridge. Until then, enable the macOS application firewall or
accept the exposure knowingly. Record which was chosen in
`docs/PHASES.md`.

## Out of scope

Any container work. Narrowing the bind (Phase 2).

## Acceptance criteria

1. `lsof -nP -iTCP:11434 -sTCP:LISTEN` shows a listener on `*:11434`,
   not `127.0.0.1:11434`.
2. `docker run --rm curlimages/curl -fsS http://host.docker.internal:11434/v1/models`
   returns a non-empty JSON model list.
3. `curl http://localhost:11434/api/tags` still works from the host.
4. `docs/PHASES.md` records the change, the LAN-exposure decision, and
   the revert command.
5. `scripts/check phase1` includes the container-to-host check and passes.
