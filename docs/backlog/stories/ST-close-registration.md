---
gh_issue: 15
gh_type: story
parent: FT-phase-2-remote-access
status: done
phase: 2
spec:
---

# Story: Close open registration

## Problem

LibreChat shipped in Phase 1 with `ALLOW_REGISTRATION=true`, so the
first account could be created. That account now exists. Every further
signup is an unwanted one: Phase 2 puts this UI on the tailnet, and an
open signup form on a reachable host is exactly what
`FT-phase-2-remote-access` calls out.

Pulled forward from Phase 2 rather than waiting for the Caddy and
Tailscale work, because the account exists now and the window costs
nothing to close.

## Scope

- `ALLOW_REGISTRATION=false` in `.env.example`, with the comment
  explaining why and how to re-open it for a second account
- Same flip in the running `.env`
- `scripts/check` asserts registration is refused
- Test guide section 2.4 rewritten: the reader logs in rather than
  signs up, with the re-open instructions for a fresh install

## Out of scope

Everything else in Phase 2 — Tailscale, Caddy, TLS, the MagicDNS
certificate, and narrowing the Ollama bind. Social and email login
settings beyond the registration flag.

## Acceptance criteria

1. `POST /api/auth/register` with a new, valid, unused email is
   rejected — a non-2xx status, and no new row in `db.users`.
2. The existing account still logs in through the UI at
   `http://127.0.0.1:3080` and its conversations are intact.
3. `db.users.countDocuments({})` is unchanged by criterion 1.
4. `.env.example` carries `ALLOW_REGISTRATION=false` and states how to
   re-open registration for a second account.
5. `scripts/check phase1` covers criterion 1 and passes in full.
