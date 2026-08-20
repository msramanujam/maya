# Aider, confined to one repository.
#
# Chosen over OpenHands because OpenHands spawns runtime containers and
# needs the Docker socket to do it — a hard no under CLAUDE.md, and worse
# than it sounds: it would let a model-driven agent start privileged
# containers on the host. See docs/PHASES.md.
#
# Pinned. An agent that edits code and runs tests is the last thing that
# should change under you on a rebuild.
FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1 \
    GIT_PAGER=cat \
    AIDER_CHECK_UPDATE=false \
    HOME=/home/coder

# git because aider works through commits; build-essential because the
# test suites it runs may need to compile something.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 coder

# pytest so the agent has a test command to iterate against out of the
# box; a repository needing more installs it in its own environment.
RUN pip install --no-cache-dir aider-chat==0.86.1 pytest==8.3.4

USER coder
WORKDIR /repo

# Idle by default. The agent is driven by `scripts/maya-code`, which
# execs into it — a long-running process that edits code on a timer is
# not what anyone wants.
ENTRYPOINT ["sleep", "infinity"]
