---
gh_issue: 23
gh_type: story
parent: FT-phase-2-remote-access
status: in-progress
phase: 2
spec:
---

# Story: Narrow the Ollama bind and make the host settings survive a reboot

## Problem

Story #9 bound Ollama to `0.0.0.0:11434` so containers could reach it,
knowingly opening the model API to the LAN with the macOS firewall off.
Anyone on the same Wi-Fi can run inference on these models. Phase 2 is
where that window closes.

Separately, both Ollama settings are `launchctl setenv` variables, which
do not survive a reboot. After a restart the bind reverts to loopback
(containers break) and the context reverts to 262144 (15 GB more
resident, silently). `scripts/check` catches both, but catching is not
the same as not happening.

## Open question for implementation

`OLLAMA_HOST` takes one address, so "the tailnet address plus the
container bridge" cannot be expressed as a single bind. Resolve
empirically, preferring in this order:

1. Bind to the Docker bridge gateway alone, with the `maya-edge` subnet
   and gateway pinned in `compose.yaml` so the address is stable.
   Tailnet clients reach models through LibreChat, not directly — check
   whether `host.docker.internal` still resolves to that gateway.
2. Keep `0.0.0.0` and enable the macOS application firewall with Ollama
   allowed, which blocks unsolicited LAN inbound.
3. Keep `0.0.0.0` behind a `pf` rule permitting only the Docker subnets
   and the tailnet.

Whichever is chosen, record in `docs/PHASES.md` why the other two were
not, since a future reader will ask.

## Scope

- Narrow the bind so port 11434 is not reachable from a LAN machine
- Keep every container able to reach Ollama — Phase 1's checks must
  still pass unchanged
- Both settings applied by something that survives a reboot: a user
  LaunchAgent, not `launchctl setenv`
- `docs/PHASES.md` updated — the standing LAN-exposure note from story
  #9 is now closed, and says so

## Out of scope

Caddy. TLS. Any change to LibreChat.

## Acceptance criteria

1. `curl http://<LAN-IP>:11434/api/tags` from a machine on the LAN but
   not on the tailnet is refused or times out.
2. `docker run --rm curlimages/curl -fsS
   http://host.docker.internal:11434/v1/models` still returns both
   models.
3. `scripts/check phase1` passes in full, unchanged.
4. After a real reboot, `lsof -nP -iTCP:11434 -sTCP:LISTEN` shows the
   narrowed bind and `ollama ps` shows 32768 — with no manual step.
5. `docs/PHASES.md` records the chosen approach, the two rejected, and
   marks the story-#9 LAN exposure closed.
6. `scripts/check phase2` asserts the bind is not `0.0.0.0` and that the
   reboot-persistent mechanism is installed, and passes.
