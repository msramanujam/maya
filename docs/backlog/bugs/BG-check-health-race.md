---
gh_issue: 17
gh_type: bug
parent: FT-phase-1-librechat-ollama
status: ready
phase: 1
spec:
---

# Bug: scripts/check reports a false FAIL right after `scripts/maya up`

## Symptom

Running `scripts/check` within a few seconds of `scripts/maya up`
reports:

    FAIL  maya-librechat health is 'starting' (docker compose logs maya-librechat --tail 50)

The stack is fine. LibreChat takes roughly 45 seconds to become healthy
from cold, and the health assertion samples once, immediately, with no
wait. Re-running the same command a minute later passes.

## Why it matters

The operator's procedure is "bring the stack up, then run
`scripts/check`" — precisely the sequence that trips this. A check that
cries wolf on a healthy stack trains everyone to re-run it and ignore
the first result, which is how a real failure gets waved through.

Introduced by story #10, which added the health assertions.

## Scope

- Health assertions in `check_phase1` wait for a terminal state instead
  of sampling once: poll while the status is `starting`, up to a bound
  comfortably past LibreChat's cold start, then assert.
- A container that is genuinely unhealthy, missing, or still `starting`
  at the bound still FAILs — the wait must not become a way to pass.
- Report the wait when one happens, so a slow start stays visible rather
  than being hidden by the fix.

## Out of scope

Every other check. Container start-up time itself. `start_period` tuning
in `compose.yaml`.

## Acceptance criteria

1. `scripts/maya up && scripts/check` run back to back, with no sleep in
   between, passes on a working stack.
2. With LibreChat stopped (`docker compose --profile core stop
   librechat`), `scripts/check phase1` FAILs on the health assertion
   rather than hanging, and does so within the bound.
3. The passing run states how long it waited when it waited at all.
4. Total added wall-clock on an already-healthy stack is under a second.
