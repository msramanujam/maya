---
gh_issue: 35
gh_type: story
parent: FT-phase-4-mcp-filesystem
status: in-progress
phase: 4
spec:
---

# Story: Prove the MCP loop with one trivial tool

## Problem

Nothing has ever exercised tool calling on this stack. Attaching
filesystem access to an unproven interface means debugging two things at
once when it fails.

One tool that does something trivial and verifiable proves the whole
loop: advertised to the model, chosen by it, executed, returned, and
reasoned over.

## Scope

- MCP configured in LibreChat with a single time server
- Package caches persisted so a restart does not re-download the server
- `scripts/check phase4` asserts the server starts and advertises its
  tools

## Note for implementation

No prebuilt MCP images were reachable, but the LibreChat image ships
`node`, `npx`, `uvx` and `python3`, and stdio servers run inside it —
LibreChat's documented arrangement. That puts any future filesystem
mounts on the LibreChat container, which is fine: explicit named mounts,
read-only, no home directory and no Docker socket.

## Out of scope

Filesystem access. Document extraction. Any tool that touches the host.

## Acceptance criteria

1. The time tool is advertised to the model — it appears in the UI's
   tool list for the endpoint.
2. Asked something requiring the current time, the model calls the tool
   and its answer reflects the returned value rather than a guess.
3. Restarting the stack does not re-download the server: the second
   start is materially faster and works offline from the cache.
4. `scripts/check phase4` starts the server, confirms it advertises at
   least one tool, and passes.
