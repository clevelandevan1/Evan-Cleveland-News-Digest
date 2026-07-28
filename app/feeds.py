"""Feed configuration.

Each entry: {"name": <display name>, "url": <feed URL>, "category": <topic>}.
Edit freely — add, remove, or re-point sources; the app reads whatever is here.
All feeds below were verified to return entries.

The "category" is used to group articles into topic sections in the digest
(no AI required). Use one of the labels in CATEGORY_ORDER below, or add your
own — any new category is appended after the known ones.

Note: the original four URLs you gave were homepages / marketing pages, not
feeds, so each was mapped to its real RSS endpoint.
"""

# The order topic sections appear in the digest.
CATEGORY_ORDER = [
    "Top Stories",
    "World",
    "Politics",
    "Business & Economy",
    "Technology",
    "Science",
    "Health",
    "Sports",
    "Culture & Entertainment",
]

FEEDS = [
    # ---- Top Stories (general front pages) ----
    {
        # https://www.nytimes.com/  ->  NYT HomePage RSS
        "name": "The New York Times",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "category": "Top Stories",
    },
    {
        # https://www.cnn.com/  ->  CNN Top Stories RSS
        "name": "CNN",
        "url": "http://rss.cnn.com/rss/cnn_topstories.rss",
        "category": "Top Stories",
    },
    {
        # https://www.fox.com/news  ->  Fox News latest RSS
        "name": "Fox News",
        "url": "https://moxie.foxnews.com/google-publisher/latest.xml",
        "category": "Top Stories",
    },

    # ---- World ----
    {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
     "category": "World"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml",
     "category": "World"},
    {"name": "The Guardian — World", "url": "https://www.theguardian.com/world/rss",
     "category": "World"},

    # ---- Politics ----
    {"name": "NPR Politics", "url": "https://feeds.npr.org/1014/rss.xml",
     "category": "Politics"},
    {"name": "BBC Politics", "url": "https://feeds.bbci.co.uk/news/politics/rss.xml",
     "category": "Politics"},
    {"name": "Politico", "url": "https://rss.politico.com/politics-news.xml",
     "category": "Politics"},

    # ---- Business & Economy ----
    {"name": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
     "category": "Business & Economy"},
    {"name": "MarketWatch", "url": "http://feeds.marketwatch.com/marketwatch/topstories/",
     "category": "Business & Economy"},
    {"name": "The Economist — Finance & Economics",
     "url": "https://www.economist.com/finance-and-economics/rss.xml",
     "category": "Business & Economy"},
    {"name": "NPR Economy", "url": "https://feeds.npr.org/1017/rss.xml",
     "category": "Business & Economy"},

    # ---- Technology ----
    {
        # https://www.apple.com/apple-news/ has no feed; Apple's newsroom does.
        "name": "Apple Newsroom",
        "url": "https://www.apple.com/newsroom/rss-feed.rss",
        "category": "Technology",
    },
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml",
     "category": "Technology"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index",
     "category": "Technology"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/",
     "category": "Technology"},

    # ---- Science ----
    {"name": "NPR Science", "url": "https://feeds.npr.org/1007/rss.xml",
     "category": "Science"},
    {"name": "BBC Science & Environment",
     "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
     "category": "Science"},

    # ---- Health ----
    {"name": "NPR Health", "url": "https://feeds.npr.org/1128/rss.xml",
     "category": "Health"},
    {"name": "BBC Health", "url": "https://feeds.bbci.co.uk/news/health/rss.xml",
     "category": "Health"},

    # ---- Sports ----
    {"name": "ESPN", "url": "https://www.espn.com/espn/rss/news",
     "category": "Sports"},
    {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml",
     "category": "Sports"},

    # ---- Culture & Entertainment ----
    {"name": "NPR Arts", "url": "https://feeds.npr.org/1008/rss.xml",
     "category": "Culture & Entertainment"},
    {"name": "Variety", "url": "https://variety.com/feed/",
     "category": "Culture & Entertainment"},
]


def category_for(source_name):
    """Return the configured category for a source, or 'Other' if unknown."""
    for feed in FEEDS:
        if feed["name"] == source_name:
            return feed.get("category", "Other")
    return "Other"
