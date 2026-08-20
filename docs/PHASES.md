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

> **Superseded by story #23, and its premise was wrong.** Containers on
> OrbStack reach a loopback-bound Ollama perfectly well — see "Narrow the
> Ollama bind" below. The `0.0.0.0` bind described here was never
> necessary, and the LAN exposure accepted for it bought nothing. Kept as
> written because the build log records what was believed at the time;
> the bind is now back to loopback.

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

### Registration closed (story #15)

Pulled forward from Phase 2. Phase 1 shipped `ALLOW_REGISTRATION=true`
so a first account could be created; that account exists, so the window
was closed rather than left open until the Caddy and Tailscale work.

`POST /api/auth/register` now answers `403 {"message":"Registration is
not allowed."}` and writes no row. Existing accounts are unaffected —
the flag gates signup, not login.

**`docker compose restart` does not re-read `env_file`.** Flipping the
flag and restarting looked like it worked: the container came back
healthy, and registration still succeeded, because the container kept
its original environment (`docker exec maya-librechat env` still read
`ALLOW_REGISTRATION=true`). Only `scripts/maya up`, which recreates the
container, applies a changed `.env`. This is silent in both directions,
so `scripts/check` probes the running endpoint rather than reading
`.env` — the file agreeing with intent proves nothing.

The probe uses a throwaway address and, if registration turns out to be
open, deletes the row it just created and reports FAIL. Verified both
ways: with the flag off, `registration refused (403)`; with it on
temporarily, `registration is OPEN (200); probe user removed` and
`db.users` back to one.

Remote access stays deferred to Phase 2 in full — Tailscale is already
running on this host (`madhu-m3-mpb`, `100.92.97.39`), but nothing binds
to it yet, and LibreChat is still `127.0.0.1` only.

Deferred: nothing new.

### Check health race (bug #17)

The health assertions added by story #10 sampled `docker inspect` once,
immediately. The operator's procedure is `scripts/maya up` then
`scripts/check` — exactly that sequence — and LibreChat needs ~45s from
cold, so a correct stack reported
`FAIL maya-librechat health is 'starting'`.

`starting` is not a verdict, it is the absence of one, so the check now
waits it out: poll while `starting`, bounded by `HEALTH_WAIT` (default
90s, overridable), then assert. `unhealthy`, `none` and `missing` stay
terminal and fail immediately, and a container still `starting` at the
bound fails too — the wait is not a way to pass. A run that waited says
so (`maya-librechat healthy (after 4s)`), so a slow start stays visible
instead of being hidden by the fix.

Verified: `maya up && check` back to back, no sleep, 17 passed 0 failed
with `healthy (after 4s)`; LibreChat stopped, FAIL in 1s rather than a
hang; `HEALTH_WAIT=4` against a cold start, `still starting after 4s`;
added cost on an already-healthy stack, none measurable.

The wider lesson, and the reason this was worth a bug rather than a
quiet patch: a check that cries wolf on a healthy stack trains everyone
to re-run it and ignore the first result, which is how a real failure
gets waved through.

Deferred: nothing new.

### Ollama endpoint (story #11)

`config/librechat/librechat.yaml`, mounted read-only at
`/app/librechat.yaml` and referenced by `CONFIG_PATH`. One
`endpoints.custom` entry against
`http://host.docker.internal:11434/v1` — Ollama's OpenAI-compatible API,
not its native one, so Phase 3 swaps the `baseURL` for LiteLLM's and this
file barely changes.

Note the path: `config/librechat/librechat.yaml`, per the CLAUDE.md
per-service layout, where the story said `config/librechat.yaml`.

Models come from `fetch: true`, so `ollama pull` is enough to see a new
one in the picker. `models.default` cannot be empty — LibreChat's schema
rejects it with `Array must contain at least 1 element(s)`, and the
container exits rather than starting degraded — so one name sits there as
the model a new conversation opens on. That is a default, not a
hand-maintained list; Phase 3 replaces it with the `general` alias.

