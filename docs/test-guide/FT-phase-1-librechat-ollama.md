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

## 2. Starting Maya and creating your account

**What this proves.** The chat interface starts, keeps its data on this
Mac, and is reachable from this Mac only.

### Step 2.1 — First-time setup (once, ever)

Skip this if you have run Maya before. Paste:

    cd ~/Dev/maya && ls .env

If it prints `.env`, you are set — skip to step 2.2. If it says `No such
file`, paste these two blocks, one at a time:

    cd ~/Dev/maya && cp .env.example .env

    cd ~/Dev/maya && printf 'CREDS_KEY=%s\nCREDS_IV=%s\nJWT_SECRET=%s\nJWT_REFRESH_SECRET=%s\n' \
      "$(openssl rand -hex 32)" "$(openssl rand -hex 16)" \
      "$(openssl rand -hex 32)" "$(openssl rand -hex 32)" >> .env

**Pass:** no output, no error. That file holds this machine's private
keys. It is never uploaded and never committed.

### Step 2.2 — Start it

Paste:

    cd ~/Dev/maya && ./scripts/maya up

The very first run downloads about 1 GB and takes a few minutes. Later
runs take seconds.

**Pass:** a small table appears at the end with two rows — `maya-mongo`
and `maya-librechat` — and the STATUS column says `Up` for both. The
first minute may say `health: starting`; that is fine.

**Fail:** `Cannot connect to the Docker daemon` — Docker/OrbStack is not
running. Or `no .env` — go back to step 2.1.

### Step 2.3 — Open the interface

Open **http://127.0.0.1:3080** in your browser.

**Pass:** a login screen appears.

**Fail:** "This site can't be reached". Wait a minute — LibreChat takes
up to 45 seconds on a cold start — then reload. Still nothing: paste
`cd ~/Dev/maya && ./scripts/maya logs librechat` and send what appears.

### Step 2.4 — Log in

Enter the email and password of the account on this machine and submit.

**Pass:** you land in the chat interface.

There is no model to talk to yet — that is the next story. An empty chat
screen at this stage is the correct result.

**Signing up is deliberately closed.** Clicking Sign up and submitting
gives "Registration is not allowed." Maya is a single-user stack, and
Phase 2 puts this interface on your Tailscale network — an open signup
form on a reachable machine is exactly what that phase is meant to
prevent.

To create an account anyway — a fresh install with no account yet, or a
second person — takes three steps:

    cd ~/Dev/maya
    sed -i '' 's/^ALLOW_REGISTRATION=false$/ALLOW_REGISTRATION=true/' .env
    ./scripts/maya up

Sign up at http://127.0.0.1:3080, then close it again:

    cd ~/Dev/maya
    sed -i '' 's/^ALLOW_REGISTRATION=true$/ALLOW_REGISTRATION=false/' .env
    ./scripts/maya up

Use `./scripts/maya up` both times, never `restart`. Restarting reuses
the container's old settings, so the change appears to have worked while
signup quietly stays open. Accounts that already exist are never affected
by any of this — the setting controls signup, not login.

### Step 2.5 — Nobody else can reach it

Maya is bound to this Mac alone. From a **different** device on the same
Wi-Fi, open `http://<this-Mac's-IP>:3080` in a browser.

To get that IP, paste on this Mac:

    ipconfig getifaddr en0

**Pass:** the other device fails to connect — "can't be reached",
"connection refused", or a spinner that gives up.

**Fail:** the other device shows the Maya login screen. That means the
interface is on your network when it should not be. Stop and report it.

Note the contrast with step 1.4: the *models* on port 11434 are open to
your network, deliberately. The *chat interface* on port 3080 is not.

### Step 2.6 — Stopping and restarting

Paste:

    cd ~/Dev/maya && ./scripts/maya down

then:

    cd ~/Dev/maya && ./scripts/maya up

Reload http://127.0.0.1:3080 and log in.

**Pass:** your account still exists and the same password works. Nothing
was lost by stopping the stack.

---

## 3. Talking to a model

**What this proves.** The chat interface can reach the models on this
Mac, and a conversation works end to end.

