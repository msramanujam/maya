"""MCP server: web_search (discovery) and web_fetch (retrieval).

Two tools, deliberately. A single search-and-read tool makes the model
pull ten pages when it needed one, and floods the context doing it.
Search returns titles, URLs and snippets so the model can *choose*; fetch
returns one page's text.

Search goes through the stack's own SearXNG. Fetch strips boilerplate
with readability-lxml and caps its output — an uncapped fetch of a long
page is a context-window denial of service.

Run: uvx --with readability-lxml --with lxml_html_clean --with beautifulsoup4 \
       python server.py
"""
import json
import os
import sys
import re
import urllib.parse
import urllib.request

SEARXNG = os.environ.get("SEARXNG_URL", "http://maya-searxng:8080")
MAX_CHARS = int(os.environ.get("WEB_FETCH_MAX_CHARS", "40000"))
MAX_BYTES = 5_000_000        # stop reading the socket long before memory hurts
TIMEOUT = 30
UA = "Maya/1.0 (+local self-hosted assistant)"


def _get(url, accept="text/html"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read(MAX_BYTES).decode(resp.headers.get_content_charset() or "utf-8",
                                           errors="replace")
        return body, resp.geturl()


META_REFRESH = re.compile(
    r"""<meta[^>]+http-equiv=['"]?refresh['"]?[^>]*content=['"][^'"]*url=([^'";>]+)""",
    re.I,
)


def _get_following_meta_refresh(url, hops=3):
    """urllib follows HTTP redirects; it cannot see a meta refresh.

    Plenty of sites answer 200 with a "Click here to be redirected" stub —
    which extracts to nothing and looks exactly like a page that failed to
    parse. Follow those too, up to a small bound.
    """
    seen = []
    for _ in range(hops):
        body, final = _get(url)
        seen.append(final)
        m = META_REFRESH.search(body[:4000])
        if not m:
            return body, final
        url = urllib.parse.urljoin(final, m.group(1).strip())
        if url in seen:
            return body, final
    return body, final


def web_search(query, limit=8):
    url = SEARXNG + "/search?" + urllib.parse.urlencode({"q": query, "format": "json"})
    data = json.loads(_get(url, accept="application/json")[0])
    out = []
    for r in data.get("results", [])[:limit]:
        out.append({
            "title": (r.get("title") or "").strip(),
            "url": r.get("url"),
            "snippet": (r.get("content") or "").strip(),
        })
    if not out:
        return "No results for: %s" % query
    return "\n\n".join(
        "%d. %s\n   %s\n   %s" % (i, r["title"], r["url"], r["snippet"])
        for i, r in enumerate(out, 1)
    )


def web_fetch(url):
    if not url.lower().startswith(("http://", "https://")):
        raise ValueError("only http and https URLs can be fetched: %s" % url)
    html, url = _get_following_meta_refresh(url)

    from readability import Document
    from bs4 import BeautifulSoup

    # Strip structural navigation before readability sees it. Readability
    # scores by text density and happily keeps a Wikipedia navbox — a
    # wall of link text that reads as content and is not.
    pre = BeautifulSoup(html, "html.parser")
    for tag in pre(["script", "style", "noscript", "nav", "header", "footer",
                    "aside", "form", "iframe"]):
        tag.decompose()
    # Collect first, then remove: decomposing mid-iteration detaches
    # later matches and they come back with no attributes at all.
    NOISE = ("navbox", "infobox", "sidebar", "breadcrumb", "menu",
             "cookie", "banner", "footer", "navigation")
    total = len(pre.get_text(" ", strip=True)) or 1
    doomed = []
    for el in pre.find_all(True):
        attrs = getattr(el, "attrs", None) or {}
        classes = " ".join(attrs.get("class") or []).lower()
        hit = any(k in classes for k in NOISE) or \
            attrs.get("role") in ("navigation", "banner", "contentinfo")
        if not hit:
            continue
        # Never delete the element holding the article. Wikipedia's skin
        # wraps everything in containers whose classes say "menu" and
        # "navigation"; matching on class alone removed 232 elements and
        # left an empty document.
        if len(el.get_text(" ", strip=True)) > 0.3 * total:
            continue
        doomed.append(el)
    for el in doomed:
        el.decompose()

    def _readable(markup):
        """(title, text) via readability, or (None, None) if it gets nothing."""
        try:
            doc = Document(markup)
            body = BeautifulSoup(doc.summary(html_partial=True), "html.parser")
            for tag in body(["script", "style", "noscript"]):
                tag.decompose()
            return (doc.short_title() or "").strip(), body.get_text("\n")
        except Exception:
            return None, None

    # Cleaned first. Stripping navigation can empty a thin page entirely —
    # readability then raises "Document is empty" — so fall back to the
    # raw document, and to plain text stripping if even that fails. A
    # hostile page should degrade, not error.
    title, text = _readable(str(pre))
    if not text or len(text.strip()) < 200:
        t2, x2 = _readable(html)
        if x2 and len(x2.strip()) > len((text or "").strip()):
            title, text = t2, x2
    if not text:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        title, text = (soup.title.string.strip() if soup.title and soup.title.string else ""), soup.get_text("\n")

    lines = [ln.strip() for ln in text.splitlines()]
    text = "\n".join(ln for ln in lines if ln)

    if len(text) > MAX_CHARS:
        text = text[:MAX_CHARS] + (
            "\n\n[truncated at %d characters — fetch a more specific URL, "
            "or search for the part you need]" % MAX_CHARS
        )
    header = "# %s\n%s\n\n" % (title, url) if title else "%s\n\n" % url
    return header + text


TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Search the web and get back titles, URLs and snippets. Use this "
            "first to find out WHICH page answers a question. It does not "
            "return page contents — pick a URL from the results and pass it "
            "to web_fetch."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "description": "results to return, default 8"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "web_fetch",
        "description": (
            "Fetch one web page and return its readable text, with navigation "
            "and boilerplate stripped. Use it on a URL you already have — from "
            "web_search or from the user. Long pages are truncated."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
]

HANDLERS = {
    "web_search": lambda a: web_search(a["query"], int(a.get("limit", 8))),
    "web_fetch": lambda a: web_fetch(a["url"]),
}


def reply(msg_id, result=None, error=None):
    out = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        out["error"] = error
    else:
        out["result"] = result
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except ValueError:
            continue
        method, msg_id = req.get("method"), req.get("id")

        if method == "initialize":
            reply(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "maya-web", "version": "1.0.0"},
            })
        elif method == "tools/list":
            reply(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            params = req.get("params") or {}
            fn = HANDLERS.get(params.get("name"))
            if fn is None:
                reply(msg_id, error={"code": -32601,
                                     "message": "unknown tool: %s" % params.get("name")})
                continue
            try:
                reply(msg_id, {"content": [{"type": "text",
                                            "text": fn(params.get("arguments") or {})}]})
            except Exception as exc:
                reply(msg_id, {"content": [{"type": "text",
                                            "text": "%s: %s" % (type(exc).__name__, exc)}],
                               "isError": True})
        elif msg_id is not None:
            reply(msg_id, error={"code": -32601, "message": "unknown method: %s" % method})


if __name__ == "__main__":
    main()
