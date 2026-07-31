"""Render the cloud agent's analysis JSON into the newsletter HTML.

Expected analysis shape (all fields optional except headline):

{
  "date": "2026-07-30",
  "generated_at_local": "Wednesday, July 30, 2026",
  "intro": "One-sentence editor's note.",
  "feedback_note": "Surfaced more enterprise-tech per your 👍 history.",
  "top_picks": [ <item>, ... ],          # 2-3 deep dives — "What matters most"
  "sections": [ {"topic": "Technology", "items": [ <item>, ... ]}, ... ],
  "no_updates": ["No major update on Monday's story about X."]
}

<item> = {
  "id": "stable-id",                 # used for feedback links
  "headline": "...",
  "summary": "2-4 sentences (deep) or one line (brief)",
  "depth": "deep" | "brief",
  "stakes": 1-5,                     # 5 = highly consequential
  "topic": "World",
  "sources": [{"name": "NYT", "url": "https://..."}, ...],
  "new_info": "What's genuinely new vs prior coverage.",
  "framing": "How outlets differ in framing (neutral).",
  "primer": "Background on a referenced bill/company/person.",
  "follow_up": "Follow-up to Monday's piece on X; what changed.",
  "relevance": ["enterprise IT", "WWT"],
  "action": "You may want to ... (affects NVDA you hold)."
}
"""

import html
from datetime import datetime
from urllib.parse import quote

# Prefilled GitHub-issue feedback links (no backend needed).
REPO = "https://github.com/clevelandevan1/Evan-Cleveland-News-Digest"


def _esc(text):
    return html.escape(str(text), quote=True) if text is not None else ""


def _feedback_links(item):
    hid = item.get("id") or item.get("headline", "")
    head = item.get("headline", "")
    def link(vote, glyph, label):
        title = quote(f"feedback:{vote}: {head}")
        body = quote(f"id: {hid}\nvote: {vote}\n\n(add any notes here)")
        url = _esc(f"{REPO}/issues/new?labels=feedback&title={title}&body={body}")
        return f'<a class="fb" href="{url}" title="{label}" target="_blank" rel="noopener">{glyph}</a>'
    return (
        '<span class="feedback">'
        + link("up", "&#128077;", "More like this")
        + link("down", "&#128078;", "Less like this")
        + "</span>"
    )


def _sources(item):
    srcs = item.get("sources") or []
    chips = []
    for s in srcs:
        name = _esc(s.get("name", ""))
        url = _esc(s.get("url", ""))
        chips.append(f'<a class="src" href="{url}" target="_blank" rel="noopener">{name}</a>'
                     if url else f'<span class="src">{name}</span>')
    tag = ""
    if len(srcs) > 1:
        tag = f'<span class="cluster-tag">{len(srcs)} outlets</span>'
    return f'<div class="sources">{tag}{"".join(chips)}</div>' if chips else ""


def _tags(item):
    rel = item.get("relevance") or []
    return "".join(f'<span class="tag">{_esc(t)}</span>' for t in rel)


def _stakes(item):
    s = item.get("stakes")
    if not s:
        return ""
    dots = "".join(
        f'<span class="dot {"on" if i < s else ""}"></span>' for i in range(5)
    )
    return f'<span class="stakes" title="Stakes {s}/5">{dots}</span>'


def _extra(label, cls, value):
    if not value:
        return ""
    return f'<div class="note {cls}"><span class="note-label">{label}</span> {_esc(value)}</div>'


def _primer(item):
    if not item.get("primer"):
        return ""
    return (
        '<details class="primer"><summary>Context</summary>'
        f"<p>{_esc(item['primer'])}</p></details>"
    )


