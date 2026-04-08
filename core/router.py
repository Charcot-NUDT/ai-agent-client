import re
import random
from typing import Tuple
from core.api_clients import ClaudeClient, GPTClient, BasicClient, BaseClient

class Router:
    """
    路由器类，负责评估用户输入难度并分发到合适的模型。
    """
    def __init__(self):
        """
        初始化路由器，并实例化不同类型的API客户端。
        """
        self.claude_client = ClaudeClient()
        self.gpt_client = GPTClient()
        self.basic_client = BasicClient()

    def _assess_difficulty(self, prompt: str) -> int:
        """
        评估用户输入的难度 (1-10分)。
        规则:
        - 包含“架构”、“算法”、“分析”等词或字数超过50字记为8-10分。
        - 包含“代码”、“修改”记为4-7分。
        - 其他记为1-3分。
        """
        prompt_lower = prompt.lower()

        # 高难度关键词
        high_difficulty_keywords = ["架构", "算法", "分析", "设计模式", "分布式", "高并发", "优化"]
        if any(keyword in prompt_lower for keyword in high_difficulty_keywords) or len(prompt) > 50:
            return random.randint(8, 10)

        # 中等难度关键词
        medium_difficulty_keywords = ["代码", "修改", "实现", "功能", "调试", "bug"]
        if any(keyword in prompt_lower for keyword in medium_difficulty_keywords):
            return random.randint(4, 7)

        # 低难度
        return random.randint(1, 3)

    def route_and_generate_response(self, prompt: str) -> Tuple[str, int, str]:
        """
        路由用户请求到合适的模型，并生成响应。
        返回 (模型名称, 难度分数, 响应内容)。
        """
        difficulty_score = self._assess_difficulty(prompt)
        
        selected_client: BaseClient
        if difficulty_score >= 8:
            selected_client = self.claude_client
        elif difficulty_score >= 4:
            selected_client = self.gpt_client
        else:
            selected_client = self.basic_client
        
        response_content = selected_client.generate_response(prompt)
        return selected_client.model_name, difficulty_score, response_content

if __name__ == '__main__':
    # 简单的测试用例
    print("--- 测试路由器 ---")
    router = Router()

    test_prompts = [
        "请详细分析一下大规模分布式系统中的一致性哈希算法的实现原理和优缺点。", # 期望 Claude
        "如何使用Python实现一个简单的RESTful API接口？请提供示例代码。", # 期望 GPT
        "你好，请问现在几点？", # 期望 Basic
        "如何优化一个高并发系统的数据库连接池设计？", # 期望 Claude
        "帮我修改一下这段 Python 代码，让它更高效。", # 期望 GPT
        "今天的日程安排是什么？" # 期望 Basic
    ]

    for prompt in test_prompts:
        print(f"\n用户输入: {prompt}")
        model_name, difficulty, response = router.route_and_generate_response(prompt)
        print(f"路由结果: 模型={model_name}, 难度={difficulty}")
        print(f"模型响应: {response}")
