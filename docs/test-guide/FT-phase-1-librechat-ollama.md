# Test guide — Phase 1: LibreChat + Ollama

Follow the steps in order. Each section ends with a clear pass/fail
signal. You do not need to know anything about this repo — just open
Terminal (press ⌘-Space, type `Terminal`, press Return) and paste the
commands exactly as written.

Sections are added as Phase 1 stories land.

---

## 1. Ollama is reachable from containers

**What this proves.** The AI models run directly on this Mac, but
everything else in Maya runs inside Docker containers. Containers can
only reach the models if Ollama accepts connections from outside the Mac
itself. This section checks that it does.

**Before you start.** Docker (OrbStack) must be running, and the Ollama
app must be running — look for the llama icon in the menu bar at the top
of the screen. If it is not there, open Ollama from Applications.

### Step 1.1 — Ollama answers on this Mac

Paste:

    curl http://localhost:11434/api/tags

**Pass:** a wall of text appears, and somewhere in it you can see
`Qwen3.8-27B-Uncensored` and `qwen3:0.6b`.

**Fail:** you see `Failed to connect` or `Connection refused`. Ollama is
not running — start the Ollama app and try again.

### Step 1.2 — Ollama is not locked to this Mac only

Paste:

    lsof -nP -iTCP:11434 -sTCP:LISTEN

**Pass:** the last part of the line reads `*:11434`.

**Fail:** it reads `127.0.0.1:11434`. That means Ollama is still locked
to this Mac only and containers cannot reach it. Fix it with:

    launchctl setenv OLLAMA_HOST 0.0.0.0:11434

then quit the Ollama app (click the menu-bar icon → Quit) and open it
again, and repeat this step. Note: this needs redoing after every
restart of the Mac.

### Step 1.3 — A container can reach the models

This starts a tiny throwaway container that asks Ollama what models it
has. The first run takes about a minute while Docker downloads it.

Paste:

    docker run --rm curlimages/curl -fsS http://host.docker.internal:11434/v1/models

**Pass:** a line of text appears containing both
`orcarouter/Qwen3.8-27B-Uncensored:q8_0` and `qwen3:0.6b`.

**Fail:** you see `curl: (7) Failed to connect` — go back to step 1.2.
If you see `Cannot connect to the Docker daemon`, Docker/OrbStack is not
running; start it and try again.

### Step 1.4 — Know what you have opened up

There is nothing to fix here — this step just shows you the current
state, so it holds no surprises.

Paste:

    /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

Expect: `Firewall is disabled. (State = 0)`.

**This is on purpose.** Steps 1.2 and 1.3 opened the models to your
whole local network, and the macOS firewall was deliberately left off in
front of it. Until Phase 2 lands, anyone on the same Wi-Fi — home,
office, or a shared network — can list these models and chat with them,
with no password. Nothing else on this Mac is opened up: only the model
port.

If you want that closed before Phase 2, ask for it and it takes a
minute. The reasoning and both fixes are written down in
`docs/PHASES.md` under "Host Ollama bind".

---

## Everything at once

To run every automated check in one go, paste:

    cd ~/Dev/maya && scripts/check

**Pass:** the last line reads `N passed, 0 failed`.

**Fail:** any line starting with `FAIL`. The text after it says which
check failed; find the matching section above.
