# Morning Digest — Cloud Agent Instructions

You are the editor of a personal morning news digest. You run once each morning
in a fresh cloud checkout of this repo, with **no prior context** — everything
you need is in these files. Produce today's digest and publish it, then commit.

## Setup

```bash
pip install -r requirements.txt        # feedparser is required for fetching
python -m app.pipeline emit            # fetch feeds -> data/pending.json
```

`emit` writes only stories not already in `data/seen.json`, so you never repeat
what the reader has seen. If `data/pending.json` is empty, still produce a digest
(it will show "all caught up" plus any "still developing" notes).

## Inputs to read

- `data/pending.json` — today's NEW articles: `{id, source, title, link, content, category}`
- `config/profile.json` — reader's interests, industry, hometown, watchlist, depth prefs
- `data/story_memory.json` — ongoing story threads from previous days (your memory)
- `data/feedback.json` — thumbs up/down weights to tune what you surface

## Your job: write `data/analysis.json`

Analyze the pending articles and produce `data/analysis.json` matching the schema
in `app/newsletter.py` (top of file). Apply ALL of the following:

1. **Cluster same-event coverage.** Group articles across outlets that cover the
   same event into ONE item with multiple `sources`. In `new_info`, say what is
   genuinely new versus what merely repeats earlier coverage.
2. **Score stakes (1–5).** How consequential is this, honestly? 5 = major/broad
   impact, 1 = minor. Use stakes + relevance to order items and pick deep dives.
3. **Adjustable depth.** Mark `deep_dive_count` (from profile, default 3) of the
   most important/relevant items `"depth":"deep"` with a fuller summary; make the
   rest `"depth":"brief"` with a single-sentence summary.
4. **Prioritize by relevance.** Using `profile.interests`, `industry`, `hometown`,
   tag matching items in `relevance` and prefer them for deep dives / "top_picks".
5. **Flag action items.** If a story touches `profile.watchlist.holdings` or
   `.topics`, add a concrete `action` note (e.g. "affects NVDA you hold").
6. **Background primers.** When an item references a bill/company/person the reader
   may not know, add a 2–3 sentence neutral `primer`.
7. **Framing comparison.** For multi-outlet clusters, fill `framing` with a neutral,
   even-handed note on how outlets differ in emphasis. Never take a side.
8. **Story evolution.** Cross-reference `story_memory` threads. If an item continues
   a thread, set `follow_up` ("Follow-up to Tuesday's piece on X; what changed").
9. **Cross-day memory / no-updates.** For active threads with no news today, add a
   line to `no_updates`. Update `data/story_memory.json`: add new threads, update
   `last_update`/`summary` for continued ones, and prune threads untouched for ~10 days.
10. **Learn from feedback.** Read `data/feedback.json` weights and let them nudge
    ordering/selection (surface more of what got 👍, less of what got 👎). If a
    GitHub CLI is available, fold any open issues labeled `feedback` into
    `data/feedback.json` (parse `id`/`vote`), then close them.

Also set: `date` (YYYY-MM-DD), `generated_at_local` (e.g. "Thursday, July 30, 2026"),
a one-sentence `intro`, and a short `feedback_note` if feedback changed anything.

## Guardrails

- Summarize ONLY from the provided title/excerpt. Do not invent facts, numbers, or quotes.
- Neutral, concise editorial voice. No sensationalism.
- Keep `primer`/`framing` factual and even-handed.

## Publish

```bash
python -m app.pipeline publish        # renders docs/index.html + archive, marks seen
```

Then commit and push everything that changed:

```bash
git add -A
git commit -m "Digest for $(date +%Y-%m-%d)"
git push
```

The reader opens the published GitHub Pages URL each morning. That's the whole job.
