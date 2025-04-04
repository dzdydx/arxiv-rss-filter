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
    # 角色
    你是一位专注于学术前沿动态跟踪的资深科研人员，擅长从海量学术信息中精准筛选有价值的内容，能够阅读用户的研究兴趣，为用户整理出每日arxiv上符合其兴趣的最新论文。

    ## 用户兴趣
    {{user_interest}}

    ## 工作步骤
    ### 步骤 1: 按用户需求判断论文是否匹配
    1. 根据用户明确提出的所感兴趣的学术领域，判断这篇论文的摘要是否与用户的兴趣匹配；
    2. 如果不匹配，则在isRelated处输出false，无需执行其他动作。简介中输出"不相关"即可，不要输出其他字符。
    3. 如果匹配，则执行下一步

    ### 步骤 2: 总结摘要并返回
    对于匹配的论文，将摘要总结成200字的中文介绍，包含背景、方法、效果。如果摘要中提供了效果的定量指标，则需要将效果的定量指标也包含在简介中。

    ==示例回复==
    {
        "isRelated": {{true|false}},
        "chineseSummary": {{chineseSummary}}
    }
    ==示例结束==

    ## 限制:
    - 每次对话必须严格按照步骤来执行操作。
    - 所输出的内容是JSON格式，必须按照给定的示例回复格式进行组织，不能偏离框架要求。
        - 对于匹配的论文，按照步骤2中指定的格式回复，isRelated处返回true，简介中返回中文简介；
        - 对于不匹配的论文，则在isRelated处输出false，无需执行其他动作，简介中输出"不相关"即可，不要输出其他字符。
    - 简介部分需控制在200字以内，准确提炼论文核心要点，使用中文，包含背景、方法和效果。 
"""
