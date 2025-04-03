import os
import json
from datetime import datetime
import pytz
from typing import List, Dict
from logger import setup_logger
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger(__name__)

def generate_rss_feed(json_data: List[Dict]) -> str:
    """将JSON数据转换为RSS feed格式
    
    Args:
        json_data: 包含论文信息的JSON数据
        
    Returns:
        RSS feed的XML字符串
    """
    # 获取当前时间
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    current_time = now.strftime("%a, %d %b %Y %H:%M:%S %z")
    
    # 生成RSS feed的头部
    rss_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:arxiv="http://arxiv.org/schemas/atom" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" version="2.0">
<channel>
    <title>arXiv Paper Filter</title>
    <link>https://github.com/{os.getenv("USER_NAME")}/arxiv_filter</link>
    <description>根据研究兴趣筛选的arXiv论文</description>
    <atom:link href="https://raw.githubusercontent.com/{os.getenv("USER_NAME")}/arxiv_filter/main/feed.xml" rel="self" type="application/rss+xml" />
    <docs>http://www.rssboard.org/rss-specification</docs>
    <language>zh-CN</language>
    <lastBuildDate>{current_time}</lastBuildDate>
    <managingEditor>{os.getenv("USER_NAME")}@github.com</managingEditor>
    <pubDate>{current_time}</pubDate>
    <skipDays>
        <day>Saturday</day>
        <day>Sunday</day>
    </skipDays>
"""
    
    # 添加每个论文条目
    for category in json_data:
        rss_url = category["rss_url"]
        user_interest = category["user_interest"]
        
        for paper in category["filter_results"]:
            # 解析发布时间
            try:
                published_time = datetime.strptime(paper["published"], "%a, %d %b %Y %H:%M:%S %z")
            except ValueError:
                published_time = now
            
            # 生成条目
            rss_content += f"""
    <item>
        <title>{paper["title"]}</title>
        <link>{paper["link"]}</link>
        <guid isPermaLink="false">oai:arXiv.org:{paper["id"]}</guid>
        <category>{user_interest}</category>
        <pubDate>{published_time.strftime("%a, %d %b %Y %H:%M:%S %z")}</pubDate>
        <arxiv:announce_type>new</arxiv:announce_type>
        <dc:rights>http://arxiv.org/licenses/nonexclusive-distrib/1.0/</dc:rights>
        <dc:creator>{paper["author"]}</dc:creator>
        <description><![CDATA[
            {paper["chineseSummary"]}
            {paper["summary"]}
        ]]></description>
    </item>"""
    
    # 添加RSS feed的尾部
    rss_content += """
</channel>
</rss>"""
    
    return rss_content

def main():
    """主函数"""
    # 获取最新的JSON文件
    arxiv_updates_dir = "arxiv_updates"
    if not os.path.exists(arxiv_updates_dir):
        logger.error("arxiv_updates目录不存在")
        return
    
    # 获取最新的JSON文件
    json_files = [f for f in os.listdir(arxiv_updates_dir) if f.endswith('.json')]
    if not json_files:
        logger.error("没有找到JSON文件")
        return
    
    latest_json = max(json_files, key=lambda x: os.path.getctime(os.path.join(arxiv_updates_dir, x)))
    json_path = os.path.join(arxiv_updates_dir, latest_json)
    
    # 读取JSON数据
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except Exception as e:
        logger.error(f"读取JSON文件时发生错误: {e}")
        return
    
    # 生成RSS feed
    rss_content = generate_rss_feed(json_data)
    
    # 保存RSS feed
    try:
        with open('feed.xml', 'w', encoding='utf-8') as f:
            f.write(rss_content)
        logger.info("RSS feed生成成功")
    except Exception as e:
        logger.error(f"保存RSS feed时发生错误: {e}")

if __name__ == "__main__":
    main() 