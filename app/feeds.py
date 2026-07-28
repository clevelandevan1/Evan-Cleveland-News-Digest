"""Feed configuration.

Each entry: {"name": <display name>, "url": <RSS/Atom feed URL>}.
Edit freely — add, remove, or re-point sources; the app reads whatever is here.
All feeds below were verified to return entries.

Note: the original four URLs you gave were homepages / marketing pages, not
feeds, so each was mapped to its real RSS endpoint.
"""

FEEDS = [
    # ---- Original sources (mapped to real RSS endpoints) ----
    {
        # https://www.nytimes.com/  ->  NYT HomePage RSS
        "name": "The New York Times",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    },
    {
        # https://www.apple.com/apple-news/ has no feed; Apple's newsroom does.
        "name": "Apple Newsroom",
        "url": "https://www.apple.com/newsroom/rss-feed.rss",
    },
    {
        # https://www.fox.com/news  ->  Fox News latest RSS
        "name": "Fox News",
        "url": "https://moxie.foxnews.com/google-publisher/latest.xml",
    },
    {
        # https://www.cnn.com/  ->  CNN Top Stories RSS
        "name": "CNN",
        "url": "http://rss.cnn.com/rss/cnn_topstories.rss",
    },

    # ---- Technology ----
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},

    # ---- Business & finance ----
    {"name": "BBC Business", "url": "https://feeds.bbci.co.uk/news/business/rss.xml"},
    {
        "name": "MarketWatch",
        "url": "http://feeds.marketwatch.com/marketwatch/topstories/",
    },

    # ---- Economics ----
    {
        "name": "The Economist — Finance & Economics",
        "url": "https://www.economist.com/finance-and-economics/rss.xml",
    },
    {"name": "NPR Economy", "url": "https://feeds.npr.org/1017/rss.xml"},

    # ---- Politics ----
    {"name": "NPR Politics", "url": "https://feeds.npr.org/1014/rss.xml"},
    {"name": "BBC Politics", "url": "https://feeds.bbci.co.uk/news/politics/rss.xml"},
    {"name": "Politico", "url": "https://rss.politico.com/politics-news.xml"},

    # ---- World ----
    {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"name": "The Guardian — World", "url": "https://www.theguardian.com/world/rss"},

    # ---- Science ----
    {"name": "NPR Science", "url": "https://feeds.npr.org/1007/rss.xml"},
    {
        "name": "BBC Science & Environment",
        "url": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    },

    # ---- Health ----
    {"name": "NPR Health", "url": "https://feeds.npr.org/1128/rss.xml"},
    {"name": "BBC Health", "url": "https://feeds.bbci.co.uk/news/health/rss.xml"},

    # ---- Sports ----
    {"name": "ESPN", "url": "https://www.espn.com/espn/rss/news"},
    {"name": "BBC Sport", "url": "https://feeds.bbci.co.uk/sport/rss.xml"},

    # ---- Culture & Entertainment ----
    {"name": "NPR Arts", "url": "https://feeds.npr.org/1008/rss.xml"},
    {"name": "Variety", "url": "https://variety.com/feed/"},
]
