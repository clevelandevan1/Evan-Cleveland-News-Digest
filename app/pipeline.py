"""Cloud digest pipeline (GitHub-delivered).

Two Python entry points bracket the cloud agent's AI work:

    python -m app.pipeline emit      # fetch feeds, dedupe, write data/pending.json
    <the cloud agent reads pending.json + config + memory, writes data/analysis.json>
    python -m app.pipeline publish   # render docs/index.html, mark seen, update memory

State lives in JSON files under data/ so it versions cleanly in git and gives
the cloud agent memory across days:

    data/seen.json          ids already shown (dedupe)
    data/pending.json       new articles awaiting analysis (transient)
    data/analysis.json      the agent's structured digest (transient)
    data/story_memory.json  ongoing story threads (cross-day memory)
    data/feedback.json      thumbs up/down signals
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import fetch, newsletter
from .feeds import FEEDS

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"

SEEN = DATA / "seen.json"
PENDING = DATA / "pending.json"
ANALYSIS = DATA / "analysis.json"


def _load(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def emit(limit=12):
    """Fetch all feeds, drop already-seen items, write new ones to pending.json."""
    print("Fetching feeds...")
    fetched = fetch.fetch_all(FEEDS, limit=limit)
    seen = _load(SEEN, {})
    new = [a for a in fetched if a["id"] not in seen]
    # Attach each source's configured category so the agent has a starting topic.
    from .feeds import category_for
    for a in new:
        a["category"] = category_for(a["source"])
    _save(PENDING, new)
    print(f"Fetched {len(fetched)}; {len(new)} new -> {PENDING.relative_to(ROOT)}")
    return len(new)


def publish():
    """Render the agent's analysis.json into the GitHub Pages site and mark seen."""
    analysis = _load(ANALYSIS, None)
    if analysis is None:
        print(f"ERROR: {ANALYSIS} not found. Run the analysis step first.", file=sys.stderr)
        sys.exit(1)

    html = newsletter.render_from_analysis(analysis)

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    date_key = analysis.get("date") or datetime.now().strftime("%Y-%m-%d")
    archive = DOCS / "archive"
    archive.mkdir(exist_ok=True)
    (archive / f"digest-{date_key}.html").write_text(html, encoding="utf-8")

    # Mark everything that was pending as seen so tomorrow won't repeat it.
    pending = _load(PENDING, [])
    seen = _load(SEEN, {})
    now = datetime.now(timezone.utc).isoformat()
    for a in pending:
        seen[a["id"]] = {"source": a["source"], "title": a["title"], "seen": now}
    _save(SEEN, seen)
    _save(PENDING, [])  # clear the transient queue

    print(f"Published docs/index.html ({date_key}); {len(pending)} marked seen; "
          f"{len(seen)} total in history.")


def list_feeds():
    """Print the configured feeds as JSON (no network).

    Used by the cloud agent, whose sandbox blocks direct outbound network, so
    it retrieves each feed via its WebFetch tool instead of feedparser.
    """
    from .feeds import category_for
    out = [
        {"name": f["name"], "url": f["url"], "category": category_for(f["name"])}
        for f in FEEDS
    ]
    print(json.dumps(out, indent=2, ensure_ascii=False))


def seen_ids():
    """Print the set of already-seen article ids as JSON, for dedupe."""
    print(json.dumps(sorted(_load(SEEN, {}).keys()), ensure_ascii=False))


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else ""
    if cmd == "emit":  # local/testing only — uses feedparser (needs direct network)
        limit = int(argv[1]) if len(argv) > 1 else 12
        emit(limit=limit)
    elif cmd == "feeds":
        list_feeds()
    elif cmd == "seen":
        seen_ids()
    elif cmd == "publish":
        publish()
    else:
        print("usage: python -m app.pipeline [feeds | seen | emit [limit] | publish]",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
