# Maya — Root CLAUDE.md

Maya is a local, self-hosted AI stack: a ChatGPT-style interface plus a
Codex-style coding environment, running against locally hosted models.
LibreChat is the UI, LiteLLM is the model gateway, MCP is the tool layer.
Full reasoning lives in docs/specs/ — read the relevant spec before
proposing changes that touch its territory.

## Architecture

```
                      LibreChat
                          |
                   Model Gateway (LiteLLM)
                          |
              +-----------+-----------+
              |           |           |
           Ollama       vLLM      Other APIs

                      TOOL LAYER (MCP)
              +-----------+-----------+
              |           |           |
         Filesystem   Search+Fetch  Browser
                       (SearXNG)  (Playwright)

                  CODING ENVIRONMENT
                          |
                    coding agent -> LiteLLM -> local model
```

**The model is a replaceable reasoning engine.** Tool calling, filesystem
access, search, fetch, browser automation, code execution, repo access,
document retrieval, permissions, and conversation state belong to the
platform — never to a particular LLM. A change that couples any of these
to a specific model or to Ollama: rejected PR.

## Host environment

- Apple M3 Max, 128 GB RAM, macOS. OrbStack provides Docker.
- **Ollama runs natively on the host, not in a container** — Docker on
  macOS has no GPU passthrough, and containerizing it loses Metal.
  Containers reach it via `host.docker.internal:11434`.
- Models: `orcarouter/Qwen3.8-27B-Uncensored:q8_0` (tools, thinking,
  vision; 262k context) and `qwen3:0.6b` (fast/utility).
- Remote access is over Tailscale. Nothing is exposed to the public
  internet, at any phase.

## Repo layout

- `compose.yaml` — one file; phases enable services via profiles
  (`core`, `edge`, `gateway`, `tools`, `web`, `browser`, `coding`)
- `config/` — per-service configuration (librechat, litellm, caddy, searxng)
- `data/` — container volumes, gitignored
- `scripts/` — `maya` (up/down/logs/status), `check` (health tests),
  `gh-bootstrap.sh` (one-time label creation)
- `docs/specs/` — specs; `docs/backlog/` — epics/features/stories/bugs;
  `docs/test-guide/` — human-followable verification steps;
  `docs/PHASES.md` — build log and deferral triggers

## Hard rules

**Frameworks.** No LangChain, LangGraph, CrewAI, AutoGen, n8n, Flowise,
Dify, or LlamaIndex. Interfaces are OpenAI-compatible HTTP, MCP, HTTP,
and Docker networking. Introducing one of the above without a concrete
requirement that standards-based interfaces cannot meet: rejected PR.

**No premature retrieval.** No vector database and no indexing layer
until plain filesystem access provably fails, with the concrete failure
logged in `docs/PHASES.md` first.

**Networking.** Only the edge proxy publishes a host port. Every other
service sits on `maya-internal` (`internal: true`). A new service with a
`ports:` mapping: rejected PR unless it is the edge proxy. Published
ports bind to a specific address (`127.0.0.1` or the Tailscale address),
never `0.0.0.0`.

**Secrets.** No secret, key, token, or password in a committed file.
Secrets live in `.env` (gitignored); `.env.example` carries shape and
never values. A credential in `compose.yaml`, a config file, or a
commit message: rejected PR.

**Container privilege.** No container gets the Docker socket. No
container runs privileged. No container mounts the host root or the
home directory — filesystem access is explicit, named mounts only,
read-only unless the story is specifically about granting write.

**Model coupling.** LibreChat and every tool consumer address models by
logical alias (`general`, `fast`, `coding`, `reasoning`) resolved in
LiteLLM config, not by concrete model name. From Phase 3 onward, a
concrete model name outside `config/litellm/config.yaml`: rejected PR.

**Configuration over code.** Swapping a model, a search backend, or a
vendor is a config edit. If it requires editing a caller, the
abstraction is wrong — fix the abstraction, not the caller.

## Definition of done

- The operator agent's `scripts/check` run is green and its **raw output
  is pasted** into the session — not summarized. A compose file that
  parses is not a stack that works.
- The stack survives `docker compose down` + up: state that does not
  survive a restart is a failure, not a caveat.
- The feature's test guide at `docs/test-guide/FT-<slug>.md` is current.
- Backlog front-matter status and the GitHub issue label agree.

## Dev workflow (spec 001)

- Every unit of work exists in three linked places: a markdown backlog
  file in `docs/backlog/` (source of truth for content), a GitHub issue
  (state, via `status:*` labels), and a branch/PR (code). On conflict,
  markdown wins and is pushed to GitHub.
- No commits to main. One story = one branch (`story/<gh_issue>-<slug>`,
  or `bugfix/<gh_issue>-<slug>`) = one PR. Exception: workflow
  self-changes (this section, `docs/specs/001-dev-workflow.md`,
  `.claude/agents/*.md`) commit straight to main — no branch, no PR, no
  issue.
- Every commit message carries a `#<gh_issue>` trailer line. A commit
  without a work-item reference is a rejected PR. PR bodies carry
  `Closes #<gh_issue>`.
- Session protocol: clear context (`/clear`), name the story (analyst
  agent drafts spec, backlog entry, and acceptance criteria first if
  none exist), create the branch, implement, operator runs checks,
  reviewer passes, test guide updated, push, `gh pr create`, then
  `gh pr merge --squash --delete-branch`. scrum_master syncs state
  before the session ends. **A local-only branch is an unfinished
  session.**
- Context clears at the start of every story, for the orchestrating
  session and for every agent (analyst, implementer, operator, reviewer,
  scrum_master) — each is a fresh spawn per story, never resumed from a
  prior story's instance. No agent carries context across stories.
- Specs, backlog items, and acceptance criteria are drafted by the
  analyst agent (Opus). Implementer and reviewer inherit those
  acceptance criteria as given — neither redefines them; ambiguity goes
  back to the analyst.
- The operator agent runs the stack and reports; it never edits. A role
  that both breaks and fixes gives the reviewer no independent signal.
- All backlog-status/GitHub-label syncing is the scrum_master agent's
  job (Sonnet), and only its job — it never drafts content, never
  creates or deletes items, never touches code.
- Creating backlog items: markdown file first, `gh issue create` second,
  write the returned number into front-matter, link as a sub-issue of
  its parent, commit.
- Bugs get a `docs/backlog/bugs/BG-<slug>.md` file and a GitHub issue
  before the fix lands. No silent fixes, even trivial ones.
- Implement-review loop caps at two cycles. Still blocked after two:
  scrum_master sets `status:blocked`, findings return to chat. Never
  raise a PR past a failing review.
- No manual PR-approval gate: reviewer pass + green operator check is
  the merge bar. After merge, the next highest-priority `status:ready`
  item starts immediately — no human prompt in between. If none exists,
  report backlog state rather than idling.
- Every feature ships a human test guide at
  `docs/test-guide/FT-<slug>.md` — plain steps a non-engineer can follow
  to exercise what was built. Written or updated before the PR, in the
  same session. A bugfix or behavior change updates the existing guide,
  never adds a new one. No up-to-date guide, no PR.
