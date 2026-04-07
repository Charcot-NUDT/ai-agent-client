import os
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

# 导入真实 API 客户端和 dotenv
import openai
import anthropic
from dotenv import load_dotenv

# 在文件顶部加载 .env 文件
load_dotenv()

class BaseClient(ABC):
    """
    模型 API 客户端的抽象基类。
    定义了模型客户端的通用接口。
    """
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """
        根据给定的 prompt 生成模型响应。
        :param prompt: 用户输入或待处理的文本。
        :return: 模型生成的响应字符串。
        """
        pass

class OpenAICompatibleClient(BaseClient):
    """
    兼容 OpenAI API 接口的模型客户端基类。
    适用于 GPT、DeepSeek、Qwen 等兼容 OpenAI 接口的模型。
    """
    def __init__(
        self,
        model_name: str,
        api_key_env_var: str, # 环境变量名
        base_url_env_var: Optional[str] = None, # 环境变量名
        default_model: str = "gpt-3.5-turbo",
        timeout: int = 30
    ):
        super().__init__(model_name)
        self.api_key = os.getenv(api_key_env_var)
        self.base_url = os.getenv(base_url_env_var) if base_url_env_var else None
        self.default_model = default_model
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(f"API Key for {self.model_name} (env var: {api_key_env_var}) not found in environment variables.")

        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def _make_api_call(self, messages: list[Dict[str, str]]) -> str:
        """
        执行 OpenAI 兼容的 API 调用。
        """
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=0.7,
                timeout=self.timeout
            )
            return response.choices[0].message.content if response.choices else "未能获取有效回复。"
        except openai.APIConnectionError as e:
            return f"API 连接错误: {e}. 请检查网络连接或 Base URL。"
        except openai.RateLimitError as e:
            return f"API 请求频率受限: {e}. 请稍后再试。"
        except openai.AuthenticationError as e:
            return f"API 认证失败: {e}. 请检查 {self.model_name} 的 API Key 是否有效。"
        except openai.APIStatusError as e:
            return f"API 返回错误状态: {e.status_code} - {e.response}. {e.message}"
        except Exception as e:
            return f"发生未知错误: {e}"

    def generate_response(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        return self._make_api_call(messages)


class GPTClient(OpenAICompatibleClient):
    """
    基于 OpenAI GPT 模型的客户端。
    """
    def __init__(self):
        super().__init__(
            model_name="GPT (OpenAI)",
            api_key_env_var="OPENAI_API_KEY",
            base_url_env_var="OPENAI_BASE_URL", # 可选，用于自定义代理或兼容 API
            default_model="gpt-3.5-turbo" # 可以是 gpt-4o, gpt-4-turbo 等
        )

class BasicClient(OpenAICompatibleClient):
    """
    最基础的模型客户端，兼容 OpenAI API 格式。
    可用于部署本地模型或价格更低的第三方模型。
    """
    def __init__(self):
        super().__init__(
            model_name="Basic Model (DeepSeek/Qwen)",
            api_key_env_var="BASIC_MODEL_API_KEY", # 针对基础模型设定的 API Key
            base_url_env_var="BASIC_MODEL_BASE_URL", # 基础模型的 Base URL
            default_model="deepseek-chat" # 例如 'deepseek-chat', 'qwen-turbo'
        )


class ClaudeClient(BaseClient):
    """
    Anthropic Claude 模型的客户端。
    """
    def __init__(self):
        super().__init__("Claude (Anthropic)")
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.default_model = "claude-3-5-sonnet-20240620" # Claude 3.5 Sonnet 是目前推荐模型
        self.timeout = 60 # Claude API 默认超时时间可能长一些

        if not self.api_key:
            raise ValueError(f"API Key for {self.model_name} (env var: ANTHROPIC_API_KEY) not found in environment variables.")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_response(self, prompt: str) -> str:
        try:
            message = self.client.messages.create(
                model=self.default_model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=self.timeout
            )
            return message.content[0].text if message.content else "未能获取有效回复。"
        except anthropic.APIStatusError as e:
            return f"Claude API 状态错误: {e.response.status_code} - {e.response.text}. 请检查 API Key 或模型配置。"
        except anthropic.APIConnectionError as e:
            return f"Claude API 连接错误: {e}. 请检查网络连接。"
        except anthropic.AuthenticationError as e:
            return f"Claude API 认证失败: {e}. 请检查 ANTHROPIC_API_KEY 是否有效。"
        except Exception as e:
            return f"Claude API 发生未知错误: {e}"


# --- 测试用例 (仅在直接运行此文件时执行) ---
if __name__ == '__main__':
    print("--- 正在测试 api_clients.py ---")
    # 为了避免实际的网络请求，这里我们仍然使用模拟的方式
    # 实际运行时请确保 .env 文件配置正确

    # 模拟加载环境变量 (实际运行时 load_dotenv() 会在文件顶部执行)
    # os.environ["OPENAI_API_KEY"] = "sk-..."
    # os.environ["BASIC_MODEL_API_KEY"] = "sk-..."
    # os.environ["BASIC_MODEL_BASE_URL"] = "https://api.deepseek.com/v1"
    # os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

    # 尝试实例化客户端，并捕获可能的 ValueError
    try:
        gpt_client = GPTClient()
        print(f"GPTClient 实例化成功 (模型: {gpt_client.default_model})")
    except ValueError as e:
        print(f"GPTClient 实例化失败: {e}. 请确保设置 OPENAI_API_KEY。")
        gpt_client = None # 将客户端设为 None 以防止后续调用

    try:
        basic_client = BasicClient()
        print(f"BasicClient 实例化成功 (模型: {basic_client.default_model}, Base URL: {basic_client.base_url})")
    except ValueError as e:
        print(f"BasicClient 实例化失败: {e}. 请确保设置 BASIC_MODEL_API_KEY 和 BASIC_MODEL_BASE_URL。")
        basic_client = None

    try:
        claude_client = ClaudeClient()
        print(f"ClaudeClient 实例化成功 (模型: {claude_client.default_model})")
    except ValueError as e:
        print(f"ClaudeClient 实例化失败: {e}. 请确保设置 ANTHROPIC_API_KEY。")
        claude_client = None

    test_prompt = "请用一句话介绍你自己。"

    if gpt_client:
        print(f"\n--- GPTClient ({gpt_client.model_name}) 响应 ---")
        response = gpt_client.generate_response(test_prompt)
        print(response)
        time.sleep(1)

    if basic_client:
        print(f"\n--- BasicClient ({basic_client.model_name}) 响应 ---")
        response = basic_client.generate_response(test_prompt)
        print(response)
        time.sleep(1)

    if claude_client:
        print(f"\n--- ClaudeClient ({claude_client.model_name}) 响应 ---")
        response = claude_client.generate_response(test_prompt)
        print(response)
        time.sleep(1)

    print("\n--- api_clients.py 测试结束 ---")