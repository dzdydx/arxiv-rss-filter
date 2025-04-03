from typing import List, Optional
import os
import json
from datetime import datetime

def replace_placeholder_in_prompt(prompt: str, placeholder: str, value: str) -> str:
    return prompt.replace("{{" + placeholder + "}}", value)

def extract_abstract(summary: str) -> str:
    abstract_start = summary.find("Abstract:")
    if abstract_start == -1:
        return summary
    return summary[abstract_start + len("Abstract:"):].strip()

def extract_paper_summary(entry: dict) -> str:
    title = entry["title"]
    summary = entry["summary"]
    abstract = extract_abstract(summary)

    return f"Title: {title}\nAbstract: {abstract}"

def save_results(output: List[dict], suffix: Optional[str] = None):
    # 创建 arxiv_updates 文件夹（如果不存在）
    os.makedirs("arxiv_updates", exist_ok=True)
    
    # 生成基于日期的文件名
    current_date = datetime.now().strftime("%Y-%m-%d")
    if suffix:
        output_file = os.path.join("arxiv_updates", f"{current_date}_{suffix}.json")
    else:
        output_file = os.path.join("arxiv_updates", f"{current_date}.json")
    
    # 保存结果到文件
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        