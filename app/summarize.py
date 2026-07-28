"""Summarize new articles with Claude and assign each a topic.

Sends articles to Claude in batches and uses structured outputs so every
response is a validated list of {id, summary, topic}. The summary is 2-3
sentences; the topic is drawn from a small, consistent taxonomy so the
digest groups cleanly day to day.
"""

import anthropic
from pydantic import BaseModel

# Haiku is the fastest / cheapest model — a good fit for high-volume daily
# summarization. Swap this for a stronger model with no other code changes:
#   claude-sonnet-5    (stronger, still economical)
#   claude-opus-4-8    (most capable)
MODEL = "claude-haiku-4-5"

# A fixed taxonomy keeps grouping stable across days. Claude is told to pick
# the closest fit, falling back to "Other".
TOPICS = [
    "World",
    "U.S. / Politics",
    "Business & Economy",
    "Technology",
    "Science",
    "Health",
    "Sports",
    "Culture & Entertainment",
    "Other",
]

BATCH_SIZE = 10

SYSTEM_PROMPT = (
    "You are the editor of a concise morning news digest. For each article you "
    "are given, write a neutral 2-3 sentence summary capturing what happened and "
    "why it matters, and assign exactly one topic from this list: "
    + ", ".join(TOPICS)
    + ". Match each article to the closest topic; use 'Other' only when nothing "
    "fits. Summarize only from the title and excerpt provided — do not invent "
    "facts, figures, or quotes. Return one entry per article, keyed by its id."
)


class ArticleSummary(BaseModel):
    id: int
    summary: str
    topic: str


class BatchResult(BaseModel):
    items: list[ArticleSummary]


def _summarize_batch(client, batch):
    """Summarize one batch; returns {local_index: {"summary", "topic"}}."""
    lines = []
    for i, art in enumerate(batch):
        excerpt = art["content"][:600] if art["content"] else "(no excerpt available)"
        lines.append(
            f"[id={i}] SOURCE: {art['source']}\nTITLE: {art['title']}\nEXCERPT: {excerpt}"
        )
    user_content = "Summarize and categorize these articles:\n\n" + "\n\n".join(lines)

    response = client.messages.parse(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
        output_format=BatchResult,
    )
    result = response.parsed_output
    out = {}
    if result:
        for item in result.items:
            out[item.id] = {"summary": item.summary.strip(), "topic": item.topic.strip()}
    return out


def summarize(articles):
    """Attach 'summary' and 'topic' to each article in `articles`.

    On any per-batch failure the affected articles fall back to their feed
    excerpt and the 'Other' topic, so the digest still renders.
    """
    if not articles:
        return articles

    client = anthropic.Anthropic()  # resolves ANTHROPIC_API_KEY / ant profile

    for start in range(0, len(articles), BATCH_SIZE):
        batch = articles[start : start + BATCH_SIZE]
        try:
            summaries = _summarize_batch(client, batch)
        except Exception as exc:  # noqa: BLE001 - degrade gracefully
            print(f"  ! summarization failed for a batch ({exc}); using excerpts")
            summaries = {}

        for i, art in enumerate(batch):
            got = summaries.get(i)
            if got:
                art["summary"] = got["summary"]
                art["topic"] = got["topic"] if got["topic"] in TOPICS else "Other"
            else:
                art["summary"] = art["content"][:280] or "(no summary available)"
                art["topic"] = "Other"

    return articles


def group_by_topic(articles):
    """Return an ordered dict-like list of (topic, [articles]) in TOPICS order."""
    grouped = []
    for topic in TOPICS:
        items = [a for a in articles if a.get("topic") == topic]
        if items:
            items.sort(key=lambda a: a.get("published", 0), reverse=True)
            grouped.append((topic, items))
    return grouped


def group_by_category(articles, order):
    """Group by each article's 'topic' (a feed category), following `order`.

    Categories in `order` come first in that order; any extra categories are
    appended alphabetically. Used when AI summarization is off — sections are
    derived from each feed's configured category, so no AI is required.
    """
    present = {a.get("topic", "Other") for a in articles}
    ordered = [c for c in order if c in present]
    ordered += sorted(present - set(order))
    grouped = []
    for cat in ordered:
        items = [a for a in articles if a.get("topic", "Other") == cat]
        items.sort(key=lambda a: a.get("published", 0), reverse=True)
        grouped.append((cat, items))
    return grouped
