---
gh_issue: 32
gh_type: bug
parent: EP-maya-v1
status: in-progress
phase: 3
spec:
---

# Bug: single-file bind mounts break when git rewrites the file

## Symptom

`/app/librechat.yaml` does not exist inside `maya-librechat`, while
`docker inspect` still lists the mount and the container is healthy:

    $ docker exec maya-librechat ls -la /app/librechat.yaml
    ls: /app/librechat.yaml: No such file or directory

    $ docker inspect maya-librechat -f '{{range .Mounts}}...'
    /Users/msramanujam/Dev/maya/config/librechat/librechat.yaml -> /app/librechat.yaml (ro)

## Cause

A single-file bind mount binds an inode, not a path. Git does not edit
files in place — it writes and renames — so `git checkout`, `git pull`
and a merge all replace the inode. The mount is then pointing at a file
that no longer exists, and the container sees nothing there.

It is silent. LibreChat read its config at startup and keeps serving from
memory, so nothing fails until the next restart, which is the worst time
to discover it. Merging #30 and pulling `main` is what did it here.

Every config in the stack is mounted this way: `librechat.yaml`,
`Caddyfile`, `litellm/config.yaml`. Caddy and LiteLLM have not been hit
only because their files have not been rewritten since those containers
started.

## Scope

- Mount the containing directory rather than the file, for all three
  services, read-only
- Adjust in-container paths to match
- `scripts/check` asserts each container can actually read its config,
  rather than trusting that a mount is listed

## Out of scope

Anything about the contents of those configs.

## Acceptance criteria

1. `docker exec <service> cat <config path>` succeeds for LibreChat,
   Caddy and LiteLLM.
2. After `git checkout` of a branch that rewrites a config file, with
   the stack left running, the same three commands still succeed.
3. `scripts/check` fails if any container cannot read its config, and
   passes now.
4. Phases 1, 2 and 3 pass in full.
