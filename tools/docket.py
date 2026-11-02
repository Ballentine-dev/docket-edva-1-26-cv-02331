#!/usr/bin/env python3
"""Search this docket from a command line. Needs Python 3 and nothing else. Works in a clone, or alone, reading the public repository.

  docket.py menu [--filed-by Plaintiff]    what is on the docket, one line per paper
  docket.py get 90 [3-5]                   the exact text of ECF 90, optionally only those pages
  docket.py para 5 112-118                 paragraphs of a complaint (5 or 59-1)
  docket.py find "exact phrase"            every paper and page with that phrase

Output is the stored text, with nothing added and nothing summarized."""
import json, os, re, sys, urllib.request

RAW = "https://raw.githubusercontent.com/Ballentine-dev/docket-edva-1-26-cv-02331/main/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path):
    local = os.path.join(ROOT, path)
    if os.path.exists(local):
        return json.load(open(local, encoding="utf-8"))
    return json.load(urllib.request.urlopen(RAW + path))


def paper_id(q):
    q = q.strip()
    m = re.fullmatch(r"(?:ECF[- ]?(?:No\. ?)?)?(\d+)(?:-(\d+))?", q, flags=re.I)
    if m:
        return f"ECF-{int(m.group(1)):04d}" + (f"-{int(m.group(2)):02d}" if m.group(2) else "")
    return q


def wanted(spec):
    if not spec:
        return None
    a, _, b = spec.partition("-")
    return set(range(int(a), int(b or a) + 1))


def show(p, want=None):
    print(f"{p['cite']} | {p['date']} | Filed by: {p['filed_by']}\nDocket title: {p['docket_title']}\nStatus: {p['status']}\nText source: {p['text_source']}")
    for pg in p["pages"]:
        if want is None or pg["page"] in want:
            print(f"\n--- {p['cite']}" + (f" at {pg['page']}" if pg["page"] else "") + f" ---\n{pg['text']}")
    if not p["pages"]:
        print("\nThis paper has no stored text. The docket title above is all that is here.")


def norm(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).lower()


def main(a):
    if not a:
        sys.exit(__doc__)
    cmd = a[0]
    if cmd == "menu":
        who = a[a.index("--filed-by") + 1].lower() if "--filed-by" in a else None
        for r in load("menu.json"):
            if who is None or who in r["filed_by"].lower():
                print(f"{r['id']} | {r['date']} | {r['filed_by']} | {r['description']} | {r['page_count'] or '-'} pp | {r['words']} words")
    elif cmd == "get":
        show(load(f"papers/{paper_id(a[1])}.json"), wanted(a[2]) if len(a) > 2 else None)
    elif cmd == "para":
        doc = load(f"pleadings/{paper_id(a[1])}.json")
        want = wanted(a[2]) if len(a) > 2 else None
        for x in doc["paras"]:
            if want is None or x.get("n") in want:
                print(f"¶ {x['n']} (at {'-'.join(str(n) for n in x['pages'])}): {x['text']}\n")
    elif cmd == "find":
        q, hits = norm(a[1]), 0
        for p in load("master-docket.json")["papers"]:
            for pg in p["pages"]:
                if q in norm(pg["text"]):
                    hits += 1
                    print(p["id"] + (f" at {pg['page']}" if pg["page"] else ""))
        print(f"{hits} pages match")
    else:
        sys.exit(__doc__)


main(sys.argv[1:])