def _render_item(item, deep=False):
    cls = "item deep" if deep else "item brief"
    parts = [f'<article class="{cls}">']
    parts.append('<div class="item-head">')
    parts.append(_stakes(item))
    parts.append(f'<h3>{_esc(item.get("headline",""))}</h3>')
    parts.append("</div>")
    if item.get("follow_up"):
        parts.append(f'<div class="followup">&#8618; {_esc(item["follow_up"])}</div>')
    if item.get("summary"):
        parts.append(f'<p class="summary">{_esc(item["summary"])}</p>')
    if deep:
        parts.append(_extra("What&rsquo;s new", "new", item.get("new_info")))
        parts.append(_extra("How outlets frame it", "framing", item.get("framing")))
    parts.append(_primer(item))
    if item.get("action"):
        parts.append(f'<div class="action">&#9873; {_esc(item["action"])}</div>')
    parts.append('<div class="meta">')
    parts.append(_sources(item))
    tags = _tags(item)
    if tags:
        parts.append(f'<div class="tags">{tags}</div>')
    parts.append(_feedback_links(item))
    parts.append("</div>")
    parts.append("</article>")
    return "".join(parts)


def render_from_analysis(a):
    date_long = a.get("generated_at_local") or datetime.now().strftime("%A, %B %-d, %Y")
    intro = a.get("intro", "")

    body = []

    top = a.get("top_picks") or []
    if top:
        body.append('<section class="topic featured">')
        body.append('<h2 class="topic-title">What matters most</h2>')
        body.extend(_render_item(it, deep=True) for it in top)
        body.append("</section>")

    for section in a.get("sections") or []:
        items = section.get("items") or []
        if not items:
            continue
        body.append('<section class="topic">')
        body.append(f'<h2 class="topic-title">{_esc(section.get("topic","More"))}</h2>')
        body.extend(_render_item(it, deep=(it.get("depth") == "deep")) for it in items)
        body.append("</section>")

    no_updates = a.get("no_updates") or []
    if no_updates:
        body.append('<section class="topic developing">')
        body.append('<h2 class="topic-title">Still developing</h2>')
        body.append("<ul class='nolist'>")
        body.extend(f"<li>{_esc(n)}</li>" for n in no_updates)
        body.append("</ul></section>")

    if not (top or any(s.get("items") for s in a.get("sections") or [])):
        body.append('<p class="empty">No new stories since your last digest. Enjoy the quiet.</p>')

    feedback_note = a.get("feedback_note", "")
    footer_bits = [f"Generated for your morning read &middot; Analysis by Claude"]
    if feedback_note:
        footer_bits.append(_esc(feedback_note))
    footer = " &middot; ".join(footer_bits)

    return _PAGE.format(
        date=_esc(a.get("date", "")),
        date_long=_esc(date_long),
        intro=_esc(intro),
        body="\n".join(body),
        footer=footer,
    )


