---
gh_issue: 3
gh_type: feature
parent: EP-maya-v1
status: ready
phase: 2
spec:
---

# Feature: Phase 2 — Remote access (Tailscale + Caddy + auth hardening)

## Problem

Phase 1 is localhost-only, and its Ollama bind change opened port 11434
to the LAN. Maya needs to be reachable from the owner's other devices —
including off-network — without being reachable by anything else, and
without an open-registration app sitting on a now-reachable host.

## Scope

- Tailscale started and signed in; CLI symlinked to `/usr/local/bin`
- Tailnet HTTPS certificate for the machine's MagicDNS name
- Caddy container (profile `edge`) terminating TLS, proxying to
  LibreChat; LibreChat stops publishing a port
- Caddy's published port bound to the Tailscale interface address, not
  `0.0.0.0`
- Ollama bind narrowed from `0.0.0.0` to the tailnet address plus the
  container bridge
- `ALLOW_REGISTRATION=false`; confirmation that no example secrets remain

## Out of scope

Public internet exposure of any kind. Multi-user accounts. SSO.

## Acceptance criteria

1. The MagicDNS URL loads LibreChat over HTTPS with a valid certificate
   from a second device on the tailnet.
2. The same URL loads from a phone on cellular with Tailscale on, and
   fails with Tailscale off.
3. `curl http://<LAN-IP>:3080` from a LAN machine not on the tailnet is
   refused, and so is `curl http://<LAN-IP>:11434/api/tags`.
4. Registering a new account through the UI is rejected.
5. `scripts/check phase2` passes and covers criteria 3 and 4.

## Stories

- `ST-tailscale-cert-and-cli` (#21)
- `ST-caddy-edge-tls` (#22)
- `ST-narrow-ollama-bind` (#23)
