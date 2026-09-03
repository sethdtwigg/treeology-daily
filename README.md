# Treeology Catechism App

A mobile-ready Progressive Web App (PWA) for daily review of the Treeology Theology catechism from [Mount Calvary Baptist Church](https://www.mountcalvarybaptist.org/treeology/). Install it to your phone's home screen and work through all 91 questions at your own pace — one catechism per day, or spread each one across as many days as you like.

---

## About the Catechism

The **Treeology Theology** catechism was developed by [Mount Calvary Baptist Church](https://www.mountcalvarybaptist.org) beginning in 2017. It draws heavily from the rich tradition of Reformed catechisms, particularly the **Westminster Shorter Catechism**, and is designed to ground believers in foundational Christian doctrine through memorization and scripture.

The catechism consists of **91 questions and answers**, each accompanied by supporting scripture passages. A special **Thanksgiving catechism** is also included for seasonal use.

All catechism content is the property of Mount Calvary Baptist Church. This app is an unofficial personal study tool and is not affiliated with or endorsed by the church. Visit their website for the original materials: [mountcalvarybaptist.org/treeology](https://www.mountcalvarybaptist.org/treeology/)

---

## Features

- 📖 **Daily catechism** — automatically shows the right catechism for today based on your start date and pace
- 🧠 **Quiz mode** — question shown first, tap to reveal the answer
- 📄 **Reading mode** — question and answer displayed together
- 📜 **Scripture references** — all supporting passages included and expandable
- ✅ **Daily review tracking** — mark each day as reviewed
- ⚙️ **Fully configurable** — set how many days to spend on each catechism, where to start, and display preferences
- 📋 **Browse all 91** — scroll the full list with completion status and upcoming dates
- ⬅️➡️ **Step between catechisms** — prev/next arrows on the card, in either mode
- 🔗 **Linkable questions** — every card has its own URL, and the back button works
- 💾 **Backup and restore** — export your progress to a file and move it to another device
- 🍂 **Thanksgiving special** — bonus catechism surfaced automatically in November
- 📻 **Best-effort daily reminder** — optional local notification at your chosen time
- 📡 **Works offline** — service worker caches everything after first load
- 📱 **Installable** — add to your iPhone or Android home screen as a full-screen app

---

## Setup

`catechisms.json` is already committed, so **you do not need to run the scraper to use the app** — skip to "Serve the app". The scraper is only for regenerating the data from source.

### Prerequisites

- Python 3.9+
- `pip install -r requirements.txt` (`pypdf`, pinned; `requests` for `download.py`)
- Node 18+ if you want to run the tests

### Serve the app

```bash
python -m http.server 8080
```

Then open `http://localhost:8080`. Use `localhost`, not `file://` — service workers
and the Notification API both require a secure context.

**Hosted (recommended for phone use):** See the [Deployment](#deployment) section below.

---

## Regenerating the data

> **Read this before running `scraper.py`.** The pipeline is not currently
> reproducible: re-parsing the same cards with the pinned `pypdf==6.16.2`
> produces **220** scripture passages where the committed `catechisms.json` has
> **249**, and questions 30, 60, 61 and 86 come back with none at all. The
> committed file was generated with an older, unrecorded pypdf version and has
> since been hand-repaired. Regenerating will **lose data** unless you diff the
> result entry by entry first.

```bash
pip install -r requirements.txt
python download.py      # fetch the 92 card PDFs into Catechism_PDFs/ (once)
python scraper.py       # parse them into catechisms.json
python validate_data.py # check for extraction damage
```

`download.py` writes into `Catechism_PDFs/`; `scraper.py` reads from there and
only falls back to the network for cards that are missing. Both write next to
the script, not into the current working directory. `scraper.py` refuses to
overwrite `catechisms.json` if any card fails, and logs every scripture it
skips to stderr.

### Why `validate_data.py` exists

PDF text extraction is imperfect and the source cards contain overlapping text
layers, so extraction silently produces damage that renders verbatim in the
app. Real examples that shipped: question 31's answer repeated one phrase 38
times across 5,716 characters; eight cards had whole teaching paragraphs
swallowed into the one-line italic attribution; `"offered"` came through as
`"off ered"`. `validate_data.py` fails on all of these plus the structural
invariants (92 entries, contiguous numbering, non-empty answers, and so on).

### Running the tests

```bash
node --test
```

Covers the schedule math in `schedule.js` — cycle rollover, `startFromQ`
offsets, future start dates, end-of-list clamping, and DST transitions.

---

## File Structure

```
treeology_daily/
├── index.html           ← The app (HTML + CSS + JS)
├── schedule.js          ← Schedule math, split out so it can be unit-tested
├── schedule.test.mjs    ← Tests for the above (`node --test`)
├── sw.js                ← Service worker for offline support
├── manifest.json        ← PWA manifest for home screen installation
├── _headers             ← Cloudflare Pages cache rules
├── catechisms.json      ← The catechism content — required for the app to run
├── fonts/               ← Self-hosted Playfair Display + EB Garamond
├── icon-192.png         ← Referenced by manifest.json
├── icon-512.png         ← Referenced by manifest.json
├── apple-touch-icon.png ← iOS home screen icon
├── download.py          ← Fetches the card PDFs into Catechism_PDFs/
├── scraper.py           ← Parses those PDFs into catechisms.json
├── validate_data.py     ← Checks catechisms.json for extraction damage
├── requirements.txt
└── README.md
```

---

## Deployment

### GitHub + Cloudflare Pages (recommended)

1. Push this repository to GitHub (private repo is fine)
2. Go to [pages.cloudflare.com](https://pages.cloudflare.com) → Create a project → Connect to Git
3. Select your repository
4. Set **Framework preset** to `None`, leave build command and output directory blank
5. Deploy — you'll get a URL like `https://your-app.pages.dev`

Any `git push` to `main` will trigger an automatic redeployment in ~30 seconds.

> **Bump `CACHE_VERSION` in `sw.js` whenever you change `index.html`, `schedule.js`,
> or the fonts.** The service worker serves the app shell cache-first, so without
> a bump, installed clients keep running the old version indefinitely.
> `catechisms.json` is the exception — it is fetched network-first, so data
> changes ship without a bump.
>
> `_headers` keeps Cloudflare from edge-caching `sw.js` and `catechisms.json`;
> without it the edge can hand out a stale worker and defeat the version bump.

### Install to your phone

**iPhone (Safari):**
1. Open your app URL in Safari
2. Tap the Share button → **Add to Home Screen**
3. Tap **Add**

**Android (Chrome):**
1. Open your app URL in Chrome
2. Tap the three-dot menu → **Add to Home screen**

---

## Settings

All settings are stored locally on your device (`localStorage`). Nothing is sent to any server.

| Setting | Default | Description |
|---|---|---|
| Days per catechism | 3 | How many days before advancing to the next question |
| Start date | Today | The day you began — used to calculate which catechism is current |
| Start from # | 1 | Jump into the series at any question number |
| Backup | — | Export/restore settings and review history as a JSON file |
| Default to reading mode | Off | Show answer immediately instead of requiring a tap |
| Show scriptures expanded | Off | Open the scripture list by default |
| Daily reminder | Off | Best-effort local notification at a chosen time — see below |

### Backing up your progress

Everything lives in this browser's `localStorage`. Clearing site data, switching
phones, or reinstalling **destroys your progress with no recovery** — so
Settings → Backup is worth using before any of those.

- **Save a Backup File** downloads `treeology-backup-<date>.json`.
- **Copy Backup to Clipboard** does the same via the clipboard. Use this on an
  installed iPhone app, where Safari tends to open a downloaded JSON in a viewer
  rather than saving it.
- **Restore from a Backup** replaces your current settings and history, after a
  confirmation naming both counts.

```json
{
  "version": 1,
  "exportedAt": "2026-09-03T16:37:06.410Z",
  "settings": {
    "daysPerCatechism": 5, "startDate": "2026-01-15", "startFromQ": 12,
    "defaultMode": "read", "scriptureOpen": true,
    "notifEnabled": false, "notifTime": "07:00"
  },
  "reviewedDates": { "2026-09-01": true, "2026-09-02": true }
}
```

Two honest limits. Review history older than **400 days** is pruned on import,
and the app reports how many entries it dropped. And a backup cannot carry
notification *permission* — if you had reminders on, you may need to re-grant
permission on the new device.

### Linking to a question

| URL | Opens |
|---|---|
| `#today` | today's scheduled catechism |
| `#browse` | the full list |
| `#settings` | settings |
| `#q=40` | catechism 40 |
| `#q=thanksgiving` | the Thanksgiving card |

Opening a specific question is a **temporary view** — it shows a "Back to Today"
banner and never changes your place in the schedule. An unknown question or an
unrecognised route falls back to today. Because each view is a real history
entry, the Android back button steps back through the app instead of leaving it.

### How the daily catechism is calculated

```
current_question = startFromQ + floor(daysSinceStart ÷ daysPerCatechism)
```

`startFromQ` is a catechism **number**, resolved to a position in the sorted list
at lookup time, so the schedule stays correct even if the data ever gains a gap.
`daysSinceStart` is counted in whole calendar days through `Date.UTC`, so it is
unaffected by daylight-saving transitions. Simple, deterministic, and entirely
offline — no server, no account, no sync.

### Reminders are best-effort

The daily reminder uses an in-app timer (`setTimeout`), not a push server. That means:

- It only fires while the app is open in the foreground, or shortly after it was last active.
- Phones suspend background web apps aggressively — **iOS will usually not deliver the reminder** if the app was closed.
- Reliable scheduled delivery would require Web Push with a small backend (VAPID keys + a push service), which this app intentionally avoids to stay 100% serverless and private.

---

## Catechism JSON Format

Each entry in `catechisms.json` follows this structure:

```json
{
  "number": 1,
  "question": "What is the chief end of man?",
  "answer": "The chief end of man is to glorify God and to enjoy Him forever.",
  "scriptures": [
    {
      "reference": "Rom. 11:36",
      "translation": "NASB",
      "text": "For from Him and through Him and to Him are all things..."
    }
  ],
  "attribution": "(Westminster Shorter Catechism, Q. 1)"
}
```

The Thanksgiving entry uses `"number": "thanksgiving"` and is excluded from the regular daily rotation.

---

## Credits

**Catechism content:** [Mount Calvary Baptist Church](https://www.mountcalvarybaptist.org), Treeology Theology series (2017–present). All catechism questions, answers, and scripture selections are their work. Audio recordings of all 91 questions are also available on their website.

**Historical source material:** The Westminster Shorter Catechism (1647) and other Reformed catechisms from which the Treeology catechism draws.

---

## License

The **app code** (HTML, CSS, JavaScript, Python scripts) is released under the MIT License.

The **catechism content** (`catechisms.json`) belongs to Mount Calvary Baptist Church and is used here for personal study only. Do not redistribute the content commercially or without attribution.
