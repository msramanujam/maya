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

## Phase 1 — LibreChat + Ollama

In progress. Sections are appended by each story as it lands.

### Host Ollama bind (story #9)

Ollama shipped listening on `127.0.0.1:11434`. A loopback-bound listener
refuses connections arriving on any other interface, so containers
calling `host.docker.internal:11434` got connection-refused. Every later
phase reaches the model through that name, so this went first.

Changed:

    launchctl setenv OLLAMA_HOST 0.0.0.0:11434
    # then restart the Ollama app — a launchctl variable does not reach
    # an already-running process

`launchctl setenv` is not persistent across reboots. After a reboot,
re-run both lines (`scripts/check phase1` fails loudly if the bind
reverted).

Measured after the restart: `lsof -nP -iTCP:11434 -sTCP:LISTEN` shows
`*:11434`; `docker run --rm curlimages/curl -fsS
http://host.docker.internal:11434/v1/models` returns both models;
`curl http://localhost:11434/api/tags` from the host still works.

**LAN exposure decision.** `0.0.0.0` also exposes 11434 to the local
network. The story offered two options — enable the macOS application
firewall, or accept the exposure knowingly. **Exposure was accepted
knowingly.** The macOS application firewall is off
(`socketfilterfw --getglobalstate` → `State = 0`) and was deliberately
left off; no host-level filtering stands in front of 11434.

So until Phase 2, any device on the same LAN can list these models and
run inference against them, unauthenticated. Ollama has no auth of its
own — the bind *is* the access control. This window is deliberate and
time-boxed, not an oversight.

If that becomes unacceptable before Phase 2 lands, turn the firewall on
and keep Ollama reachable with:

    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add \
      /Applications/Ollama.app/Contents/Resources/ollama
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp \
      /Applications/Ollama.app/Contents/Resources/ollama

Or close it entirely with the revert below.

Revert (back to loopback-only):

    launchctl unsetenv OLLAMA_HOST
    # restart the Ollama app

Deferred: narrowing the bind to the tailnet address plus the container
bridge. Trigger: Phase 2 (`FT-phase-2-remote-access`), which is when the
tailnet address exists to bind to.

### Compose scaffold (story #10)

One `compose.yaml`, profiles rather than overlay files. `core` carries
`mongo:7` and `ghcr.io/danny-avila/librechat:latest`; `edge`, `gateway`,
`tools`, `web`, `browser` and `coding` are reserved names recorded in the
file's header and `x-maya-profiles` until their phase lands — compose has
no way to declare a profile before a service uses it.

`scripts/maya up|down|logs|status` composes the active profile set
(`MAYA_PROFILES`, default `core`) and creates the bind-mount directories
before compose can create them root-owned.

**Two networks, not one.** The first attempt put both services on
`maya-internal` alone (`internal: true`, per CLAUDE.md). The stack came
up healthy and looked correct — but `internal: true` silently drops
published ports: `docker compose ps` showed
`maya-librechat [{ 3080 0 tcp}]`, a published port of 0, and
`127.0.0.1:3080` refused connections. There was no route to
`host-gateway` either, so Ollama would have been unreachable in story #11
for the same reason.

So: `maya-internal` (`internal: true`) carries service-to-service traffic
and holds Mongo alone; `maya-edge` is an ordinary bridge, and whichever
service currently faces the host sits on it too. Phase 1 that is
LibreChat, which is its own edge. Phase 2 gives `maya-edge` to Caddy and
drops LibreChat back to `maya-internal` alone. Mongo never leaves
`maya-internal` in any phase.

Measured: `scripts/check` 16 passed, 0 failed, including after a full
`scripts/maya down` + `up`. Publishing is `maya-librechat
[{127.0.0.1 3080 3080 tcp}]` and `maya-mongo [{ 27017 0 tcp}]` — nothing
on `0.0.0.0`. `http://192.168.50.144:3080` (this machine's LAN address)
is refused both from the host and from a container. Registration through
`POST /api/auth/register` created a user row in Mongo; the throwaway
account was deleted afterwards, so the database ships empty. A marker
document written before `down` was still readable after `up`.

Secrets: `.env` is generated locally with `openssl rand -hex` and
gitignored; `.env.example` carries key names, the generating command, and
placeholder shapes only.

Deferred: nothing new.
