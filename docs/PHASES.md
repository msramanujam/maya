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
