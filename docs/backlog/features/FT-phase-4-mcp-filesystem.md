---
gh_issue: 5
gh_type: feature
parent: EP-maya-v1
status: done
phase: 4
spec:
---

# Feature: Phase 4 — MCP foundation and scoped filesystem access

## Problem

The model has no tools. It also needs access to real files without being
handed a home directory. Both problems are solved by one standard
interface, but the interface must be proven before capability is
attached to it.

## Scope

- MCP configured in LibreChat with **one trivial tool first** (time or
  echo), to prove the full loop: advertised, chosen, executed, returned,
  reasoned over
- Filesystem MCP with explicit mounts: `~/Documents -> /documents ro`,
  `~/Dev -> /projects ro`
- Write access to `/projects` promoted in a separate, deliberate story
- Document extraction (PDF, DOCX, XLSX) through an extraction-capable
  MCP server

## Out of scope

RAG, embeddings, vector databases, and indexing — deferred until plain
filesystem access provably fails, with the concrete failure logged in
docs/PHASES.md first. Shell or execution tools of any kind.

## Acceptance criteria

1. The trivial MCP tool is advertised to the model, chosen by it for an
   appropriate prompt, executed, and its result used in the answer.
2. The model lists `/documents`, finds a named file, reads it, and
   quotes a line that matches the file on disk.
3. A write to `/documents` fails **and the model reports the failure**
   rather than claiming success.
4. After the write-access story, the model creates a file under
   `/projects` and it appears on the host at the expected path.
5. No MCP container mounts the home directory, host root, or the Docker
   socket.
6. The model extracts and quotes text from a PDF and a DOCX.
7. `scripts/check phase4` passes and covers criteria 3 and 5.
