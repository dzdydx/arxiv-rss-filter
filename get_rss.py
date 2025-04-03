import feedparser
from typing import Optional
from logger import setup_logger

logger = setup_logger(__name__)

def get_rss_from_url(url: str) -> Optional[dict]:
    try:
        logger.info(f"开始获取RSS feed: {url}")
        feed = feedparser.parse(url)
        
        if not feed.entries:
            logger.warning(f"RSS feed {url} 中没有找到entries")
            return None
            
        if not hasattr(feed.feed, 'updated'):
            logger.warning(f"RSS feed {url} 中没有updated字段")
            return None
            
        return {
            "feed": {
                "title": feed.feed.title,
                "link": feed.feed.link,
                "updated": feed.feed.updated,
            },
            "entries": [
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
        }
    except Exception as e:
        logger.error(f"获取RSS feed时发生错误: {url}, 错误信息: {str(e)}")
        return None

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