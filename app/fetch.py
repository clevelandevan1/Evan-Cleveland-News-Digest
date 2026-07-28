"""Fetch and normalize entries from each configured feed."""

import hashlib
import html
import re
import time

import feedparser

# Some feeds (Fox, others) reject the default urllib UA. Present a normal one.
feedparser.USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "MorningDigest/1.0 (+personal news digest)"
)

_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text):
    """Strip HTML tags and collapse whitespace from a feed summary."""
    if not text:
        return ""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _article_id(entry, feed_name):
    """A stable id for dedup: prefer the feed's guid/id, fall back to link,
    then to a hash of source+title."""
    for key in ("id", "guid", "link"):
        val = entry.get(key)
        if val:
            return val
    basis = f"{feed_name}:{entry.get('title', '')}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()


def _published(entry):
    """Return an epoch seconds sort key (0 if the feed omits a date)."""
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            try:
                return time.mktime(parsed)
            except (TypeError, ValueError, OverflowError):
                pass
    return 0.0


def fetch_feed(feed, limit=15):
    """Fetch one feed and return a list of normalized article dicts.

    Never raises for a single bad feed — returns [] and prints a warning so a
    flaky source doesn't sink the whole digest.
    """
    name = feed["name"]
    try:
        parsed = feedparser.parse(feed["url"])
    except Exception as exc:  # noqa: BLE001 - want the digest to survive
        print(f"  ! {name}: fetch failed ({exc})")
        return []

    if parsed.bozo and not parsed.entries:
        reason = getattr(parsed, "bozo_exception", "unknown error")
        print(f"  ! {name}: could not parse feed ({reason})")
        return []

    articles = []
    for entry in parsed.entries[:limit]:
        articles.append(
            {
                "id": _article_id(entry, name),
                "source": name,
                "title": _clean(entry.get("title", "")) or "(untitled)",
                "link": entry.get("link", ""),
                "content": _clean(
                    entry.get("summary", "") or entry.get("description", "")
                ),
                "published": _published(entry),
            }
        )
    return articles


def fetch_all(feeds, limit=15):
    """Fetch every feed, newest first within each source."""
    articles = []
    for feed in feeds:
        got = fetch_feed(feed, limit=limit)
        print(f"  - {feed['name']}: {len(got)} entries")
        articles.extend(got)
    return articles
