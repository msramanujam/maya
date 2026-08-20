import json, sys, urllib.request
BASE = sys.argv[1]; tool = sys.argv[2]; args = json.loads(sys.argv[3])
sid = None
def call(payload):
    global sid
    h = {"Content-Type":"application/json","Accept":"application/json, text/event-stream"}
    if sid: h["Mcp-Session-Id"] = sid
    req = urllib.request.Request(BASE, data=json.dumps(payload).encode(), headers=h)
    with urllib.request.urlopen(req, timeout=180) as r:
        sid = r.headers.get("Mcp-Session-Id") or sid
        body = r.read().decode()
    for line in body.splitlines():
        if line.startswith("data: "): body = line[6:]; break
    try: return json.loads(body)
    except ValueError: return {"raw": body[:200]}
call({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"p","version":"1"}}})
h = {"Content-Type":"application/json","Accept":"application/json, text/event-stream","Mcp-Session-Id":sid}
urllib.request.urlopen(urllib.request.Request(BASE, data=json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}).encode(), headers=h), timeout=30)
out = call({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":tool,"arguments":args}})
res = out.get("result") or out
txt = json.dumps(res)
print(("ERROR " if res.get("isError") else "OK ") + txt[:1200])
