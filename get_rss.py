import feedparser

def get_rss_from_url(url):
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            print("No entries found in the RSS feed.")
            return None
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return None

    output = dict()
    output["feed"] = {
            "title": feed.feed.title,
            "link": feed.feed.link,
            "updated": feed.feed.updated,
    }
    output["entries"] = [
        {
            "id": entry.id,
            "title": entry.title,
            "link": entry.link,
            "author": entry.author,
            "published": entry.published,
            "summary": entry.summary,
        }
        for entry in feed.entries
    ]

    return output


if __name__ == "__main__":
    url = "https://rss.arxiv.org/rss/cs.AI"
    result = get_rss_from_url(url)
    if result:
        print("Feed Title:", result["feed"]["title"])
        print("Feed Link:", result["feed"]["link"])
        print("Feed Updated:", result["feed"]["updated"])
        for entry in result["entries"][:5]:  # Print only the first 5 entries
            print("Title:", entry["title"])
            print("Link:", entry["link"])
            print("Author:", entry["author"])
            print("Published:", entry["published"])
            print("Summary:", entry["summary"])