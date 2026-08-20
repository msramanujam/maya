# Maya — build log

One section per phase. Written as the phase completes, not before.
Records what was built, what the tests actually showed, and what was
deferred with the trigger that would bring it back.

Deferral triggers are the point of this file: "later" rots, a recorded
trigger does not.

## Standing deferrals

| Deferred | Trigger to revisit |
|---|---|
| RAG / vector database | Plain filesystem access provably fails — e.g. a question needing synthesis across many files where context-stuffing failed. Log the concrete failure here first. |
| Interactive approval gate (MCP proxy) | Capability scoping (read-only mounts, withheld tools) proves too blunt in real use. |
| vLLM as a second backend | Ollama becomes the bottleneck, or a model ships that Ollama cannot serve. |
| LiteLLM database / virtual keys | Usage tracking or per-consumer keys are actually needed. |

## Phase 0 — workflow scaffold

Built: CLAUDE.md, `.claude/agents/*` (analyst, implementer, reviewer,
operator, scrum_master), `docs/specs/001-dev-workflow.md`, backlog
skeleton, `scripts/gh-bootstrap.sh`, `scripts/check`.

Tested: `scripts/check` prereq section.

Deferred: nothing.
