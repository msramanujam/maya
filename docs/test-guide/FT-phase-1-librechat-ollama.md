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

### Step 1.2 — Ollama is not open to your network

Paste:

    lsof -nP -iTCP:11434 -sTCP:LISTEN

**Pass:** the last part of the line reads `127.0.0.1:11434`.

**Fail:** it reads `*:11434` or an address starting with `192.168` or
`100.`. That means the models are answering to your whole network. Fix
it with:

    launchctl unsetenv OLLAMA_HOST

then quit the Ollama app (click the menu-bar icon → Quit), open it
again, and repeat this step.

`127.0.0.1` means "this Mac only". Maya's containers still reach the
models through it — that is step 1.3 — but nothing else on your Wi-Fi
can.

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

### Step 1.4 — Nobody else can reach the models

Find this Mac's address on your network:

    ipconfig getifaddr en0

Then try to reach the models at that address — substitute the number it
printed:

    curl -m 5 http://192.168.1.23:11434/api/tags

**Pass:** it fails — "Failed to connect" or "Could not connect to
server" after a few seconds.

**Fail:** a wall of text listing the models. That means anyone on the
same Wi-Fi can use them. Go back to step 1.2.

Maya deliberately keeps the models to this Mac. Reaching them from
another device is what Phase 2 is for, over your private Tailscale
network rather than the local Wi-Fi.

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

Open **https://madhu-m3-mpb.tailadf0a2.ts.net** in your browser. This
works from this Mac and from any of your other devices, as long as
Tailscale is running on both.

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

Sign up at https://madhu-m3-mpb.tailadf0a2.ts.net, then close it again:

    cd ~/Dev/maya
    sed -i '' 's/^ALLOW_REGISTRATION=true$/ALLOW_REGISTRATION=false/' .env
    ./scripts/maya up

Use `./scripts/maya up` both times, never `restart`. Restarting reuses
the container's old settings, so the change appears to have worked while
signup quietly stays open. Accounts that already exist are never affected
by any of this — the setting controls signup, not login.

### Step 2.5 — Your devices can reach it, nobody else can

Two halves to this.

**It should work from your own devices.** On a phone, tablet, or another
computer with Tailscale installed and switched on, open
https://madhu-m3-mpb.tailadf0a2.ts.net

**Pass:** the Maya login screen, with a padlock and no security warning.
This works from anywhere — home Wi-Fi, a café, or mobile data — because
Tailscale carries it, not the local network.

Turn Tailscale off on that device and reload. **Pass:** it now fails to
connect.

**It should not work for anyone else.** From a device on the same Wi-Fi
*without* Tailscale, get this Mac's local address:

    ipconfig getifaddr en0

and open `http://<that address>:3080` and `https://<that address>` in a
browser.

**Pass:** both fail to connect.

**Fail:** either shows Maya. That means the interface is on your local
network when it should only be on your private Tailscale network. Stop
and report it.

### Step 2.6 — Stopping and restarting

Paste:

    cd ~/Dev/maya && ./scripts/maya down

then:

    cd ~/Dev/maya && ./scripts/maya up

Reload https://madhu-m3-mpb.tailadf0a2.ts.net and log in.

**Pass:** your account still exists and the same password works. Nothing
was lost by stopping the stack.

---

## 3. Talking to a model

**What this proves.** The chat interface can reach the models on this
Mac, and a conversation works end to end.

### Step 3.1 — The models appear

Log in at https://madhu-m3-mpb.tailadf0a2.ts.net and open the model picker at the top of
a new chat.

**Pass:** four choices are listed under **Maya** — `general`, `fast`,
`coding` and `reasoning`.

These are nicknames, not models. `general` is the big model for normal
conversation, `fast` is a small quick one used for chat titles, and
`coding` and `reasoning` are reserved for later phases. Which actual
model sits behind each nickname can be changed without touching anything
you see here.

**Fail:** the list is empty or the picker is missing. Paste
`cd ~/Dev/maya && ./scripts/maya logs librechat` and look for
`Invalid custom config file`.

Nothing lists these models by hand — Maya asks Ollama what it has. Run
`ollama pull <some-model>` and it shows up here after a reload.

### Step 3.2 — Ask it something

Pick `general` and send:

    In one sentence: what is the capital of France?

**Pass:** a sensible sentence naming Paris.

Answers normally come back in a few seconds. The very first message
after restarting the Mac is slower — sometimes a few minutes — because
the 31 GB model is being read from disk. There is no progress bar while
that happens, so it can look frozen. It is not; wait it out. After that
first load the model stays in memory and every later message is quick.

Nothing is sent over the internet; the answer is computed on this Mac.

**Fail:** an error banner, or it hangs past a minute. Check the menu-bar
Ollama icon is there, then see step 1.3.

### Step 3.3 — The conversation names itself

Look at the conversation list on the left after that first answer.

**Pass:** the conversation has a short title about France or capitals,
not "New chat".

The title is written by whatever is behind the `fast` nickname — a small
quick model, on purpose. Using the big one would make you wait twice for
the first answer.

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

    cd ~/Dev/maya && ./scripts/install-host-env

then quit the Ollama app from the menu bar and open it again. An empty
list just means no model is loaded right now; send a chat message and
run it again.

That command installs a small login item so the setting comes back by
itself after a restart. You should only ever need to run it once.

**Worth knowing.** That setting is a memory trade. At 32768 the big model
occupies about 31 GB while loaded; at its maximum of 262144 it takes
about 46 GB. Both fit on this machine. If you routinely hit the limit in
step 4.1, it can be raised — the cost is roughly 15 GB for the full jump.

### Step 4.3 — Nothing is lost on restart

Note the title of a conversation in the left sidebar. Then paste:

    cd ~/Dev/maya && ./scripts/maya down

Wait for it to finish, then:

    cd ~/Dev/maya && ./scripts/maya up

Reload https://madhu-m3-mpb.tailadf0a2.ts.net and log in.

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

---

## 5. What Maya can do now

Everything below happens in a normal conversation — no setup, no
switching modes. Ask in plain language; Maya decides which tool it needs.

### Tools

    What time is it in Tokyo?
    List the files in my Documents folder.
    Read /projects/maya/docs/fixtures/sample.pdf and tell me what it says.
    Search the web for the latest Apple silicon benchmarks and summarise them.
    Open https://quotes.toscrape.com/js/ and tell me the first quote.

The last one needs the browser, because that page builds itself with
JavaScript and a plain fetch sees nothing. Maya should reach for the
browser only when a simple fetch will not do — it is much slower.

### What it cannot do

- **Write to your Documents folder.** Read-only, deliberately. Ask it to
  write there and it will tell you it cannot.
- **See anything outside Documents and Dev.** No other part of your disk
  is visible to it.
- **Reach the models from another machine.** Only Maya's own containers
  can.

### The coding agent

Separate, and deliberately kept away from everything above. It can see
exactly one folder — whatever `CODING_REPO` points at in `.env` — and
nothing else.

    cd ~/Dev/maya
    ./scripts/maya-code "add a --verbose flag and a test for it"

It edits files, runs the tests, and shows you the diff. It does **not**
commit: read the change before you keep it.

**Watch it honestly.** Given a task it cannot satisfy, it may make the
tests pass by breaking the code rather than admitting defeat — during
this build it did exactly that, replacing a function's return value with
an object that claims to equal everything. Read the diff, not the test
output.

