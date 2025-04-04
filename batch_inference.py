import asyncio
import sys
import json
from datetime import datetime
import uvloop
from volcenginesdkarkruntime import AsyncArk
from typing import List, Optional
from config import API_KEY, BASE_URL, MODEL_NAME
from logger import setup_logger
from utils import save_results
# 配置日志
logger = setup_logger(__name__)

class BatchInference:
    """批量推理处理类"""
    
    def __init__(self):
        """初始化 OpenAI 客户端"""
        self.client = AsyncArk(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        self.task_num = 50  # 每个 worker 处理的任务数

    async def process_single_task(
        self,
        worker_id: int,
        task_index: int,
        system_prompt: str,
        user_content: Optional[dict]
    ) -> Optional[dict]:
        """处理单个任务
        
        Args:
            worker_id: worker ID
            task_index: 任务索引
            system_prompt: 系统提示词
            user_content: 用户内容
            
        Returns:
            处理结果或 None（如果失败）
        """
        if not user_content:
            logger.info(f"Worker {worker_id} task {task_index} skipped (None input)")
            return None
            
        logger.info(f"Worker {worker_id} task {task_index} is running.")
        try:
            completion = await self.client.batch_chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content["content"]},
                ],
                temperature=0.8
            )
            result = completion.choices[0].message.content
            logger.info(f"Worker {worker_id} task {task_index} is completed.")
            try:
                # 将字符串结果解析为字典对象
                result_dict = json.loads(result)
                result_dict.update(user_content)
                result_dict["success"] = True
                return result_dict
            except json.JSONDecodeError as e:
                logger.error(f"Worker {worker_id} task {task_index} failed to parse JSON: {e}")
                logger.error(f"Raw response content: {result}")
                # 创建一个包含原始内容的字典，并设置isRelated为false
                error_result = {
                    "success": False,
                    "isRelated": True, # 解析失败，看看LLM返回了什么东西
                    "raw_response": result,
                    "chineseSummary": "解析失败，请查看原始内容",
                    "error": str(e)
                }
                error_result.update(user_content)
                return error_result
        except Exception as e:
            logger.error(f"Worker {worker_id} task {task_index} failed with error: {e}")
            return None

    async def worker(
        self,
        worker_id: int,
        task_num: int,
        system_prompt: str,
        user_content: List[dict]
    ) -> List[dict]:
        """单个 worker 处理多个任务
        
        Args:
            worker_id: worker ID
            task_num: 任务数量
            system_prompt: 系统提示词
            user_content: 用户内容列表
            
        Returns:
            处理结果列表
        """
        logger.info(f"Worker {worker_id} is starting.")
        tasks = [self.process_single_task(worker_id, i, system_prompt, content) for i, content in enumerate(user_content)]
        results = await asyncio.gather(*tasks)
        logger.info(f"Worker {worker_id} is completed.")
        return results

    async def create_tasks(
        self,
        system_prompt: str,
        user_content: List[dict]
    ) -> List[dict]:
        """创建并执行批量任务
        
        Args:
            system_prompt: 系统提示词
            user_content: 用户内容列表
            
        Returns:
            处理结果列表
        """
        start_time = datetime.now()
        total_items = len(user_content)
        
        # 计算 worker 数量
        max_concurrent_tasks = max(1, (total_items + self.task_num - 1) // self.task_num)
        
        logger.info(f"Processing {total_items} items with {max_concurrent_tasks} workers")

        # 填充数据以确保任务数量一致
        padding_size = (max_concurrent_tasks * self.task_num) - total_items
        if padding_size > 0:
            user_content.extend([None] * padding_size)
            logger.info(f"Padded content with {padding_size} empty items")

        # 创建并执行任务
        tasks = [
            self.worker(i, self.task_num, system_prompt, user_content[i * self.task_num:(i + 1) * self.task_num])
            for i in range(max_concurrent_tasks)
        ]
        all_results = await asyncio.gather(*tasks)
        
        # 处理结果
        actual_results = [result for worker_results in all_results for result in worker_results][:total_items]
        total_success = sum(1 for result in actual_results if result is not None)
        success_rate = (total_success / total_items) * 100
        
        # 记录统计信息
        end_time = datetime.now()
        logger.info(f"Completed in {end_time - start_time}")
        logger.info(f"Total items processed: {total_items}")
        logger.info(f"Successful items: {total_success}")
        logger.info(f"Success rate: {success_rate:.2f}%")

        # 返回之前，保存结果到文件，以免后续运行时重复推理
        save_results(actual_results, f"temp_{datetime.now().strftime('%H-%M-%S')}")

        return actual_results

def main():
    """主函数"""
    # 测试用例

    test_system_prompt = """
        # 角色
        你是一位专注于学术前沿动态跟踪的资深科研人员，擅长从海量学术信息中精准筛选有价值的内容，能够阅读用户的研究兴趣，为用户整理出每日arxiv上符合其兴趣的最新论文。

        ## 用户兴趣
        我关注的研究话题是多模态大模型，尤其是与结构化数据（图、序列等）相关的研究，包括大模型结构化数据特征对齐、大模型结构化数据RAG、大模型思维链。具体的研究问题有：（1）如何有效地将结构化的信息（图、序列数据）与自然语言的语义空间进行对齐，使得模型能够同时理解数据结构和语义信息；（2）如何用适当的指令使得大模型理解结构化数据中的结构信息；（3）如何赋予大语言模型图学习下游任务的逐步推理能力，从而逐步推断出更复杂的关系和属性。（4）对于下游任务的推理能力，目前的研究比较少，针对序列数据的推理能力研究非常少。

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

    test_user_content = [
        """Title: GraphMaster: Automated Graph Synthesis via LLM Agents in Data-Limited Environments
        Abstract: The era of foundation models has revolutionized AI research, yet Graph Foundation Models (GFMs) remain constrained by the scarcity of large-scale graph corpora. Traditional graph data synthesis techniques primarily focus on simplistic structural operations, lacking the capacity to generate semantically rich nodes with meaningful textual attributes: a critical limitation for real-world applications. While large language models (LLMs) demonstrate exceptional text generation capabilities, their direct application to graph synthesis is impeded by context window limitations, hallucination phenomena, and structural consistency challenges. To address these issues, we introduce GraphMaster, the first multi-agent framework specifically designed for graph data synthesis in data-limited environments. GraphMaster orchestrates four specialized LLM agents (Manager, Perception, Enhancement, and Evaluation) that collaboratively optimize the synthesis process through iterative refinement, ensuring both semantic coherence and structural integrity. To rigorously evaluate our approach, we create new data-limited "Sub" variants of six standard graph benchmarks, specifically designed to test synthesis capabilities under realistic constraints. Additionally, we develop a novel interpretability assessment framework that combines human evaluation with a principled Grassmannian manifold-based analysis, providing both qualitative and quantitative measures of semantic coherence. Experimental results demonstrate that GraphMaster significantly outperforms traditional synthesis methods across multiple datasets, establishing a strong foundation for advancing GFMs in data-scarce environments.""",
        """Title: Federated Learning for Cross-Domain Data Privacy: A Distributed Approach to Secure Collaboration
        Abstract: This paper proposes a data privacy protection framework based on federated learning, which aims to realize effective cross-domain data collaboration under the premise of ensuring data privacy through distributed learning. Federated learning greatly reduces the risk of privacy breaches by training the model locally on each client and sharing only model parameters rather than raw data. The experiment verifies the high efficiency and privacy protection ability of federated learning under different data sources through the simulation of medical, financial, and user data. The results show that federated learning can not only maintain high model performance in a multi-domain data environment but also ensure effective protection of data privacy. The research in this paper provides a new technical path for cross-domain data collaboration and promotes the application of large-scale data analysis and machine learning while protecting privacy."""
    ]

    # 创建批处理实例并运行
    batch_inference = BatchInference()
    
    if sys.version_info >= (3, 11):
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            results = runner.run(batch_inference.create_tasks(test_system_prompt, test_user_content))
    else:
        uvloop.install()
        results = asyncio.run(batch_inference.create_tasks(test_system_prompt, test_user_content))
    
    # 保存输出结果，去掉None
    results = [result for result in results if result is not None]
    with open("results.json", "w", encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results

if __name__ == "__main__":
    main()