`titleModel: qwen3:0.6b` keeps conversation titling off the 27B, which
would otherwise put a second cold load in front of the first answer.

The dummy API key lives in `.env` as `OLLAMA_API_KEY` rather than as a
literal in the YAML. Ollama authenticates nothing and the value is
ignored, but nothing key-shaped belongs in a committed file even when
it is inert.

Measured: `/api/models` returns
`["orcarouter/Qwen3.8-27B-Uncensored:q8_0", "qwen3:0.6b"]` under the
`ollama` endpoint — both models, one of them never named in config.
A chat completion over the exact URL LibreChat uses answered "The capital
of France is Paris." in 9.8s cold; the 0.6b answered in 11.9s cold.
`scripts/check`: 19 passed, 0 failed.

Titling was confirmed against Ollama's own log rather than LibreChat's,
which does not record the title request at default verbosity. Both
models load within two seconds of each other on the first message:

    11:22:14.8  blob 7f4030143c1c, 311 tensors   -> qwen3:0.6b
    11:22:16    POST /v1/chat/completions  1.76s -> the title
    11:22:16.5  blob 31756fca94be, 866 tensors   -> the 27B
    11:22:27    POST /v1/chat/completions 12.74s -> the answer

Ollama's GIN lines carry no model name, so the attribution comes from
matching load events to manifest digests — worth knowing before trying
to read that log again.

Verification note: this LibreChat build has no `/api/ask/*` routes — all
chat runs through the agents pipeline — and driving that from curl was
not worth the yak-shave, so criteria 2 and 3 were exercised in the UI by
the owner. `/api/models` needs a session, so the check asserts what
produces the picker (endpoint loaded, `fetch: true`, more models upstream
than the one named default) rather than the picker itself; the picker
contents were confirmed once, by hand, with a throwaway account that was
deleted afterwards.

Deferred: nothing new.

### Context window and persistence (story #12)

    launchctl setenv OLLAMA_CONTEXT_LENGTH 32768
    # then restart the Ollama app

**The story's premise was wrong for this Ollama.** It assumed Ollama
defaults the context far below the model's 262k. Version 0.32.14 does the
opposite — it loads a model at its full advertised context. Measured on
the 27B, same prompt, only the setting changed:

| Context | Resident | Processor |
|---|---|---|
| 262144 (default) | 46 GB | 100% GPU |
| 32768 (set) | 31 GB | 100% GPU |

So the setting buys 15 GB rather than rescuing a truncated conversation.
32768 stands as the deliberate starting point the story asked for, and
raising it is now an informed decision: roughly 15 GB per 230k of context
on this model, on a 128 GB machine.

**`num_ctx` cannot come from `librechat.yaml`.** Ollama's
OpenAI-compatible endpoint ignores it, both as a top-level body parameter
and nested under `options` — verified by sending each and watching
`ollama ps` still report 262144. The lever is the server-wide
`OLLAMA_CONTEXT_LENGTH`, which is why this is a host setting like the
bind in story #9, and carries the same reboot caveat: `launchctl setenv`
does not survive one. `scripts/check` asserts both the variable and the
context of any resident model, so a reboot that silently reverts it fails
the run.

Reading `ollama ps` from a script needs column offsets, not field
numbers: `SIZE` is "31 GB" and `UNTIL` is "4 minutes from now", so
`$(NF-3)` lands on a word of the timestamp. The first version of the
check reported `context '3 '`.

Recall verified at 12252 prompt tokens — three times the old 4096 default
— with a passphrase in the opening message and 8k tokens of filler after
it. The model returned `BRASS-LANTERN-47` and nothing else. Note the
27B is a thinking model: with `max_tokens: 40` the answer came back
empty, having spent the budget on reasoning. That is a real trap for
anything scripting against it.

Persistence across `scripts/maya down` + `up`: the conversation
`334fed93` ("FRANCE CAPITALE") survived intact with both messages. The
assistant's reply lives in `content[{type:"text"}]` and its `text` field
is empty — the agents pipeline stores it that way, so a query reading
`text` will wrongly conclude the history is gone.

