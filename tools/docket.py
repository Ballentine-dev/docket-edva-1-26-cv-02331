#!/usr/bin/env python3
"""Search this docket from a command line. Needs Python 3 and nothing else. Works in a clone, or alone, reading the public repository.

  docket.py menu [--filed-by Plaintiff]    what is on the docket, one line per paper
  docket.py get 90 [3-5]                   the exact text of ECF 90, optionally only those pages
  docket.py para 5 112-118                 paragraphs of a complaint (5 or 59-1)
  docket.py find "exact phrase"            every paper and page with that phrase
  docket.py search discovery scheduling    every paper and page with all of those words
  docket.py around 108                     the papers connected to ECF 108, and what decided it
  docket.py check 84 2 "quoted words"      are these exact words on that page of that paper?

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


def body(text):
    """A page's text without the court's page stamp or a bare page number, so a sentence can be followed across a page break."""
    lines = [l for l in text.split("\n") if not re.search(r"Document\s*\d+.*Filed\s*\d", l) and not re.fullmatch(r"\s*\d{1,3}\s*", l)]
    return "\n".join(lines)


def places(p, q):
    """Every place the words appear: a page, or two pages when the words cross a page break."""
    out, pages = [], p["pages"]
    for i, pg in enumerate(pages):
        if q in norm(pg["text"]):
            out.append(str(pg["page"]) if pg["page"] else "")
        elif i + 1 < len(pages) and q not in norm(pages[i + 1]["text"]) and q in norm(body(pg["text"]) + " " + body(pages[i + 1]["text"])):
            out.append(f"{pg['page']}-{pages[i + 1]['page']}")
    return out


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
            for at in places(p, q):
                hits += 1
                print(p["id"] + (f" at {at}" if at else ""))
        print(f"{hits} matches")
    elif cmd == "search":
        words, hits = [norm(w) for w in a[1:]], 0
        for p in load("master-docket.json")["papers"]:
            for pg in p["pages"]:
                t = norm(pg["text"])
                if all(re.search(r"\b" + re.escape(w), t) for w in words):
                    hits += 1
                    print(p["id"] + (f" at {pg['page']}" if pg["page"] else "") + f" | {p['description']}")
        print(f"{hits} pages match")
    elif cmd == "around":
        p = load(f"papers/{paper_id(a[1])}.json")
        print(f"{p['id']} | {p['date']} | {p['filed_by']} | {p['description']}")
        if p.get("decided_by"):
            print(f"\nDecided by: {p['decided_by']['id']} ({p['decided_by']['words']})")
        if p.get("decides"):
            print("\nDecides: " + "; ".join(f"{x['id']} ({x['words']})" for x in p["decides"]))
        for title, rows in (("Refers to", p["refers_to"]), ("Referred to by", p["referred_to_by"])):
            if rows:
                print(f"\n{title}:")
                for x in rows:
                    print(f"  {x['id']} | {x['description']} | words: {x['words']}")
        pre = p["id"] + "-"
        kin = [r for r in load("menu.json") if r["id"].startswith(pre) and r["id"] != p["id"]]
        if kin:
            print("\nSame filing:")
            for r in kin:
                print(f"  {r['id']} | {r['description']}")
    elif cmd == "check":
        pid, page, quote = paper_id(a[1]), a[2], norm(a[3])
        p = load(f"papers/{pid}.json")
        on = places(p, quote)
        if page in on or any(page in x.split("-") for x in on):
            print(f"FOUND: the words are on {p['cite']} at {next(x for x in on if page in x.split('-'))}.")
            return
        print(f"NOT FOUND on {p['cite']} at {page}." + (f" They are at {', '.join(x or 'an unpaged copy' for x in on)} in this paper." if on else " They are not in this paper's stored text."))
        print(f"Text source: {p['text_source']}. Scanned text can differ from the page, so check the docketed PDF before treating this as an error.")
        sys.exit(1)
    else:
        sys.exit(__doc__)


main(sys.argv[1:])
