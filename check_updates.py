import json
import os
from datetime import datetime
from typing import Dict, Optional
from config import area_interest_list
from get_rss import get_rss_from_url
from logger import setup_logger

logger = setup_logger(__name__)

CACHE_FILE = "rss_cache.json"

def load_cache() -> Dict:
    """加载缓存的RSS数据"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取缓存文件失败: {str(e)}")
    return {}

def save_cache(cache: Dict) -> None:
    """保存RSS数据到缓存"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存缓存文件失败: {str(e)}")

def check_feed_update(feed_url: str, cache: Dict) -> tuple[bool, Optional[dict]]:
    """检查RSS feed是否有更新"""
    current_feed = get_rss_from_url(feed_url)
    if not current_feed:
        return False, None

    if feed_url not in cache:
        return True, current_feed

    try:
        cached_published = cache[feed_url]["feed"]["published"]
        current_published = current_feed["feed"]["published"]
        
        # 如果发布时间不同，说明有更新
        if cached_published != current_published:
            return True, current_feed
            
    except KeyError as e:
        logger.error(f"缓存数据格式错误: {str(e)}")
        return True, current_feed

    return False, current_feed

def main() -> bool:
    """
    主函数，检查所有RSS源是否有更新
    返回: 如果有任何更新返回True，否则返回False
    """
    cache = load_cache()
    new_cache = {}
    has_updates = False

    for item in area_interest_list:
        feed_url = item["rss_url"]
        is_updated, current_feed = check_feed_update(feed_url, cache)
        
        if is_updated:
            has_updates = True
            logger.info(f"发现更新: {feed_url}")
        
        if current_feed:
            new_cache[feed_url] = current_feed

    if has_updates:
        save_cache(new_cache)
        
    return has_updates

if __name__ == "__main__":
    has_updates = main()
    # 为了与GitHub Actions集成，输出特定格式的结果
    print(f"::set-output name=has_updates::{str(has_updates).lower()}") 