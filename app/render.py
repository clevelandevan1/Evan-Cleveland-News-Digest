"""Render the digest as a clean, minimal newsletter-style HTML page."""

import html
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Morning Digest — {date}</title>
<style>
  :root {{
    --bg: #faf9f6;
    --card: #ffffff;
    --ink: #1a1a1a;
    --muted: #6b6b6b;
    --faint: #999;
    --rule: #e7e4dd;
    --accent: #8a5a2b;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #16161a;
      --card: #1e1e24;
      --ink: #eceae4;
      --muted: #a5a29a;
      --faint: #77746c;
      --rule: #2c2c34;
      --accent: #d0a06a;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: Georgia, "Times New Roman", serif;
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 680px; margin: 0 auto; padding: 56px 24px 80px; }}
  header.masthead {{
    text-align: center;
    border-bottom: 2px solid var(--ink);
    padding-bottom: 20px;
    margin-bottom: 8px;
  }}
  .masthead h1 {{
    font-size: 40px;
    letter-spacing: 0.5px;
    margin: 0 0 6px;
    font-weight: 700;
  }}
  .masthead .date {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    text-transform: uppercase;
    letter-spacing: 2.5px;
    font-size: 11px;
    color: var(--muted);
  }}
  .lead {{
    text-align: center;
    color: var(--muted);
    font-style: italic;
    font-size: 15px;
    margin: 18px 0 40px;
  }}
  section.topic {{ margin: 0 0 44px; }}
  h2.topic-title {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent);
    border-bottom: 1px solid var(--rule);
    padding-bottom: 8px;
    margin: 0 0 22px;
  }}
  article.item {{ margin: 0 0 26px; }}
  article.item h3 {{
    font-size: 20px;
    line-height: 1.3;
    margin: 0 0 6px;
    font-weight: 700;
  }}
  article.item h3 a {{ color: var(--ink); text-decoration: none; }}
  article.item h3 a:hover {{ color: var(--accent); }}
  article.item p {{ margin: 0 0 8px; font-size: 16px; }}
  .byline {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--faint);
  }}
  footer {{
    border-top: 1px solid var(--rule);
    margin-top: 40px;
    padding-top: 20px;
    text-align: center;
    color: var(--faint);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 12px;
    line-height: 1.7;
  }}
  .empty {{
    text-align: center;
    color: var(--muted);
    font-style: italic;
    padding: 40px 0;
  }}
</style>
</head>
<body>
  <div class="wrap">
    <header class="masthead">
      <h1>Morning Digest</h1>
      <div class="date">{date_long}</div>
    </header>
    <p class="lead">{lead}</p>
    {body}
    <footer>
      {footer}
    </footer>
  </div>
</body>
</html>
"""


def _esc(text):
    return html.escape(text or "", quote=True)


def _render_item(art):
    title = _esc(art["title"])
    summary = _esc(art.get("summary", ""))
    source = _esc(art.get("source", ""))
    link = _esc(art.get("link", ""))
    heading = f'<a href="{link}">{title}</a>' if link else title
    return (
        '<article class="item">'
        f"<h3>{heading}</h3>"
        f"<p>{summary}</p>"
        f'<span class="byline">{source}</span>'
        "</article>"
    )


def render(grouped, new_count, source_count, ai_summaries=True, out_path=None):
    """Render `grouped` (list of (topic, [articles])) to an HTML file.

    Returns the Path written.
    """
    now = datetime.now()
    date_key = now.strftime("%Y-%m-%d")
    date_long = now.strftime("%A, %B %-d, %Y")

    if grouped:
        lead = (
            f"{new_count} new "
            f"{'story' if new_count == 1 else 'stories'} across {source_count} "
            f"{'source' if source_count == 1 else 'sources'}, "
            + ("summarized and grouped by topic for you."
               if ai_summaries else "grouped by topic for you.")
        )
        sections = []
        for topic, items in grouped:
            body_items = "\n".join(_render_item(a) for a in items)
            sections.append(
                f'<section class="topic"><h2 class="topic-title">{_esc(topic)}</h2>'
                f"{body_items}</section>"
            )
        body = "\n".join(sections)
    else:
        lead = "You're all caught up."
        body = (
            '<p class="empty">No new stories since your last digest. '
            "Enjoy the quiet.</p>"
        )

    footer = (
        f"Generated {now.strftime('%-I:%M %p')} &middot; "
        + ("Summaries by Claude &middot; " if ai_summaries else "")
        + "Already-read stories are hidden automatically."
    )

    page = _PAGE.format(
        date=date_key,
        date_long=date_long,
        lead=_esc(lead),
        body=body,
        footer=footer,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = Path(out_path) if out_path else OUTPUT_DIR / f"digest-{date_key}.html"
    out_path.write_text(page, encoding="utf-8")
    return out_path
