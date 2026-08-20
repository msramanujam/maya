---
gh_issue: 21
gh_type: story
parent: FT-phase-2-remote-access
status: done
phase: 2
spec:
---

# Story: Tailscale CLI on PATH and a tailnet HTTPS certificate

## Problem

Caddy cannot terminate TLS without a certificate, and the only
certificate authority that will issue for this host is Tailscale's, for
the MagicDNS name `madhu-m3-mpb.tailadf0a2.ts.net`. Nothing else in
Phase 2 can start until that certificate exists.

The CLI is also not on PATH — it lives inside the app bundle at
`/Applications/Tailscale.app/Contents/MacOS/Tailscale`, which every
later script would otherwise have to hard-code.

## Blocking prerequisite

HTTPS certificates are **not enabled** on this tailnet:
`tailscale status --json` reports `CertDomains: None`. Enabling it is a
one-time toggle in the admin console under DNS → HTTPS Certificates,
which cannot be done from the CLI. The story is blocked until it is on.

## Scope

- `tailscale` on PATH (symlink into `/usr/local/bin`, needs sudo once)
- A certificate and key for the MagicDNS name, written somewhere Caddy
  can mount read-only — under `data/` (gitignored), never `config/`
- Renewal understood and recorded: what expires, when, and what renews
  it — a certificate that silently expires in 90 days is a Phase 2 bug
  waiting to happen
- `scripts/check` gains a `phase2` section asserting the certificate
  exists and is not near expiry

## Out of scope

Caddy itself. Any change to how LibreChat publishes. The Ollama bind.

## Acceptance criteria

1. `tailscale status` runs from a plain shell with no path prefix.
2. `tailscale cert` has produced a certificate and key for
   `madhu-m3-mpb.tailadf0a2.ts.net`, and
   `openssl x509 -noout -subject -dates` on it shows that name and a
   future expiry.
3. The certificate and key are under `data/`, and `git status` shows
   neither as untracked or staged.
4. `docs/PHASES.md` records where the certificate lives, when it
   expires, and how renewal happens.
5. `scripts/check phase2` asserts the certificate exists and has more
   than 14 days left, and passes.
