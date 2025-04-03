from get_rss import get_rss_from_url
from config import area_interest_list, SYSTEM_PROMPT
from batch_inference import BatchInference
from utils import replace_placeholder_in_prompt, extract_paper_summary, save_results
from logger import setup_logger
import json
from datetime import datetime
from typing import List
import os
import asyncio

# 配置日志
logger = setup_logger(__name__)

async def filter_rss_content(rss_url: str, user_interest: str) -> List[dict]:
    sys_prompt = replace_placeholder_in_prompt(SYSTEM_PROMPT, "user_interest", user_interest)
    rss_content = get_rss_from_url(rss_url)
    
    if rss_content is None:
        logger.error(f"无法获取RSS内容: {rss_url}")
        return []
    
    # 解析feed更新时间
    feed_update_time = datetime.strptime(rss_content["feed"]["updated"], "%a, %d %b %Y %H:%M:%S %z")
    # 如果feed_update_time距离现在超过1天，则认为rss内容尚未更新，直接退出
    if (datetime.now(feed_update_time.tzinfo) - feed_update_time).days > 1:
        logger.info(f"RSS {rss_url} 未更新，跳过")
        return []
    
    paper_infos = rss_content["entries"]
    for paper_info in paper_infos:
        paper_info["content"] = extract_paper_summary(paper_info)

    batch_inference = BatchInference()
    results = await batch_inference.create_tasks(sys_prompt, paper_infos)
    # 只保留isRelated为True，且success为True的paper_info
    results = [res for res in results if res["isRelated"] and res["success"]]

    return results


async def main():
    output = []
    for item in area_interest_list:
        rss_url = item["rss_url"]
        user_interest = item["area_interest"]
        filter_results = await filter_rss_content(rss_url, user_interest)

        # 只保留isRelated为True的paper_info
        filter_results = [paper_info for paper_info in filter_results if paper_info["isRelated"]]
        output.append({
            "rss_url": rss_url,
            "user_interest": user_interest,
            "filter_results": filter_results
        })
    
    save_results(output)

    # 如果有文件名里有temp的文件存在，则删除
    # for file in os.listdir("arxiv_updates"):
    #     if "temp" in file:
    #         os.remove(os.path.join("arxiv_updates", file))
    


if __name__ == "__main__":
    asyncio.run(main())