---
gh_issue: 54
gh_type: feature
parent: EP-maya-v1
status: proposed
phase: n/a
spec:
---

# Feature: Memory across conversations

## Problem

Maya starts every conversation blank. Facts established last week —
preferences, project context, how the owner works — have to be restated.

Considered on 2026-08-20 and **deliberately not built**. Recorded here so
the analysis is not redone from scratch, and so the decision is visible
rather than an absence.

## What already exists

LibreChat ships memory: the `memoryConfig` schema and an (empty)
`memoryentries` collection are present in the running stack. It is off
because no `memory:` block is configured. Turning it on is configuration,
not new infrastructure.

## The three options, as assessed

**1. LibreChat's built-in memory.** A model reads a window of recent
messages, extracts durable facts, stores them under whitelisted
`validKeys`, and injects them into later conversations. No new service,
no new dependency, reversible by deleting the config block.

    memory:
      validKeys: ["user_preferences", "projects", "learned_facts"]
      tokenLimit: 3000
      personalize: true
      messageWindowSize: 8
      agent:
        enabled: true
        provider: "Maya"
        model: "general"

Costs: an extraction pass on the 27B after exchanges, and a model
writing facts about the owner into Mongo continuously. `validKeys` bounds
what may be stored; `personalize: true` leaves a per-conversation toggle.

**2. A notes file under `/projects`.** The filesystem tools from Phase 4
already allow it: a `MAYA.md` the model reads at the start of a
conversation and appends to deliberately. Durable, greppable, editable by
hand, diffable in git — and the owner can see exactly what Maya thinks it
knows. Nothing automatic about it.

**3. Vector database / RAG.** Not on the table. CLAUDE.md forbids a
vector database or indexing layer until plain filesystem access provably
fails, with the concrete failure logged in `docs/PHASES.md` first.
Nothing has failed, so nothing justifies it.

Options 1 and 2 are complementary rather than alternatives: the first is
effortless and opaque, the second is manual and transparent.

## Decision

Neither, for now. Nothing about the current stack is worse for the lack
of it, and both options are cheap to add later. If it is picked up, the
extraction model should be `general` — a 0.6b extracting facts about a
person produces noise and misremembered details, and wrong memories are
worse than none.

## Trigger to revisit

Restating context becomes a routine irritation — concretely, the same
fact explained to Maya three times in a week. Log the fact and the
occasions here first, the same way the RAG deferral demands a logged
failure.

## Acceptance criteria

Drafted if and when this is picked up. Whatever is built must be
inspectable: the owner should be able to see, and delete, everything
Maya has remembered about them.
