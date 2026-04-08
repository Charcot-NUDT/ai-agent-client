import random
from abc import ABC, abstractmethod
import time
import logging

from ai_client_app.core.api_clients import ClaudeClient, GPTClient, BasicClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Router:
    def __init__(self):
        self.claude_client = ClaudeClient()
        self.gpt_client = GPTClient()
        self.basic_client = BasicClient()

    def _assess_difficulty(self, prompt: str) -> int:
        """
        根据prompt内容评估任务难度 (1-10分).
        """
        difficulty_score = 1
        prompt_lower = prompt.lower()

        # 高难度关键词
        high_difficulty_keywords = ["架构", "算法", "分析", "设计模式", "分布式", "高并发", "优化", "复杂逻辑"]
        if any(keyword in prompt_lower for keyword in high_difficulty_keywords) or len(prompt) > 50:
            difficulty_score = random.randint(8, 10)
        # 中等难度关键词
        elif any(keyword in prompt_lower for keyword in ["代码", "修改", "实现", "功能", "调试", "bug", "解释"]):
            difficulty_score = random.randint(4, 7)
        # 低难度
        else:
            difficulty_score = random.randint(1, 3)
        
        logging.info(f"任务难度评估: {difficulty_score}/10")
        return difficulty_score

    def route_and_generate_response(self, prompt: str) -> tuple[str, int, str]:
        """
        评估难度并路由到相应的模型生成回复。
        """
        difficulty = self._assess_difficulty(prompt)
        
        model_name = ""
        response = ""

        if difficulty >= 8:
            model_name = "Claude"
            response = self.claude_client.generate_response(prompt)
        elif difficulty >= 4:
            model_name = "GPT"
            response = self.gpt_client.generate_response(prompt)
        else:
            model_name = "Basic"
            response = self.basic_client.generate_response(prompt)
        
        return model_name, difficulty, response