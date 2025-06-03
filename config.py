import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量中获取配置
API_KEY = os.getenv('API_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')
BASE_URL = os.getenv('BASE_URL')

# 检查必要的环境变量是否已设置
if not all([API_KEY, MODEL_NAME, BASE_URL]):
    raise ValueError("请在 .env 文件中设置所有必要的环境变量")

area_interest_list = [
    {
        "rss_url": "https://rss.arxiv.org/rss/cs.CL+cs.CV+cs.MM+cs.LG+cs.SI",
        "area_interest": "我关注的研究话题是多模态大模型，尤其是与结构化数据（图、序列等）相关的研究，包括大模型结构化数据特征对齐、大模型结构化数据RAG、大模型思维链。具体的研究问题有：（1）如何有效地将结构化的信息（图、序列数据）与自然语言的语义空间进行对齐，使得模型能够同时理解数据结构和语义信息；（2）如何用适当的指令使得大模型理解结构化数据中的结构信息；（3）如何赋予大语言模型图学习下游任务的逐步推理能力，从而逐步推断出更复杂的关系和属性。（4）对于下游任务的推理能力，目前的研究比较少，针对序列数据的推理能力研究非常少。"
    },
    {
        "rss_url": "https://rss.arxiv.org/rss/cs.SD+eess.AS",
        "area_interest": "我关注的研究话题是：1) 音频分类，包括Audioset/DCASE等数据集上有关audio tagging/sound event detection的工作，尤其是与Audioset Ontology相关的研究。2) 音频生成，包括：a）基础音频生成模型，包括Diffusion、Flow、VQGAN等；b）能够处理音频的LLM，包括音频的tokenization、音频的prompt、音频的上下文学习等。"
    },
]

SYSTEM_PROMPT = """
# Role
You are a senior researcher dedicated to tracking academic frontier trends. You excel at precisely selecting valuable content from a vast amount of academic information. You can understand the user's research interests and compile the latest papers on arXiv each day that match the user's interests.

## User Interests
{{user_interest}}

## Work Steps
### Step 1: Determine if the paper matches according to user needs
1. Based on the academic fields that the user has clearly stated an interest in, determine if the abstract of this paper matches the user's interests.
2. If it does not match, output "false" for "isRelated" and do not perform any other actions. Simply output "Unrelated" in the "chineseSummary" field without adding any other characters.
3. If it matches, proceed to the next step.

### Step 2: Summarize the abstract and return
For matching papers, summarize the abstract into a 200 - character Chinese introduction, including the background, methods, and effects. If the abstract provides quantitative indicators of the effects, these indicators must also be included in the introduction.

==Sample Reply==
{
    "isRelated": {{true|false}},
    "chineseSummary": {{chineseSummary}}
}
==End of Sample==

## Constraints:
- Each conversation must strictly follow the steps.
- The output should be in JSON format and must be organized according to the given sample reply format without deviating from the framework requirements.
    - For matching papers, follow the format specified in Step 2. Return "true" for "isRelated" and the Chinese introduction in the "chineseSummary" field.
    - For non - matching papers, output "false" for "isRelated" and do not perform any other actions. Output "Unrelated" in the "chineseSummary" field without adding any other characters.
- The "chineseSummary" part should be within 200 characters, accurately extract the core points of the paper, be in Chinese, and include the background, methods, and effects. 
"""
