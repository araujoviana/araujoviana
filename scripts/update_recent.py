#!/usr/bin/env python3
"""Rewrite the block between <!-- recent starts --> and <!-- recent ends --> in README.md
with my most recently pushed public repos that carry the TOPIC topic (default: featured).
Set TOPIC="" to skip the topic filter (useful for testing)."""
import datetime, json, os, re, sys, urllib.request

USER = os.environ.get("GH_USER", "araujoviana")
TOPIC = os.environ.get("TOPIC", "featured")
LIMIT = int(os.environ.get("LIMIT", "4"))
README = os.environ.get("README", "README.md")

def fetch():
    url = f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&per_page=100"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    repos = [r for r in fetch()
             if not r["fork"] and not r["archived"] and not r["private"]
             and r["name"].lower() != USER.lower()
             and (not TOPIC or TOPIC in r.get("topics", []))]
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)
    items = []
    for r in repos[:LIMIT]:
        d = datetime.date.fromisoformat(r["pushed_at"][:10])
        items.append(f"[{r['name']}]({r['html_url']}) *({d.strftime('%b')} {d.day})*")
    block = " · ".join(items) if items else "_Nothing to show yet._"
    text = open(README, encoding="utf-8").read()
    new, n = re.subn(r"(<!-- recent starts -->\n).*?<!-- recent ends -->",
                     lambda m: m.group(1) + block + "\n<!-- recent ends -->", text, flags=re.S)
    if n != 1:
        sys.exit("markers not found in README")
    if new != text:
        open(README, "w", encoding="utf-8").write(new)
        print("README updated")
    else:
        print("no change")

main()
