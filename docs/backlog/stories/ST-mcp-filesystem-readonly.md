---
gh_issue: 36
gh_type: story
parent: FT-phase-4-mcp-filesystem
status: done
phase: 4
spec:
---

# Story: Read-only filesystem access to Documents and Dev

## Problem

The model needs real files. It must not be handed a home directory to
get them.

## Scope

- Filesystem MCP server exposing exactly two paths:
  `~/Documents -> /documents` and `~/Dev -> /projects`, both read-only
- Mounts declared explicitly, read-only at the container level, so the
  server's own permissions are not the only thing standing between the
  model and the disk
- `scripts/check phase4` asserts a write is refused and that no
  forbidden mount exists

## Out of scope

Write access (`ST-mcp-projects-write`). Document extraction. Anything
outside those two directories.

## Acceptance criteria

1. The model lists `/documents`, finds a named file, reads it, and
   quotes a line matching the file on disk.
2. A write to `/documents` fails **and the model reports the failure**
   rather than claiming success.
3. `docker inspect` shows no container mounting the home directory, the
   host root, or the Docker socket, and both new mounts are `ro`.
4. Paths outside the two mounts are not reachable from the tool.
5. `scripts/check phase4` covers criteria 2 and 3 and passes.