_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Morning Digest — {date}</title>
<style>
  :root {{
    --bg:#faf9f6; --card:#fff; --ink:#1a1a1a; --muted:#6b6b6b; --faint:#9b978e;
    --rule:#e7e4dd; --accent:#8a5a2b; --hot:#b23c2e; --chip:#f0ede6; --chipink:#5a5750;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg:#16161a; --card:#1e1e24; --ink:#eceae4; --muted:#a5a29a; --faint:#77746c;
      --rule:#2c2c34; --accent:#d0a06a; --hot:#e07a5f; --chip:#26262e; --chipink:#b8b4ac;
    }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font-family:Georgia,"Times New Roman",serif; line-height:1.55; -webkit-font-smoothing:antialiased; }}
  .wrap {{ max-width:700px; margin:0 auto; padding:56px 24px 80px; }}
  header.masthead {{ text-align:center; border-bottom:2px solid var(--ink); padding-bottom:20px; }}
  .masthead h1 {{ font-size:42px; letter-spacing:.5px; margin:0 0 6px; }}
  .masthead .date {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    text-transform:uppercase; letter-spacing:2.5px; font-size:11px; color:var(--muted); }}
  .intro {{ text-align:center; color:var(--muted); font-style:italic; font-size:15.5px; margin:20px 0 42px; }}
  section.topic {{ margin:0 0 44px; }}
  .topic-title {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:13px;
    text-transform:uppercase; letter-spacing:2px; color:var(--accent); border-bottom:1px solid var(--rule);
    padding-bottom:8px; margin:0 0 22px; }}
  section.featured .topic-title {{ color:var(--hot); }}
  article.item {{ margin:0 0 26px; padding-bottom:22px; border-bottom:1px solid var(--rule); }}
  article.item:last-child {{ border-bottom:none; }}
  .item-head {{ display:flex; align-items:baseline; gap:10px; }}
  article.item h3 {{ font-size:19px; line-height:1.3; margin:0 0 4px; font-weight:700; }}
  article.deep h3 {{ font-size:23px; }}
  .summary {{ margin:6px 0 8px; font-size:16px; }}
  article.brief .summary {{ color:var(--muted); font-size:15px; }}
  .stakes {{ display:inline-flex; gap:3px; flex:0 0 auto; transform:translateY(-2px); }}
  .stakes .dot {{ width:7px; height:7px; border-radius:50%; background:var(--rule); }}
  .stakes .dot.on {{ background:var(--hot); }}
  .followup {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:12.5px;
    color:var(--accent); margin:2px 0 6px; }}
  .note {{ font-size:14.5px; margin:8px 0; padding:8px 12px; border-left:3px solid var(--rule); background:var(--card); }}
  .note-label {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:11px;
    text-transform:uppercase; letter-spacing:1px; color:var(--faint); margin-right:6px; }}
  .note.framing {{ border-left-color:var(--accent); }}
  .note.new {{ border-left-color:var(--hot); }}
  details.primer {{ margin:8px 0; font-size:14.5px; }}
  details.primer summary {{ cursor:pointer; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    font-size:11.5px; text-transform:uppercase; letter-spacing:1px; color:var(--accent); }}
  details.primer p {{ margin:8px 0 0; color:var(--muted); }}
  .action {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:13.5px;
    background:var(--chip); color:var(--ink); padding:8px 12px; border-radius:6px; margin:10px 0; }}
  .meta {{ display:flex; align-items:center; flex-wrap:wrap; gap:8px 14px; margin-top:10px; }}
  .sources {{ display:flex; align-items:center; flex-wrap:wrap; gap:6px; }}
  .src {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:11px;
    letter-spacing:.5px; text-transform:uppercase; color:var(--faint); text-decoration:none; }}
  a.src:hover {{ color:var(--accent); }}
  .cluster-tag {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:10.5px;
    background:var(--chip); color:var(--chipink); padding:2px 7px; border-radius:10px; letter-spacing:.5px; }}
  .tags {{ display:flex; gap:6px; flex-wrap:wrap; }}
  .tag {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; font-size:11px;
    color:var(--accent); border:1px solid var(--rule); padding:1px 8px; border-radius:10px; }}
  .feedback {{ margin-left:auto; display:flex; gap:8px; }}
  .fb {{ text-decoration:none; font-size:14px; opacity:.5; }}
  .fb:hover {{ opacity:1; }}
  .nolist {{ margin:0; padding-left:18px; color:var(--muted); font-size:15px; }}
  .nolist li {{ margin:6px 0; }}
  .empty {{ text-align:center; color:var(--muted); font-style:italic; padding:40px 0; }}
  footer {{ border-top:1px solid var(--rule); margin-top:40px; padding-top:20px; text-align:center;
    color:var(--faint); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
    font-size:12px; line-height:1.7; }}
</style>
</head>
<body>
  <div class="wrap">
    <header class="masthead">
      <h1>Morning Digest</h1>
      <div class="date">{date_long}</div>
    </header>
    <p class="intro">{intro}</p>
    {body}
    <footer>{footer}</footer>
  </div>
</body>
</html>
"""
