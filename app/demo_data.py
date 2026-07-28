"""Sample articles so you can preview the digest design without a network
connection or an API key (used by `--demo`). These already include summaries
and topics, so they skip the Claude step."""

DEMO_ARTICLES = [
    {
        "id": "demo-1", "source": "The New York Times",
        "title": "Central Banks Signal a Cautious Turn as Inflation Cools",
        "link": "https://www.nytimes.com/", "published": 3,
        "summary": "Major central banks hinted they may slow the pace of rate "
        "changes as recent data show inflation easing. Officials stressed the "
        "shift is data-dependent and not a firm commitment to cuts.",
        "topic": "Business & Economy",
    },
    {
        "id": "demo-2", "source": "CNN",
        "title": "Diplomats Reach Framework for Renewed Ceasefire Talks",
        "link": "https://www.cnn.com/", "published": 5,
        "summary": "Negotiators announced a framework intended to restart stalled "
        "ceasefire discussions. The agreement sets a timeline for further talks "
        "but leaves the hardest disputes unresolved.",
        "topic": "World",
    },
    {
        "id": "demo-3", "source": "Apple Newsroom",
        "title": "Apple Details On-Device AI Features Coming This Fall",
        "link": "https://www.apple.com/newsroom/", "published": 2,
        "summary": "Apple outlined a set of on-device AI capabilities focused on "
        "privacy and speed. The features run locally rather than in the cloud, "
        "which the company frames as a key differentiator.",
        "topic": "Technology",
    },
    {
        "id": "demo-4", "source": "Fox News",
        "title": "Lawmakers Spar Over Details of New Spending Package",
        "link": "https://www.foxnews.com/", "published": 4,
        "summary": "A proposed spending package drew sharp debate over its size "
        "and priorities. Leaders from both parties signaled that amendments are "
        "likely before any vote.",
        "topic": "U.S. / Politics",
    },
    {
        "id": "demo-5", "source": "The New York Times",
        "title": "Researchers Map a Surprising Link Between Sleep and Memory",
        "link": "https://www.nytimes.com/", "published": 1,
        "summary": "A new study describes how specific sleep stages appear to "
        "consolidate memory more than previously thought. The authors caution "
        "the findings are early and need replication.",
        "topic": "Science",
    },
    {
        "id": "demo-6", "source": "CNN",
        "title": "Underdog Advances After Stunning Late Comeback",
        "link": "https://www.cnn.com/", "published": 0,
        "summary": "A heavily favored team was upset following a dramatic "
        "second-half comeback. The result reshuffles the standings heading into "
        "the final stretch of the season.",
        "topic": "Sports",
    },
]