Revert:

    launchctl unsetenv OLLAMA_CONTEXT_LENGTH
    # restart the Ollama app; models return to 262144 and 46 GB

Deferred: raising the context beyond 32768, and any summarization or
compaction strategy. Trigger: a real conversation hitting the limit —
log the conversation and what was lost here first.

### Phase 1 closed

All seven feature criteria met. What runs: LibreChat and MongoDB on the
`core` profile, LibreChat on `127.0.0.1:3080` and Mongo on nothing,
against the host's Ollama over `host.docker.internal:11434/v1`. Both
models discovered rather than listed, titling on the 0.6b, context pinned
at 32768, registration closed, conversations surviving a full cycle.
`scripts/check`: 21 passed, 0 failed.

Multi-turn coherence and sidebar persistence were confirmed in the UI by
the owner; everything else is asserted by `scripts/check`.

Two host settings carry a reboot caveat, both set with `launchctl setenv`
and neither surviving one:

    OLLAMA_HOST=0.0.0.0:11434        # story #9
    OLLAMA_CONTEXT_LENGTH=32768      # story #12

`scripts/check phase1` fails on either if it reverts. Phase 2 narrows the
first to the tailnet address plus the container bridge, which is also
when this pair should stop being launchctl variables.

Standing exposure carried into Phase 2: port 11434 is open to the LAN
with the macOS firewall off, accepted knowingly in story #9. LibreChat
itself is not — `127.0.0.1` only.

## Phase 2 — Remote access

In progress. Sections are appended by each story as it lands.

### Narrow the Ollama bind (story #23)

**The exposure is closed, and it should never have been opened.** Story
#9 assumed a loopback-bound Ollama is unreachable from containers, and
bound `0.0.0.0` to fix it. That premise is false on OrbStack. Container
traffic to `host.docker.internal` resolves to `0.250.250.254` and arrives
at the host as:

    TCP 127.0.0.1:62233 -> 127.0.0.1:11434 (ESTABLISHED)

— on loopback. Verified by binding `127.0.0.1:11434` and watching both a
throwaway container and LibreChat itself list the models. So the fix is
not to narrow the bind to the tailnet address plus the container bridge,
as the story anticipated: it is to stop setting `OLLAMA_HOST` at all.
Ollama's own default is `127.0.0.1:11434`, which is exactly right.

All three ranked options in the story are therefore moot — no pinned
bridge subnet, no application firewall, no `pf` rule. Nothing on the LAN
or the tailnet can reach 11434; containers are unaffected. Measured: the
LAN address refuses from both the host and a container, the tailnet
address refuses, `docker run ... host.docker.internal:11434/v1/models`
returns both models.

`host.docker.internal` reaching the host over loopback is an OrbStack
behaviour, not a Docker guarantee. On a runtime that routes container
traffic over a bridge instead, the loopback bind would genuinely fail and
this decision needs revisiting — `scripts/check phase1` fails loudly if
containers lose reachability, which is the signal to come back here.

**Reboot persistence.** `launchctl setenv` is lost on reboot and
Ollama reads its environment at launch, so the context window silently
reverted to 262144 — 46 GB resident instead of 31 GB, with nothing to
announce it. `config/launchd/com.maya.ollama-env.plist`, installed by
`scripts/install-host-env`, sets it at login. `OLLAMA_HOST` is
deliberately absent from that plist: the default is what we want, and a
setting that exists is a setting that can drift.

`scripts/check phase2` asserts the bind shape, that the LAN address
actually refuses, and that the agent is loaded. All three were
negative-tested: unloading the agent, and reopening the bind to
`0.0.0.0`, each produce the FAIL they exist for.

Deviation from the story: acceptance criterion 3 asked that
`scripts/check phase1` pass "unchanged". It could not — #9's assertion
demanded a *non*-loopback listener, which is now precisely the failure
condition. That assertion moved to `phase2` inverted, and `phase1` now
asserts only that Ollama is listening at all, since reachability is
already covered by two checks that call it.

