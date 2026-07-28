"""Morning news digest — fetch, dedupe, summarize, group, and render.

Usage:
    python -m app.digest              # real run (needs ANTHROPIC_API_KEY)
    python -m app.digest --demo       # render sample data, no key/network
    python -m app.digest --open       # open the result in your browser
    python -m app.digest --limit 10   # cap entries fetched per feed
    python -m app.digest --no-summarize   # skip Claude; use raw excerpts
"""

import argparse
import os
import sys
import webbrowser
from datetime import datetime

from . import emailer, fetch, render, store, summarize
from .demo_data import DEMO_ARTICLES
from .feeds import FEEDS


def run(demo=False, open_after=False, limit=8, do_summarize=True, do_email=True):
    if demo:
        print("Running in demo mode (sample data, no network or API key).")
        articles = list(DEMO_ARTICLES)
        grouped = summarize.group_by_topic(articles)
        out = render.render(grouped, len(articles), 4)
        _finish(out, open_after)
        return out

    print("Fetching feeds...")
    fetched = fetch.fetch_all(FEEDS, limit=limit)
    print(f"Fetched {len(fetched)} total entries.")

    new_articles = store.filter_new(fetched)
    print(f"{len(new_articles)} are new since your last digest.")

    if new_articles:
        if do_summarize:
            if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
                print(
                    "\nERROR: no ANTHROPIC_API_KEY set, so summaries can't be "
                    "generated.\nSet the key, or run with --no-summarize to use "
                    "raw feed excerpts, or --demo to preview the design.\n",
                    file=sys.stderr,
                )
                sys.exit(1)
            print(f"Summarizing with {summarize.MODEL}...")
            summarize.summarize(new_articles)
        else:
            for art in new_articles:
                art["summary"] = art.get("content", "")[:280] or "(no excerpt)"
                art["topic"] = "Other"

    source_count = len({a["source"] for a in new_articles}) or len(FEEDS)
    grouped = summarize.group_by_topic(new_articles)
    out = render.render(grouped, len(new_articles), source_count)

    # Only mark as seen after a successful render, so a crash doesn't cause
    # stories to be silently skipped tomorrow.
    store.mark_seen(new_articles)

    total, _ = store.stats()
    print(f"Digest written. {total} stories now in your read history.")

    if do_email:
        _maybe_email(out)

    _finish(out, open_after)
    return out


def _maybe_email(out_path):
    """Email the rendered digest if SMTP settings are configured."""
    cfg = emailer.email_config()
    if not cfg:
        print(
            "  (email not sent: set SMTP_USER, SMTP_PASS and DIGEST_TO in .env "
            "to enable delivery)"
        )
        return
    try:
        html = out_path.read_text(encoding="utf-8")
        subject = f"Morning Digest — {datetime.now().strftime('%A, %B %-d')}"
        emailer.send_digest(subject, html, cfg)
        print(f"Emailed digest to {cfg['to']}.")
    except Exception as exc:  # noqa: BLE001 - never let a send failure crash the run
        print(f"  ! email send failed ({exc}); the page was still written")


def _finish(out_path, open_after):
    print(f"\n  ->  {out_path}\n")
    if open_after:
        webbrowser.open(out_path.resolve().as_uri())


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate your morning news digest.")
    parser.add_argument("--demo", action="store_true", help="render sample data only")
    parser.add_argument("--open", action="store_true", help="open result in browser")
    parser.add_argument("--limit", type=int, default=8, help="entries per feed")
    parser.add_argument(
        "--no-summarize", action="store_true", help="skip Claude, use excerpts"
    )
    parser.add_argument(
        "--no-email", action="store_true", help="don't email the digest even if configured"
    )
    args = parser.parse_args(argv)
    run(
        demo=args.demo,
        open_after=args.open,
        limit=args.limit,
        do_summarize=not args.no_summarize,
        do_email=not args.no_email,
    )


if __name__ == "__main__":
    main()
