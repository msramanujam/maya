#!/usr/bin/env bash
# One-time: create the label set this repo's workflow depends on.
# Idempotent — re-running updates colours/descriptions, never errors.
# See docs/specs/001-dev-workflow.md.
set -euo pipefail

REPO="${MAYA_REPO:-msramanujam/maya}"

label() {
  local name="$1" colour="$2" desc="$3"
  gh label create "$name" --repo "$REPO" --color "$colour" \
    --description "$desc" --force >/dev/null
  echo "  $name"
}

command -v gh >/dev/null || { echo "gh CLI not installed"; exit 1; }
gh auth status >/dev/null 2>&1 || {
  echo "gh is not authenticated. Run: gh auth login"; exit 1;
}

echo "Creating labels on $REPO"

echo "type:"
label "type:epic"    "6f42c1" "A body of work spanning multiple features"
label "type:feature" "0e8a16" "A phase or capability; parent of stories"
label "type:story"   "1d76db" "One Claude Code session of work"
label "type:bug"     "d73a4a" "Defect; needs a BG- backlog file"

echo "status:"
label "status:proposed"    "ededed" "Written down, not yet agreed as next work"
label "status:ready"       "0e8a16" "Agreed, has acceptance criteria, can start"
label "status:in-progress" "fbca04" "A branch exists and a session is on it"
label "status:blocked"     "b60205" "Two review cycles failed or externally stalled"
label "status:done"        "5319e7" "Merged, checks green, test guide current"

echo "phase:"
label "phase:1" "c5def5" "LibreChat + Ollama"
label "phase:2" "c5def5" "Tailscale + Caddy + auth hardening"
label "phase:3" "c5def5" "LiteLLM gateway + model aliases"
label "phase:4" "c5def5" "MCP foundation + scoped filesystem"
label "phase:5" "c5def5" "Search + fetch (SearXNG)"
label "phase:6" "c5def5" "Interactive browser (Playwright)"
label "phase:7" "c5def5" "Coding agent + model specialization"

echo
echo "Done. Verify with: gh label list --repo $REPO"
