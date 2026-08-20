"""Call one tool on a stdio MCP server and print its result.

    docker exec -i maya-librechat python3 - <tool> <json-args> -- <server cmd...> \
      < scripts/lib/mcp-call.py

Prints "ERROR <json>" when the server reports isError, "OK <json>"
otherwise, so a caller can assert on either. Used by scripts/check to
prove the filesystem boundaries hold — that a write is refused, not just
that the mount says ro.
"""
import json, subprocess, sys

argv = sys.argv[1:]
sep = argv.index("--")
tool, raw_args = argv[0], argv[1]
cmd = argv[sep + 1:]


def m(obj):
    return (json.dumps(obj) + "\n").encode()


p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.DEVNULL)
p.stdin.write(m({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                 "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                            "clientInfo": {"name": "maya-check", "version": "1"}}}))
p.stdin.flush()
p.stdout.readline()
p.stdin.write(m({"jsonrpc": "2.0", "method": "notifications/initialized"}))
p.stdin.flush()
p.stdin.write(m({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                 "params": {"name": tool, "arguments": json.loads(raw_args)}}))
p.stdin.flush()

for _ in range(40):
    line = p.stdout.readline().decode()
    if not line:
        break
    try:
        d = json.loads(line)
    except ValueError:
        continue
    if d.get("id") == 2:
        res = d.get("result") or {}
        prefix = "ERROR " if res.get("isError") or "error" in d else "OK "
        print(prefix + json.dumps(d.get("result") or d.get("error"))[:600])
        break
p.kill()
