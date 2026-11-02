# Ballentine v. Hall, No. 1:26-cv-02331 (E.D. Va.)

The docket of this federal case as plain JSON. Anyone can read it, download it, or point an AI tool at it. No account or key is needed.

These are court filings. Allegations in them are not findings.

## Using it with an AI tool

Give your tool this repository's address, or paste this:

> Read https://raw.githubusercontent.com/Ballentine-dev/docket-edva-1-26-cv-02331/main/menu.md. It lists every paper in Ballentine v. Hall. To read a paper, open https://raw.githubusercontent.com/Ballentine-dev/docket-edva-1-26-cv-02331/main/papers/ID.json, replacing ID with the paper's ID from the menu, such as ECF-0084. Read only the papers you need. Each paper lists the papers connected to it under refers_to and referred_to_by. Answer from their text and cite the ECF number and page.

## What is here

| File | What it holds |
|---|---|
| `menu.md`, `menu.json` | One row per paper: ID, date, who filed it, a short description, pages, words |
| `papers/` | One file per paper, with the text page by page |
| `pleadings/` | The two complaints paragraph by paragraph, with their own menu |
| `links.json` | Which papers refer to which, with the words each link rests on |
| `master-docket.json` | Every paper in one file, for download or search |
| `case.json` | Court, judges, parties |
| `tools/docket.py` | Command-line lookup; needs only Python 3 |

```
python3 tools/docket.py menu --filed-by Plaintiff
python3 tools/docket.py get 84
python3 tools/docket.py get 84 2
python3 tools/docket.py para 5 112-118
python3 tools/docket.py find "exact phrase"
python3 tools/docket.py search discovery scheduling
python3 tools/docket.py around 108
python3 tools/docket.py check 84 2 "discovery officially begins"
```

The tool also runs by itself, reading this repository over the web.

## Paper IDs

- `ECF-0084` is ECF No. 84. `ECF-0007-02` is its second attachment.
- `NoNumber-...` is a docket row with no number and no document.
- `PKG-04-1` is the first paper of a package submitted November 1, 2026. `NOH-A` is a notice of hearing submitted November 2, 2026. These are awaiting docketing and have no ECF number yet. Their text is the paper as prepared. It will be replaced with the docketed text once ECF numbers exist.

## Each paper's fields

`id`, `cite`, `date`, `filed_by`, `description`, `docket_title`, `status`, `text_source`, `page_count`, `words`, `refers_to`, `referred_to_by`, `decided_by` and `decides` where they apply, and `pages` (each with `page` and `text`).

## Links between papers

Each paper's file lists the papers it refers to and the papers that refer to it, so opening one order shows what surrounds it. The links come from the words of the docket and the papers, and those words are stored with each link. They show that one paper names another, not what it argues. A paper can discuss another without a link appearing here, because the links do not come from reading each paper's body.

`decided_by` records twelve motions whose deciding order was confirmed from the order's words. A blank does not mean a motion is pending. Check the docket for that.

## How far to rely on the text

The docket controls. `text_source` says where each paper's text came from: CourtListener's copy of the docketed PDF, a scan of it, or Plaintiff's file copy. Scanned text can carry page stamps and reading errors, so check a quotation against the docketed PDF before relying on it. The menu's descriptions are pointers for finding a paper and are not a source. Docket entries run through ECF No. 108, as of November 2, 2026.

Docket on CourtListener: https://www.courtlistener.com/docket/73709501/ballentine-v-hall/
