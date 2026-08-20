---
gh_issue: 10
gh_type: story
parent: FT-phase-1-librechat-ollama
status: ready
phase: 1
spec:
---

# Story: Compose scaffold — LibreChat and MongoDB on the core profile

## Problem

There is no compose file. The stack needs a structure that all seven
phases can extend without turning into a pile of overlay files.

## Scope

- `compose.yaml` with a `core` profile: `mongo:7` and
  `ghcr.io/danny-avila/librechat:latest`
- Mongo: volume at `./data/mongo`, no published port
- LibreChat: published on `127.0.0.1:3080` only, with
  `extra_hosts: ["host.docker.internal:host-gateway"]` so the compose
  file is not OrbStack-specific
- `.env.example` (committed, shape only) and `.env` (gitignored) with
  `CREDS_KEY`, `CREDS_IV`, `JWT_SECRET`, `JWT_REFRESH_SECRET` generated
  via `openssl rand -hex`
- `scripts/maya` wrapper: `up`, `down`, `logs`, `status`, composing the
  active profile set
- Phase-later profiles named but empty: `edge`, `gateway`, `tools`,
  `web`, `browser`, `coding`

## Out of scope

The Ollama endpoint configuration (`ST-librechat-ollama-endpoint`).
Meilisearch, the RAG API, and every other optional LibreChat service.

## Acceptance criteria

1. `docker compose config` parses with no error and no warning.
2. `./scripts/maya up` starts exactly two containers, both reaching a
   healthy or running state.
3. `http://127.0.0.1:3080` serves the LibreChat UI and an account can be
   registered.
4. `docker compose ps --format '{{.Names}} {{.Publishers}}'` shows Mongo
   publishing nothing and LibreChat publishing only on `127.0.0.1`.
5. `curl http://<LAN-IP>:3080` from another machine is refused.
6. `git status` shows `.env` untracked and `data/` ignored.
7. `scripts/check phase1` covers criteria 1, 2, 4 and passes.
