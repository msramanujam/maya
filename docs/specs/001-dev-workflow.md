# Spec 001: Development workflow — backlog, GitHub, branching, agents

**Status:** Ready for adoption
**Applies to:** all work in this repo

## Goal

Every unit of work exists in three linked places: a markdown backlog
file (source of truth for content), a GitHub issue (tracking and state),
and a branch/PR (code). Claude Code maintains all three; nothing is
manual bookkeeping.

## Prerequisites

- `gh` CLI authenticated with `repo` scope: `gh auth login`.
- `main` exists on the remote and is the repo's default branch.
- Labels created once: `scripts/gh-bootstrap.sh`.

## Backlog structure

    docs/backlog/
      epics/    EP-<slug>.md
      features/ FT-<slug>.md
      stories/  ST-<slug>.md
      bugs/     BG-<slug>.md

Front-matter on every file:

    ---
    gh_issue: 42                  # filled after issue creation, never before
    gh_type: epic | feature | story | bug
    parent: FT-<slug>             # backlog file of parent (epics: none)
    status: proposed | ready | in-progress | blocked | done
    phase: 1                      # build phase; process items use n/a
    spec: docs/specs/00N-*.md     # if a spec exists
    ---

Body: problem, scope, out of scope, acceptance criteria. Stories must be
small enough for one Claude Code session.

Hierarchy Epic -> Feature -> Story mirrors GitHub sub-issues exactly.
The markdown file is the source of truth for content; GitHub holds the
state. On conflict, markdown wins and gets pushed to GitHub.

Acceptance criteria in this repo must be observable at a command line or
in a browser. A criterion judged by reading a config file is not a
criterion.

## GitHub integration

**Labels** (created by `scripts/gh-bootstrap.sh`):

    type:epic  type:feature  type:story  type:bug
    status:proposed  status:ready  status:in-progress
    status:blocked   status:done
    phase:1 .. phase:7

**Creating an item** — markdown file first, then the issue:

    gh issue create --title "<title>" --body-file <backlog-file> \
      --label type:story,status:proposed,phase:N

Link it under its parent as a native sub-issue. The API takes the
child's **database id**, not its issue number:

    child_id=$(gh issue view <child-number> --json id --jq .id)
    gh api -X POST /repos/msramanujam/maya/issues/<parent-number>/sub_issues \
      -F sub_issue_id=$child_id

Then write the returned issue number into front-matter `gh_issue` and
commit. Every issue body names its markdown path; every markdown file
carries its issue number — bidirectional by construction.

**Status transitions** are the scrum_master agent's job and only its
job. It edits front-matter and swaps the label in the same operation,
then reads both back to confirm:

    gh issue edit <n> --remove-label status:<old> --add-label status:<new>

## Branching and linking

- Nothing is committed to main directly. One branch per story or bugfix:

      story/<gh_issue>-<slug>       e.g. story/12-librechat-compose
      bugfix/<gh_issue>-<slug>

- The branch is created at session start, from latest `main`.
- Every commit message ends with a trailer line referencing the issue:

      #<gh_issue>

  A commit without one is a rejected PR.
- The PR body carries `Closes #<gh_issue>`, so merging closes the issue.
  The scrum_master then moves the label to `status:done` and confirms.
- One story = one branch = one PR. If a story turns out too big, split
  the story; do not stack the branch.

### Workflow self-changes

Edits to the "Dev workflow" section of CLAUDE.md, to this spec, and to
`.claude/agents/*.md` commit straight to `main`: no branch, no PR, no
issue. The workflow describing itself does not queue behind itself.

## Session protocol

1. Clear context (`/clear`), then name the story. The reset applies to
   the orchestrating session and to every agent — analyst, implementer,
   operator, reviewer, scrum_master are each a fresh spawn per story,
   never resumed from a prior story's instance. Carrying a previous
   story's context into a new story is rejected: it keeps every story's
   context lean and free of prior-story drift. If no story exists yet,
   or it has no spec or acceptance criteria, the analyst drafts the
   spec, the backlog markdown, and its acceptance criteria first; the
   issue is created from that draft.
2. Create/checkout the story branch before touching anything.
3. The implementer builds to the acceptance criteria and adds a check
   for each to `scripts/check`.
4. The operator brings the stack up, runs `scripts/check` in full,
   exercises each criterion by hand, restarts and re-runs, and pastes
   raw output. It never edits.
5. The reviewer checks the diff against the acceptance criteria, the
   spec, and CLAUDE.md, with the operator's output in hand. Blocking
   findings go back to the implementer verbatim.
6. Maximum two implement-review cycles per story. If the reviewer still
   blocks after cycle two, the session stops: scrum_master sets
   `blocked` in front-matter and on the issue, and the unresolved
   findings go back into chat for spec revision. No PR is raised from a
   blocked story.
7. Before the PR, write or update the feature's test guide (below).
   Reviewer pass and PR raise both wait on it.
8. Session ends: checks green, branch pushed, PR raised, merged.

       git push -u origin <branch>
       gh pr create --title "<title>" \
         --body "Closes #<gh_issue>

       docs/backlog/stories/<story-file>.md"
       gh pr merge --squash --delete-branch

   Reviewer pass + green operator run is the merge gate — there is no
   manual human approval step and no CI. Story status updated in
   markdown and on the issue by the scrum_master. **A local-only branch
   is an unfinished session.**
9. When a bug is reported or found mid-session: create
   `bugs/BG-<slug>.md` plus a GitHub issue immediately, before or
   instead of fixing it. The fix happens on its own
   `bugfix/<gh_issue>-<slug>` branch per the normal protocol. Trivial
   in-session fixes still get the bug record — no silent fixes.
10. After the merge, pick the next highest-priority `status:ready` item
    and start its session immediately — step 1 again, context clear
    included, no human prompt in between. If no `ready` item exists, the
    session ends and reports backlog state rather than idling.

## Agents

| Agent | Model | Owns | Never |
|---|---|---|---|
| analyst | opus | Specs, backlog files, acceptance criteria | Writes config or code |
| implementer | sonnet | Compose, service config, scripts, checks | Expands scope; verifies its own work |
| operator | sonnet | Runs the stack, runs checks, pastes raw output | Edits anything |
| reviewer | opus | Last gate: diff vs criteria vs CLAUDE.md | Passes without operator output |
| scrum_master | sonnet | Front-matter status <-> issue label, in one operation | Drafts content, creates/deletes items, touches code |

The operator role exists because of how this project fails: a compose
file that parses is not a stack that works. Separating "runs it" from
"builds it" is what makes the reviewer's evidence independent.

## Test guide (human review)

- Every feature produces one guide a non-engineer can follow to exercise
  what shipped: `docs/test-guide/FT-<slug>.md`, named after the
  feature's backlog slug.
- If the story has no `FT-` parent yet (epic-direct or process story),
  key the guide to the story instead: `ST-<slug>.md`. When a feature
  file is later created, rename the guide and carry the story section
  over — never duplicate under both names.
- Front-matter:

      ---
      feature: FT-<slug>          # or story: ST-<slug> if no feature yet
      gh_issue: <n>
      stories: [ST-slug-a, ST-slug-b]
      status: current
      ---

- Body: one section per story — what changed, setup and prerequisites,
  numbered steps, expected result, pass/fail signal. Steps assume no
  knowledge of the repo: exact commands, URLs, and clicks, not
  descriptions of behavior.
