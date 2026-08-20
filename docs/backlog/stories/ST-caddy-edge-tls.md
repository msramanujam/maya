---
gh_issue: 22
gh_type: story
parent: FT-phase-2-remote-access
status: in-progress
phase: 2
spec:
---

# Story: Caddy on the edge profile, terminating TLS for the tailnet

## Problem

LibreChat publishes `127.0.0.1:3080` in plain HTTP, which is why Maya is
reachable from this Mac and nowhere else. Reaching it from a phone or a
second machine needs a service that terminates TLS on the tailnet
address — and CLAUDE.md reserves port publishing for exactly one
service, the edge proxy. This is that service.

## Scope

- Caddy container on the `edge` profile, `maya-edge` network
- Caddyfile in `config/caddy/`, serving the MagicDNS name with the
  tailnet certificate from `ST-tailscale-cert-and-cli`, mounted
  read-only
- Reverse proxy to `librechat:3080` over `maya-internal`
- Caddy publishes on the Tailscale address only —
  `100.92.97.39:443` — never `0.0.0.0`
- LibreChat stops publishing a port and drops off `maya-edge`, back to
  `maya-internal` alone
- `scripts/maya` default profile set becomes `core edge`
- LibreChat told its public origin so links and cookies are right

## Out of scope

The Ollama bind. Authentication beyond what Phase 1 already closed.
Serving anything other than LibreChat.

## Acceptance criteria

1. `https://madhu-m3-mpb.tailadf0a2.ts.net` loads LibreChat from a
   second device on the tailnet, with a certificate the browser accepts
   and no warning.
2. The same URL loads from a phone on cellular with Tailscale on, and
   fails to connect with Tailscale off.
3. `docker compose ps --format '{{.Names}} {{.Publishers}}'` shows Caddy
   publishing on `100.92.97.39` only, and LibreChat publishing nothing.
4. `curl http://<LAN-IP>:3080` from a machine on the LAN but not on the
   tailnet is refused.
5. Logging in and holding a two-message conversation works over the
   HTTPS URL, and the conversation is the same one visible on
   `127.0.0.1`.
6. `scripts/check phase2` covers criteria 3 and passes, and
   `scripts/check phase1` still passes in full.
