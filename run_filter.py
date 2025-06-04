from config import area_interest_list, SYSTEM_PROMPT
from batch_inference import BatchInference
from utils import replace_placeholder_in_prompt, extract_paper_summary, save_results
from logger import setup_logger
import json
from typing import List, Dict
import asyncio
import os

# 配置日志
logger = setup_logger(__name__)

CACHE_FILE = "rss_cache.json"

def load_cache() -> Dict:
    """加载缓存的RSS数据"""
    if not os.path.exists(CACHE_FILE):
        logger.error(f"缓存文件 {CACHE_FILE} 不存在")
        return {}
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取缓存文件失败: {str(e)}")
        return {}

async def filter_rss_content(rss_content: dict, user_interest: str) -> List[dict]:
    sys_prompt = replace_placeholder_in_prompt(SYSTEM_PROMPT, "user_interest", user_interest)
    
    paper_infos = rss_content["entries"]
    for paper_info in paper_infos:
        paper_info["content"] = extract_paper_summary(paper_info)

    batch_inference = BatchInference()
    results = await batch_inference.create_tasks(sys_prompt, paper_infos)
    # 只保留isRelated为True，且success为True的paper_info
    results = [res for res in results 
               if res is not None 
               and (res["isRelated"] is True or res["isRelated"] == "true")
               and res["success"] is True]
    
    return results

async def main():
    cache = load_cache()
    if not cache:
        logger.error("无法获取缓存的RSS内容")
        return

    output = []
    for item in area_interest_list:
        rss_url = item["rss_url"]
        user_interest = item["area_interest"]
        
        if rss_url not in cache:
            logger.warning(f"在缓存中未找到RSS内容: {rss_url}")
            continue
            
        filter_results = await filter_rss_content(cache[rss_url], user_interest)
        output.append({
            "rss_url": rss_url,
            "user_interest": user_interest,
            "filter_results": filter_results
        })
    
    save_results(output)

if __name__ == "__main__":
    asyncio.run(main()) 