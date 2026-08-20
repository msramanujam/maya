# Playwright MCP with a real Chromium, in its own container.
#
# Not a prebuilt image because none was reachable from here, and not a
# subprocess of LibreChat because that image is Alpine/musl — Playwright's
# Chromium is glibc-only. Its own container is the better shape anyway:
# a browser is the most exposed thing in the stack and it gets no host
# mounts at all.
#
# Speaks streamable HTTP on 8931 over maya-internal, so no Docker socket
# is needed to start it — the rule that ruled out every off-the-shelf
# arrangement.
FROM node:22-bookworm-slim

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    NODE_ENV=production

# Pinned: `@latest` in a Dockerfile means the image quietly changes under
# you on every rebuild.
RUN npm install -g @playwright/mcp@0.0.41 && npm cache clean --force

# Install the browser with *this package's own* Playwright. Running
# `npx playwright@latest install` instead puts a differently-revisioned
# Chromium in /ms-playwright, and the server then fails at call time with
# "Browser specified in your config is not installed" while the container
# reports healthy. --with-deps pulls the system libraries; without them
# Chromium starts and dies with no useful error.
RUN cd /usr/local/lib/node_modules/@playwright/mcp \
    && node node_modules/playwright/cli.js install --with-deps chromium \
    && rm -rf /var/lib/apt/lists/*

# --allowed-hosts: the server refuses anything but the host it bound to,
# answering 403 "Access is only allowed at localhost:8931" — which
# LibreChat reports as a successful connection with undefined
# capabilities, not as a refusal. Named explicitly rather than '*': it is
# reachable only from maya-internal, and that is one fewer thing trusting
# the network alone.
#
# Chromium's own sandbox needs privileges this container does not have and
# should not get. The container is the sandbox: no host mounts, no socket,
# internal network.
ENTRYPOINT ["mcp-server-playwright", "--headless", "--no-sandbox", \
            "--browser", "chromium", "--host", "0.0.0.0", "--port", "8931", \
            "--allowed-hosts", "maya-browser:8931,maya-browser,localhost:8931", \
            "--output-dir", "/tmp/playwright-out"]
