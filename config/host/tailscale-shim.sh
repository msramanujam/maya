#!/usr/bin/env bash
# Puts `tailscale` on PATH without moving the binary.
#
# A symlink does not work: the CLI lives inside Tailscale.app and derives
# its bundle identity from its own path, so invoking it through a link in
# /opt/homebrew/bin dies with
#   "Fatal error: The current bundleIdentifier is unknown to the registry"
# exec'ing the real path keeps the binary where it expects to be.
#
# Installed by scripts/install-host-env.
exec /Applications/Tailscale.app/Contents/MacOS/Tailscale "$@"
