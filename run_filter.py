from config import area_interest_list, SYSTEM_PROMPT
from batch_inference import BatchInference
from utils import replace_placeholder_in_prompt, extract_paper_summary, save_results
from logger import setup_logger
import json
from typing import List, Dict
import asyncio
import os
from datetime import datetime
import hashlib

# 配置日志
logger = setup_logger(__name__)

CACHE_FILE = "rss_cache.json"
RESULTS_CACHE_DIR = "arxiv_updates"

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

def get_results_cache_file() -> str:
    """获取当天的结果缓存文件路径"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(RESULTS_CACHE_DIR, f"batch_results_{current_date}.json")

def load_results_cache() -> Dict:
    """加载当天的batch inference结果缓存"""
    cache_file = get_results_cache_file()
    if not os.path.exists(cache_file):
        return {}
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取结果缓存文件失败: {str(e)}")
        return {}

def save_results_cache(results_cache: Dict) -> None:
    """保存batch inference结果到缓存文件"""
    # 创建目录
    os.makedirs(RESULTS_CACHE_DIR, exist_ok=True)
    
    cache_file = get_results_cache_file()
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(results_cache, f, ensure_ascii=False, indent=2)
        logger.info(f"结果缓存已保存到: {cache_file}")
    except Exception as e:
        logger.error(f"保存结果缓存失败: {str(e)}")

def generate_cache_key(rss_url: str, user_interest: str) -> str:
    """生成缓存键值，使用哈希避免过长的user_interest"""
    # 将 rss_url 和 user_interest 组合后生成哈希值
    combined_content = f"{rss_url}|||{user_interest}"
    hash_object = hashlib.md5(combined_content.encode('utf-8'))
    return hash_object.hexdigest()

async def filter_rss_content(rss_content: dict, user_interest: str, rss_url: str, results_cache: Dict) -> List[dict]:
    """过滤RSS内容，支持缓存机制"""
    cache_key = generate_cache_key(rss_url, user_interest)
    
    # 检查是否有缓存的结果
    if cache_key in results_cache:
        logger.info(f"使用缓存的batch inference结果: {rss_url}")
        return results_cache[cache_key]
    
    logger.info(f"执行新的batch inference: {rss_url}")
    sys_prompt = replace_placeholder_in_prompt(SYSTEM_PROMPT, "user_interest", user_interest)
    
    paper_infos = rss_content["entries"]
    for paper_info in paper_infos:
        paper_info["content"] = extract_paper_summary(paper_info)

    batch_inference = BatchInference()
    results = await batch_inference.create_tasks(sys_prompt, paper_infos)

    # 只保留isRelated为True，且success为True的paper_info
    filtered_results = [res for res in results 
               if res is not None 
               and (res["isRelated"] is True or res["isRelated"] == "true")
               and res["success"] is True]
    
    # 将结果保存到缓存
    results_cache[cache_key] = filtered_results
    
    return filtered_results

async def main():
    cache = load_cache()
    if not cache:
        logger.error("无法获取缓存的RSS内容")
        return

    # 加载当天的结果缓存
    results_cache = load_results_cache()
    
    output = []
    for item in area_interest_list:
        rss_url = item["rss_url"]
        user_interest = item["area_interest"]
        
        if rss_url not in cache:
            logger.warning(f"在缓存中未找到RSS内容: {rss_url}")
            continue
            
        filter_results = await filter_rss_content(cache[rss_url], user_interest, rss_url, results_cache)
        output.append({
            "rss_url": rss_url,
            "user_interest": user_interest,
            "filter_results": filter_results
        })
    
    # 保存更新的结果缓存
    save_results_cache(results_cache)
    
    # 保存最终输出
    save_results(output)

if __name__ == "__main__":
    asyncio.run(main()) 