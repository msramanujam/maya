---
gh_issue: 43
gh_type: bug
parent: FT-phase-4-mcp-filesystem
status: done
phase: 4
spec:
---

# Bug: the model is never offered its tools

## Symptom

Asked the time, the model answers "I don't have access to a real-time
clock". Asked to list `~/Documents`, it explains how to do it in Finder.
Asked to read a fixture PDF, it says it has no filesystem access. It has
17 tools.

## What is not the cause

- The servers are running and advertising:
  `[MCP] Initialized with 3 configured servers and 17 tools`.
- Every tool works when called directly — the checks exercise all of
  them.
- The model and gateway handle tool calling correctly. A request to
  LiteLLM carrying a `tools` array returns
  `finish_reason: tool_calls` with a well-formed call.

So the gap is between LibreChat and the gateway: LibreChat is not putting
the tools in the request.

## Likely cause

This build routes chat through an ephemeral agent, and the request the
client sends carries an `ephemeralAgent` object listing which
capabilities are active — the phone's traffic showed
`{"execute_code":false,"web_search":false,"file_search":false}` with no
`mcp` key at all. The client bundle contains MCP selector strings, so the
servers appear in the chat UI's tool control and are off until chosen per
conversation.

If that is right, the tools work but must be switched on for each chat,
which is not a stack anyone would call finished.

## Scope

- Confirm the manual path works: enable the servers in the chat UI, ask
  for the time, observe a tool call
- Then make it the default rather than a per-conversation ritual —
  `librechat.yaml` has per-server options (`chatMenu`, `startup` appear
  in the shipped schema) worth trying before anything more invasive
- `scripts/check` asserts whatever mechanism ends up carrying the
  default, so a config change that silently disarms the tools fails

## Out of scope

Any change to the servers themselves — they work.

## Acceptance criteria

1. In a **new** conversation, with no per-chat setup, asking for the
   current time produces a visible tool call and an answer derived from
   it.
2. The same for a filesystem question and a document extraction.
3. `scripts/check phase4` asserts the default is in place and passes.
4. `docs/test-guide/FT-phase-1-librechat-ollama.md` tells a reader how to
   see which tools a conversation has.