### Step 3.1 — The models appear

Log in at http://127.0.0.1:3080 and open the model picker at the top of
a new chat.

**Pass:** both models are listed —
`orcarouter/Qwen3.8-27B-Uncensored:q8_0` and `qwen3:0.6b`, under
**Ollama**.

**Fail:** the list is empty or the picker is missing. Paste
`cd ~/Dev/maya && ./scripts/maya logs librechat` and look for
`Invalid custom config file`.

Nothing lists these models by hand — Maya asks Ollama what it has. Run
`ollama pull <some-model>` and it shows up here after a reload.

### Step 3.2 — Ask it something

Pick `orcarouter/Qwen3.8-27B-Uncensored:q8_0` and send:

    In one sentence: what is the capital of France?

**Pass:** a sensible sentence naming Paris.

The first message after starting the stack takes 10–30 seconds — the
27-billion-parameter model is being loaded into memory. Later messages
are much faster. Nothing is being sent over the internet; the answer is
computed on this Mac.

**Fail:** an error banner, or it hangs past a minute. Check the menu-bar
Ollama icon is there, then see step 1.3.

### Step 3.3 — The conversation names itself

Look at the conversation list on the left after that first answer.

**Pass:** the conversation has a short title about France or capitals,
not "New chat".

The title is written by the small `qwen3:0.6b` model, on purpose — using
the big one would make you wait twice for the first answer.

---

## 4. Memory, long chats, and restarts

**What this proves.** Maya remembers the start of a long conversation,
and nothing is lost when you stop and restart it.

### Step 4.1 — A long conversation still remembers its beginning

In a new chat, send a message that starts with a fact and then pads it
out — paste a few pages of any text after it. Something like:

    Remember this passphrase: BRASS-LANTERN-47.

    <paste several pages of any text here>

Send a second message:

    What was the passphrase in my first message?

**Pass:** it answers `BRASS-LANTERN-47`.

**Fail:** it says it does not know, or invents a different passphrase.
That means the conversation outgrew the memory window — see step 4.2.

### Step 4.2 — How much conversation Maya holds

Maya is set to hold about 32,000 tokens of conversation — very roughly
24,000 words, or fifty pages. Past that, the oldest messages fall out of
view and step 4.1 starts failing.

To see what a loaded model is using, paste:

    ollama ps

**Pass:** the CONTEXT column reads `32768`.

**Fail:** it reads `262144`, or the command prints only a header. If it
reads 262144, the setting was lost — this happens after restarting the
Mac. Fix with:

    launchctl setenv OLLAMA_CONTEXT_LENGTH 32768

then quit the Ollama app from the menu bar and open it again. An empty
list just means no model is loaded right now; send a chat message and
run it again.

**Worth knowing.** That setting is a memory trade. At 32768 the big model
occupies about 31 GB while loaded; at its maximum of 262144 it takes
about 46 GB. Both fit on this machine. If you routinely hit the limit in
step 4.1, it can be raised — the cost is roughly 15 GB for the full jump.

### Step 4.3 — Nothing is lost on restart

Note the title of a conversation in the left sidebar. Then paste:

    cd ~/Dev/maya && ./scripts/maya down

Wait for it to finish, then:

    cd ~/Dev/maya && ./scripts/maya up

Reload http://127.0.0.1:3080 and log in.

**Pass:** the same conversation is in the sidebar, and opening it shows
the whole exchange — your messages and the replies.

**Fail:** the sidebar is empty, or the conversation opens blank. Stop and
report it; conversations live in `data/mongo` and should survive any
stop and start.

---

## Everything at once

To run every automated check in one go, paste:

    cd ~/Dev/maya && scripts/check

**Pass:** the last line reads `N passed, 0 failed`.

One of those checks tries to sign up and expects to be turned away, so
seeing `registration refused` in the output is the good result.

If you run this straight after `./scripts/maya up`, it may pause for up
to a minute and then print `maya-librechat healthy (after 45s)`. That is
it waiting for LibreChat to finish starting, not a problem.

**Fail:** any line starting with `FAIL`. The text after it says which
check failed; find the matching section above.
