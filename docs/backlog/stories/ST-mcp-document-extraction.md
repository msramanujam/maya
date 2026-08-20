---
gh_issue: 38
gh_type: story
parent: FT-phase-4-mcp-filesystem
status: ready
phase: 4
spec:
---

# Story: Extract text from PDF, DOCX and XLSX

## Problem

Most of what lives in `~/Documents` is not plain text. A filesystem tool
that can only read UTF-8 can see those files and not use them, which is
worse than not seeing them — the model will guess at contents.

## Scope

- An extraction-capable MCP server able to read PDF, DOCX and XLSX from
  the existing read-only mounts
- Fixtures committed under `docs/fixtures/` so the check does not depend
  on whatever happens to be in the owner's Documents folder
- `scripts/check phase4` extracts from each format and asserts on a
  known string

## Out of scope

OCR of scanned images. Embeddings or indexing of extracted text — the
standing RAG deferral is unchanged.

## Acceptance criteria

1. Text extracted from a PDF contains a known string from that PDF.
2. The same for a DOCX and for an XLSX.
3. The model, asked about a document by name, quotes text from it that
   matches the file.
4. Extraction respects the mounts: a file outside `/documents` and
   `/projects` cannot be extracted.
5. `scripts/check phase4` covers criteria 1, 2 and 4 and passes.
