# 文法練習 · N2 Grammar Practice

A small local web app for studying JLPT N2 grammar by writing your own sentences.

- **212 grammar points** with **2,494 example sentences** and English translations
- Write practice sentences for each point; they **autosave to plain text files** in `sentences/`
- **Furigana on hover** for the examples, and for the lines you write
- Study modes: hide the translations, or blank out the target grammar (cloze)
- A **grayscale switch** for when other people might see your screen

It runs on your own computer. Nothing is uploaded anywhere.

## Quick start

You need **Python 3.10+** (check with `python3 --version`) and any modern browser.

```bash
git clone https://github.com/hildahost3000/writing.git
cd writing

python3 setup_furigana.py   # one-time, optional: downloads the furigana dictionary (~77 MB)
python3 server.py           # starts the app and opens http://localhost:8765
```

On Windows use `py` instead of `python3`.

The app works without the furigana step. You just won't get readings. You can run
`setup_furigana.py` later at any time.

Stop the server with `Ctrl+C`. Start it again with `python3 server.py` whenever you want to study;
your sentences are still there.

Other ways to start it:

```bash
python3 server.py 9000       # use a different port
python3 server.py --no-open  # don't open the browser automatically
```

## Using it

Pick a grammar point on the left. You get its meaning and pattern, then the example sentences. Write your own
sentences in the **Your sentences** pane, one per line.

| Toolbar button | What it does |
| --- | --- |
| **Examples** | Show or hide the examples pane |
| **Translations** | Hide the English (hover a sentence to peek) |
| **Cloze** | Blank out the target grammar in each example (hover to peek) |
| **Furigana** | Cycles **Hover** (point at a word), **Always**, **Off** |

Hovering a line you wrote also shows a small card with the readings, unless Furigana is Off.
Drag the divider between the panes to resize it, or double-click it to reset.

| Shortcut | Action |
| --- | --- |
| `Ctrl+P` | Jump to any grammar point (number, Japanese or English) |
| `Alt+↑` / `Alt+↓` | Previous / next point |
| `Ctrl+S` | Save now (it also saves automatically) |
| `Ctrl+E` | Show or hide the examples |
| `Alt+G` | Grayscale on / off |
| `Ctrl+B` / `Ctrl+J` | Show or hide the list / the save log |

**Grayscale** is on the first time you open the app, and the app remembers your last choice in that browser.
The grammar highlight is also bold and underlined, so it stays visible without colour.

The sidebar filter understands numbers, Japanese, English, and the word `mine`, which shows the 24 points
that came from the original hand-made list (marked ◆).

### Where your sentences go

- `sentences/001_上.txt`, `sentences/019_ざるを得ない.txt`, and so on: one plain UTF-8 file per grammar point,
  one sentence per line. Edit them in any editor if you like.
- `all_sentences.md` is rebuilt on every save and collects everything into one readable list.

`sentences/` is your own work, so decide whether you want to commit it. If the repository is public,
your practice sentences would be public too.

If the server is stopped while you type, the page keeps your text in the browser, shows a red warning,
and saves to the folder as soon as the server is back.

## What's in the folder

| File | Purpose |
| --- | --- |
| `index.html` | The whole interface (one file, no build step) |
| `server.py` | Local server: serves the page, saves sentences, provides furigana. Python standard library only |
| `furigana.py` | Turns Japanese text into readings using SudachiPy |
| `grammar.json` | The grammar points and examples |
| `setup_furigana.py`, `requirements.txt` | Installs the furigana dictionary into `vendor/` |
| `sentences/` | Your practice sentences |
| `vendor/` | The furigana dictionary (about 200 MB, not committed) |

## Changing the grammar list

`grammar.json` is a list of objects. The server reads it on every request, so edit it and refresh the page.

```json
{"id": 19, "title": "ざるを得ない", "reading": "ざるをえない", "meanings": ["can't help doing"],
 "structure": ["Verb[ない] + ざるを得ない"], "level": "N2", "status": "New to you",
 "examples": [{"ja": "断ら{{ざるを得なかった}}。", "en": "I had no choice but to decline."}]}
```

- `ja` marks the target grammar with `{{ }}`.
- `id` must be unique. A point's file is named from its `id` and `title`, so **if you change either,
  rename the matching file in `sentences/`** or your old sentences will no longer show up.
- Required: `id`, `title`, `meanings`, `level`, `status`.
- Optional: `examples`, `reading`, `structure`, `nuance`, `notes`, `books`, `links`, `mine`.

## Troubleshooting

- **"Can't reach the save server"**: start `python3 server.py` and open the page at `http://localhost:8765`.
  Opening `index.html` straight from your file manager won't work.
- **"Could not start on port 8765"**: it's probably already running (check other terminal tabs), or something else
  uses that port. Try `python3 server.py 9000`.
- **No furigana appears**: the server prints `Furigana: ready` or `NOT available` when it starts.
  If it says NOT available, run `python3 setup_furigana.py`. Also check that the toolbar button isn't set to Off.
- **`setup_furigana.py` says no wheel matches**: use a standard Python from python.org or your OS, 3.10 or newer.
  Or run `pip install --target vendor -r requirements.txt` yourself.
- **A reading looks wrong**: readings are generated automatically, so an ambiguous kanji can occasionally get
  the wrong one. Check a dictionary if something looks off.

## Hosting it online

This is built to run on your own machine. It is not a fit for serverless hosts such as Vercel as-is: it saves to local
files, it has no login (anyone who could reach it could read and overwrite your sentences), and the examples are third-party
content (see below).

## Credits

- The grammar notes and example sentences come from the **Bunpro N2 (no media)** shared deck on AnkiWeb
  (<https://ankiweb.net/shared/info/368455348>). That content belongs to Bunpro and its contributors and is here for
  personal study. If you fork this repository, keep it private or remove `grammar.json`'s examples before making it public.
- Furigana uses [SudachiPy](https://github.com/WorksApplications/SudachiPy) and SudachiDict, both by Works Applications,
  under the Apache 2.0 licence.