Closed: the story-#9 LAN exposure. Port 11434 is no longer reachable
from the network, and the macOS application firewall is not needed for
it.

Deferred: nothing new.

### Tailscale CLI and tailnet certificate (story #21)

HTTPS certificates had to be enabled for the tailnet first — a one-time
toggle at https://login.tailscale.com/admin/dns, not reachable from the
CLI. Before it, `tailscale status --json` reported `CertDomains: null`
and `tailscale cert` had no CA to ask.

Certificate for `madhu-m3-mpb.tailadf0a2.ts.net`, issued by Let's
Encrypt, valid **Aug 20 → Nov 18 2026**. Lives in `data/tailscale/`
(gitignored), key at 0600, and the public key matches the certificate.

**Two things fought back.**

`tailscale cert --cert-file <path>` fails with `operation not permitted`
for any path under this repo, and with `no such file or directory` for a
relative one. Tailscale.app is sandboxed: it cannot create files here,
and its working directory is not ours. `scripts/tailscale-cert` therefore
asks for both PEMs on stdout (`--cert-file - --key-file -`) and splits
them itself.

A symlink to the CLI does not work. The binary derives its bundle
identity from its own path, so `/opt/homebrew/bin/tailscale -> ...app/...`
dies with `Fatal error: The current bundleIdentifier is unknown to the
registry`. `config/host/tailscale-shim.sh` execs the real path instead,
which keeps the binary where it expects to be.
`/opt/homebrew/bin` is user-writable on Apple Silicon, so no sudo is
needed — `scripts/install-host-env` installs both the shim and the
LaunchAgent.

**Renewal is manual.** Tailscale issues for 90 days and renews its own
copy, but ours is a static file that nothing refreshes. Re-run
`scripts/tailscale-cert`. `scripts/check phase2` fails once fewer than
14 days remain, which is the only reminder there is — a certificate that
silently expires takes Caddy down with it.

Deferred: automating renewal. Trigger: the first time the check catches
an expiry that should have been handled, or Caddy being restarted often
enough that a stale file is likely.

### Caddy on the edge (story #22)

`caddy:2-alpine` on the `edge` profile, publishing `100.92.97.39:443` —
the Tailscale address, from `TAILSCALE_IP` in `.env`. LibreChat no longer
publishes anything. `scripts/maya` now defaults to `core edge`.

`auto_https off` and `admin off`: the certificate already exists and
Let's Encrypt cannot reach this host, so Caddy must not try to issue one.
It serves the file `scripts/tailscale-cert` wrote.

**`127.0.0.1:3080` is gone.** Everything reaches Maya through the
MagicDNS name now, including this machine. That means Maya is unreachable
if Tailscale is down, which is a real trade the tailnet-only design
implies — and `scripts/check` says so rather than reporting a mystery
failure.

**LibreChat stays on `maya-edge` despite publishing nothing.** Dropping
it to `maya-internal` alone was the first attempt, and it broke Ollama
immediately: `internal: true` means no gateway, so `host.docker.internal`
is unreachable no matter that OrbStack terminates that address on
loopback. `maya-edge` is not "the network for things that publish", it is
the only network with a route off the host — and Ollama is on the host.
Exactly one service publishes; membership is not permission.

`DOMAIN_CLIENT` and `DOMAIN_SERVER` point at the public URL. Without
them `/api/config` reported `serverDomain: http://localhost:3080`, and
absolute links and cookies would have been built against an origin that
no longer exists.

`check_phase1`'s "exactly two containers" assertion had to become "both
core services running": `docker compose ps` lists every running container
in the project regardless of `--profile`, so it failed on Caddy's
presence.

Measured: `https://madhu-m3-mpb.tailadf0a2.ts.net` answers 200 with
`ssl_verify_result 0`, served cert `CN = madhu-m3-mpb.tailadf0a2.ts.net`
from Let's Encrypt. Nothing answers on `192.168.50.144` at `:3080` or
`:443`. `scripts/check`: 28 passed, 0 failed, after a full `down` + `up`,
with conversations intact.

Deferred: nothing new.
