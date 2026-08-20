# Backlog

Markdown is the source of truth for content. GitHub issues hold state.
On conflict, markdown wins and gets pushed to GitHub. Full rules:
`docs/specs/001-dev-workflow.md`.

    epics/    EP-<slug>.md    one file per epic
    features/ FT-<slug>.md    one file per feature
    stories/  ST-<slug>.md    one file per story
    bugs/     BG-<slug>.md    one file per bug

## Front-matter

    ---
    gh_issue: 42                  # filled after issue creation, never before
    gh_type: epic | feature | story | bug
    parent: FT-<slug>             # backlog file of parent (epics: none)
    status: proposed | ready | in-progress | blocked | done
    phase: 1                      # build phase; process items use n/a
    spec: docs/specs/00N-*.md     # if a spec exists
    ---

## Status vocabulary

| Status | Meaning |
|---|---|
| `proposed` | Written down, not yet agreed as next work |
| `ready` | Agreed, has acceptance criteria, can start today |
| `in-progress` | A branch exists and a session is on it |
| `blocked` | Two review cycles failed, or an external dependency stalled it |
| `done` | Merged, checks green, test guide current |

Only the scrum_master agent changes status, and it changes both the
front-matter and the GitHub label in the same operation.

## Acceptance criteria

This is an infrastructure repo. Criteria must be observable at a command
line or in a browser — "container X answers on port Y", "the model
returns a tool call for prompt P", "a write to a read-only mount fails
and the model reports the failure". A criterion that can only be judged
by reading a config file is not a criterion; rewrite it as the behavior
the config is supposed to produce.
