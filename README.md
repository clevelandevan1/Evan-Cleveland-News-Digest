# Morning Digest

Fetches new content from your feeds, summarizes each piece in 2–3 sentences with
Claude, groups everything by topic, and generates a clean newsletter-style page
to read over coffee. Stories you've already seen are hidden on future runs.

## Setup

```bash
cd ~/news-digest
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
```

## Run

```bash
# Preview the design with sample data — no key or network needed:
./.venv/bin/python -m app.digest --demo --open

# Real run (needs an API key, see below):
export ANTHROPIC_API_KEY=sk-ant-...
./.venv/bin/python -m app.digest --open
```

The page is written to `output/digest-YYYY-MM-DD.html`.

### Options

| Flag | Effect |
|------|--------|
| `--demo` | Render built-in sample data (no key/network). |
| `--open` | Open the finished page in your browser. |
| `--limit N` | Max entries fetched per feed (default 8). |
| `--no-summarize` | Skip Claude; show raw feed excerpts instead of AI summaries. |

## How it works

- `app/feeds.py` — your sources. **Edit this to add/remove feeds.**
- `app/fetch.py` — pulls and cleans entries from each feed.
- `app/store.py` — SQLite (`data/seen.db`) of already-seen article ids → no duplicates.
- `app/summarize.py` — batches new articles to Claude for a 2–3 sentence summary + topic.
- `app/render.py` — builds the newsletter HTML.
- `app/digest.py` — ties it together.

Stories are marked "seen" only *after* a page renders successfully, so a crash
never causes a story to be silently skipped the next day.

## The feeds

The URLs you follow are homepages, not RSS feeds, so each is mapped to its real
feed in `app/feeds.py`:

| You follow | Feed used |
|------------|-----------|
| nytimes.com | NYT HomePage RSS |
| apple.com/apple-news (no feed) | Apple Newsroom RSS |
| fox.com/news | Fox News latest RSS |
| cnn.com | CNN Top Stories RSS |

## Model / cost

Defaults to `claude-haiku-4-5` (fastest / cheapest, well-suited to a daily
digest). To trade cost for quality, change the `MODEL` constant in
`app/summarize.py` to `claude-sonnet-5` or `claude-opus-4-8` — no other changes
needed.

## Email delivery (optional)

The digest can be emailed to you each morning in addition to the local page.
Configure SMTP in your `.env` (see `.env.example`). For Gmail:

1. Enable 2-Step Verification on the Google account.
2. Create an [App Password](https://myaccount.google.com/apppasswords).
3. Put that app password in `SMTP_PASS`, and set `DIGEST_TO` to the recipient.

Then a normal run will also send the email. Disable per-run with `--no-email`.
If SMTP isn't fully configured, email is silently skipped and the page is still
written.

## Run it automatically each morning

Add a cron entry (runs at 7am daily) once your API key is available to the
environment:

```
0 7 * * * cd ~/news-digest && ANTHROPIC_API_KEY=sk-ant-... ./.venv/bin/python -m app.digest
```
