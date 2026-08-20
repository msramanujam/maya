---
gh_issue: 37
gh_type: story
parent: FT-phase-4-mcp-filesystem
status: ready
phase: 4
spec:
---

# Story: Grant write access to /projects, deliberately

## Problem

Read-only access proves the model can see files. Writing is the point at
which a mistake costs something, so it is promoted on its own rather
than folded into the story that introduced the mount.

## Scope

- `~/Dev -> /projects` becomes read-write; `/documents` stays read-only
- `scripts/check phase4` asserts the asymmetry — `/projects` writable,
  `/documents` refused — so a future change that quietly widens access
  fails the run

## Out of scope

Write access to `/documents`, ever, in this phase. Deletion policy.
Any execution capability.

## Acceptance criteria

1. The model creates a file under `/projects` and it appears on the host
   at the expected path with the expected content.
2. A write to `/documents` still fails and is still reported as a
   failure.
3. `docker inspect` shows `/documents` mounted `ro` and `/projects`
   mounted `rw`, and still no home, host-root or Docker-socket mount.
4. `scripts/check phase4` covers criteria 2 and 3 and passes.
