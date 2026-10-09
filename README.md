# 文法練習 · N2 Grammar Practice

A small app for studying JLPT N2 grammar by writing your own sentences. It works in **any browser**, either as a
plain file you open (no install) or with a tiny local server that keeps your sentences as real files.

- **212 grammar points** with **2,494 example sentences** and English translations
- A goal of **10 sentences per point**, with progress rings, a daily streak and a "next point" button to keep you going
- A **phone layout** (one screen at a time, tap for furigana) and optional **sync across your devices** on the hosted site
- A **Review tab** where your teacher can correct your sentences, with the changes highlighted
- **Furigana on hover** for the examples (and for the lines you write, with the server)
- Study modes: hide the translations, or blank out the target grammar (cloze)
- A **grayscale switch** for when other people might see your screen

Nothing is uploaded anywhere: your sentences stay on your computer.

## Quick start

Pick one. Both give you the same app.

### A. Just open it (no install, any browser)

```bash
git clone https://github.com/hildahost3000/writing.git
```

Then double-click **`index.html`** in the `writing` folder. That's it: no Python, no server.

Your sentences are saved **in your browser**, so use **💾 Backup** (top right) now and then to download a copy.
See [Saving](#saving) for how it works and what to watch out for.

### B. With the local server (real files in a folder, furigana on your own sentences)

You need **Python 3.10+** (check with `python3 --version`). On Windows use `py` instead of `python3`.

```bash
cd writing
python3 setup_furigana.py   # one-time, optional: downloads the furigana dictionary (~77 MB)
python3 server.py           # starts the app and opens http://localhost:8765
```

Your sentences are saved as plain text files in `sentences/`. Stop the server with `Ctrl+C`; start it again whenever
you want to study. The app works without the furigana step; you just won't get readings on lines you write yourself.

```bash
python3 server.py 9000       # use a different port
python3 server.py --no-open  # don't open the browser automatically
```

The page works out which way it's running when it loads: if `server.py` is running it uses the folder, otherwise it
uses the browser. The header shows which (`⚡ localhost:8765` or `💾 Saved in this browser`).

| | A. Open the file | B. Local server |
| --- | --- | --- |
| Needs | Nothing | Python 3.10+ |
| Where sentences live | Your browser's storage | `sentences/` (plain `.txt` files) |
| Backup | You download one (💾 Backup) | They're already files |
| Furigana on the examples | Yes | Yes |
| Furigana on lines you write | No | Yes (needs `setup_furigana.py`) |

## Using it

Pick a grammar point on the left. You get its meaning and pattern, then the example sentences. Write your own
sentences in the **Your sentences** pane, one per line.

### Saving

Your sentences **save automatically** a moment after you stop typing. The **Save** button in the practice header shows
the state of the point you're on: yellow **Save** when something is unsaved, **✓ Saved** once it's stored (hover it for
where and when). Click it, or press `Ctrl+S`, to save immediately.

**If you open the file (A)**, sentences live in your browser's storage on that computer. That's fast and private, but:

- Clearing the site's data (or using a private window) erases them. Download a **💾 Backup** now and then; the status
  bar turns yellow when you have work that isn't backed up yet.
- Safari may clear a site's storage after about a week without a visit. If you use Safari, back up regularly.
- If you open `index.html` by double-clicking it, **don't move or rename the folder afterwards**. Some browsers, such as
  Firefox, may tie saved sentences to the file's location. A backup restores them anyway. If double-clicking ever doesn't
  keep your sentences in your browser, use option B (the local server) or host it on a website; both are reliable.
- Different browsers and different computers don't share sentences. Move them with Backup → Restore.

**💾 Backup** menu: *Download backup* (one `.json` with everything), *Download all sentences* (a readable `.md`),
*Download this point* (one `.txt`), and *Restore from backup…*. Restore accepts a backup `.json`, or the `.txt` files from the
server edition's `sentences/` folder, so you can move between A and B at any time.

**If you run the server (B)**, sentences are written to:

- `sentences/001_上.txt`, `sentences/019_ざるを得ない.txt`, and so on: one plain UTF-8 file per grammar point,
  one sentence per line. Edit them in any editor if you like.
- `all_sentences.md`: rebuilt on every save, collects everything into one readable list.
- `sentences/.progress.json`: how many sentences you added each day. It drives the streak; delete it to reset the streak.
- `sentences/.reviews.json`: your teacher's corrections (see below). Keep it if you want to keep her notes.

`sentences/` is your own work, so decide whether you want to commit it. If the repository is public, your practice
sentences would be public too. If the server is stopped while you type, the page keeps your text and saves to the
folder as soon as the server is back.

### The 10-sentence goal

- The practice pane shows **10 ruled slots**. Each sentence you write gets a ✓ and fills one segment of the meter
  above it. A sentence is any line with at least 3 characters.
- At 10/10 you get a short celebration and a **Next point →** button. Keep writing for bonus sentences (`10/10 +3`).
- In the list, each point has a ring that fills as you go and turns into a ✓ when done. The filter buttons
  (**To do / Started / Done**) show only points in that state.
- The top bar shows your overall progress, your **🔥 streak** (days in a row with at least one new sentence; it stays
  alive until the day ends, so you have all of today to keep it going) and **today's** count against a daily target of 10.
- Want a different goal? Change `GOAL` (sentences per point) or `DAILY` (daily target) at the top of the script
  in `index.html`.

| Toolbar button | What it does |
| --- | --- |
| **Examples** | Show or hide the examples pane |
| **Translations** | Hide the English (hover a sentence to peek) |
| **Cloze** | Blank out the target grammar in each example (hover to peek) |
| **Furigana** | Cycles **Hover** (point at a word), **Always**, **Off** |

Drag the divider between the panes to resize it, or double-click it to reset.

| Shortcut | Action |
| --- | --- |
| `Ctrl+P` | Jump to any grammar point (number, Japanese or English) |
| `Alt+N` | Jump to the next point you haven't finished |
| `Alt+↑` / `Alt+↓` | Previous / next point |
| `Ctrl+S` | Save now (it also saves automatically) |
| `Ctrl+E` | Show or hide the examples |
| `Alt+G` | Grayscale on / off |
| `Ctrl+B` / `Ctrl+J` | Show or hide the list / the save log |

**Grayscale** is on the first time you open the app, and the app remembers your last choice in that browser.
The grammar highlight is also bold and underlined, so it stays visible without colour.

The sidebar filter understands numbers, Japanese, English, `mine` (the 24 points from the original hand-made list,
marked ◆), and `todo`, `wip` or `done`.

### Teacher corrections

For a tutoring session on the same device, there's no account or login. On a point's page, open the **Review** tab (next to
**Write**).

- **You** see each sentence you wrote with its status: *Not reviewed*, *✓ Correct* or *Needs a fix*. A correction shows
  exactly what changed (removed text struck through, added text underlined, so it also reads in grayscale), plus your teacher's
  note. **Use this correction** replaces the sentence in your list with one tap. If you simply type the corrected sentence
  yourself, it counts as fixed too. Applied corrections are kept in a "learned from" log under the list.
- **Your teacher** switches on **✍ Teacher mode** (top right of the Review tab). For each sentence she can tap **✓ Correct**, or
  **✎ Correct it…** to edit a copy of the sentence (with a live preview of what changed) and add an optional note. Your original
  is never overwritten until you choose to apply the correction. Teacher mode switches off when you go back to **Write**.
- The Review tab shows a count of corrections you haven't dealt with yet, and the list shows **✎2** next to points that have
  some. Type `fix` in the list filter to see only those points.

Corrections are saved with everything else. With the server they go to `sentences/.reviews.json`; in the browser edition they
are kept in the browser, included in **Backup / Restore** (and listed in the `.md` export), and synced with **☁ Sync**. If two
devices change the same correction, the most recent change wins.

### On your phone

On a narrow screen the app shows **one screen at a time**, switched from the bar at the bottom: **List** (pick a point),
**Examples** (read the notes and sentences) and **Write** (your ten slots). Use ‹ › at the top to move to the previous or
next point. Because a touch screen has no hover, **tap a word** to see its furigana, and **tap a sentence** to peek at its
translation or the hidden grammar (when Translations is off or Cloze is on). The text area is sized so iPhones don't zoom
in, and the layout shrinks to fit when the keyboard opens.

### Sync across your devices

If you use the hosted site (see below), **☁ Sync** keeps your sentences the same on your phone and your computers.

- On your first device: **☁ Sync → Create a sync code**. Save the code somewhere safe (a password manager).
- On another device: open the site, **☁ Sync → I already have a code** and paste it. Or choose **Copy link for another
  device** on the first one and open that link on the other; it connects with one confirmation.
- After that it's automatic: your changes upload a few seconds after you stop typing, and the other devices pick them up
  when you open the site again (or press **Sync now**). It works offline too and catches up when you're back online.

How it behaves: it's **local-first**, so everything still works without a connection and your sentences are always on the
device too. If two devices changed the **same point** differently, you get **every distinct sentence from both** (nothing is
lost). If only one device changed it, that version wins, including deletions. The daily counts and streak add up across
devices.

Privacy: your sentences are stored on the site's server (Vercel Blob) under a key derived from your sync code. The code itself
is never stored, and **anyone who has it can read and change your sentences**, so keep it private. If you lose the code and
all your devices, the cloud copy can't be recovered. **Turn off on this device** stops syncing there and keeps your sentences.

The sync button only appears where the site has the sync service (the Vercel deployment). It doesn't appear when you open
the file directly, on GitHub Pages, or with the local server.

## What's in the folder

| File | Purpose |
| --- | --- |
| `index.html` | The whole interface (one file, no build step) |
| `data/grammar.js` | The grammar points, examples and ready-made furigana, for running without a server |
| `api/sync.js`, `api/_core.js`, `package.json` | The optional sync service for the Vercel deployment (stores one small document per sync code in Vercel Blob) |
| `vercel.json`, `.vercelignore` | Deployment settings: only `index.html`, `data/` and `api/` are published |
| `grammar.json` | The same grammar points, as editable source |
| `build_static.py` | Rebuilds `data/grammar.js` from `grammar.json` |
| `server.py` | Optional local server: saves real files, serves furigana. Python standard library only |
| `furigana.py` | Turns Japanese text into readings using SudachiPy |
| `setup_furigana.py`, `requirements.txt` | Installs the furigana dictionary into `vendor/` |
| `sentences/` | Your practice sentences (server edition) |
| `vendor/` | The furigana dictionary (about 200 MB, not committed) |

## Changing the grammar list

`grammar.json` is a list of objects:

```json
{"id": 19, "title": "ざるを得ない", "reading": "ざるをえない", "meanings": ["can't help doing"],
 "structure": ["Verb[ない] + ざるを得ない"], "level": "N2", "status": "New to you",
 "examples": [{"ja": "断ら{{ざるを得なかった}}。", "en": "I had no choice but to decline."}]}
```

- `ja` marks the target grammar with `{{ }}`.
- `id` must be unique. In the server edition a point's file is named from its `id` and `title`, so **if you change
  either, rename the matching file in `sentences/`**. In the browser edition your sentences are keyed by `id`, so changing
  an `id` hides what you wrote under the old one.
- Required: `id`, `title`, `meanings`, `level`, `status`. Optional: `examples`, `reading`, `structure`, `nuance`, `notes`,
  `books`, `links`, `mine`.

The server reads `grammar.json` on every request, so just refresh. **The file-only edition reads `data/grammar.js`**, so after
editing run `python3 build_static.py` (it needs the furigana dictionary, because it works out the readings for every example).

## Putting it on a website

Because the page can run without a server, any static host works: GitHub Pages (Settings → Pages → deploy from the
`main` branch, root folder) or Vercel (import the repository, framework preset **Other**, no build command). There's nothing
to configure; the host just serves `index.html` and `data/grammar.js`.

- Each visitor's sentences stay in **their own browser** unless they turn on ☁ Sync, which stores them under their own secret code.
  Nobody can read or change anyone else's.
- **Sync needs a Vercel Blob store** connected to the project (`vercel blob create-store <name> --access private`, which adds
  `BLOB_READ_WRITE_TOKEN`). On Vercel's free Hobby plan Blob is free within its limits (2,000 writes and 10,000 reads a month);
  Vercel pauses access rather than charging if you go over, and your sentences stay safe on each device. The app writes
  only after you stop typing, at most about once every 90 seconds. GitHub Pages and other plain hosts work too, just without ☁ Sync.
- The site is public: anyone with the link can see the grammar notes and examples. If you'd rather keep it to yourself, use
  a private deployment or a host with a password.
- `server.py`, `grammar.json` and anything committed under `sentences/` would be public too, so keep your own sentences out of git.

## Troubleshooting

- **"Couldn't load the grammar data"**: `data/grammar.js` has to sit next to `index.html` (don't copy `index.html` elsewhere
  on its own). If it's missing, run `python3 build_static.py`, or use the server (`python3 server.py`).
- **My sentences vanished (opened the file)**: the browser's storage was cleared, you're in a private window, or the folder
  was moved or renamed. Restore from your latest backup: 💾 Backup → *Restore from backup…*.
- **I used the server before and now my sentences aren't showing (opened the file)**: they're in `sentences/`, not in the
  browser. In 💾 Backup choose *Restore from backup…* and select the `.txt` files from `sentences/`.
- **☁ Sync says "No synced sentences were found for that code"**: check the code for typos (dashes and capitals don't
  matter). If this is your first device, use **Create a sync code** instead.
- **☁ Sync shows "Offline" or "Sync service problem"**: your sentences are safe on this device and it retries every minute.
  A persistent service problem can mean the Blob store's monthly limit was reached; it resets after 30 days.
- **"Could not start on port 8765"**: it's probably already running (check other terminal tabs), or something else
  uses that port. Try `python3 server.py 9000`.
- **No furigana on my own lines**: that needs the server and the dictionary. Run `python3 setup_furigana.py`, start
  `python3 server.py`, and check that the toolbar button isn't set to Off. The server prints `Furigana: ready` or
  `NOT available` when it starts.
- **`setup_furigana.py` says no wheel matches**: use a standard Python from python.org or your OS, 3.10 or newer.
  Or run `pip install --target vendor -r requirements.txt` yourself.
- **A reading looks wrong**: readings are generated automatically, so an ambiguous kanji can occasionally get
  the wrong one. Check a dictionary if something looks off.

## Credits

- The grammar notes and example sentences come from Bunpro's N2 material, via the **Bunpro N2 (no media)** shared deck on
  AnkiWeb (<https://ankiweb.net/shared/info/368455348>). They're used here for personal study, not commercially. Thanks to
  Bunpro and the deck's contributors.
- Furigana uses [SudachiPy](https://github.com/WorksApplications/SudachiPy) and SudachiDict, both by Works Applications,
  under the Apache 2.0 licence.
