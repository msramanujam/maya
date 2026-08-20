"""Speak MCP to a stdio server and print its tool names, comma-separated.

Used by scripts/check. Piped into the container's python3 rather than
copied in — `docker exec -i ... python3 - <cmd...> < this file` — so
there is nothing to clean up and no image to rebuild.

Empty output means the server never answered tools/list, which is the
failure worth catching: a server that starts but advertises nothing is
indistinguishable, from the model's side, from one that is not there.
"""
import json, subprocess, sys

cmd = sys.argv[1:]


def msg(obj):
    return (json.dumps(obj) + "\n").encode()


p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=subprocess.DEVNULL)
p.stdin.write(msg({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
               "clientInfo": {"name": "maya-check", "version": "1"}},
}))
p.stdin.flush()
p.stdout.readline()                      # initialize result
p.stdin.write(msg({"jsonrpc": "2.0", "method": "notifications/initialized"}))
p.stdin.flush()
p.stdin.write(msg({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}))
p.stdin.flush()

names = ""
for _ in range(20):
    line = p.stdout.readline().decode()
    if not line:
        break
    try:
        d = json.loads(line)
    except ValueError:
        continue                          # servers log noise on stdout
    if d.get("id") == 2:
        names = ",".join(sorted(t["name"] for t in d["result"]["tools"]))
        break

p.kill()
print(names)
