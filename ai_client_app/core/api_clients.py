import os
import time
import logging
from abc import ABC, abstractmethod
from dotenv import load_dotenv

from ai_client_app.utils.paths import get_base_path

try:
    import openai
    import anthropic
except ImportError:
    logging.warning("OpenAI or Anthropic libraries not found. API clients will not be functional.")
    openai = None
    anthropic = None

# 加载 .env 文件中的环境变量
load_dotenv(dotenv_path=os.path.join(get_base_path(), ".env"))
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BaseClient(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

class OpenAICompatibleClient(BaseClient):
    def __init__(self, api_key_env_var: str, base_url_env_var: str, default_model: str):
        self.api_key = os.getenv(api_key_env_var)
        self.base_url = os.getenv(base_url_env_var)
        self.model_name = default_model

        if not self.api_key:
            raise ValueError(f"API Key for {default_model} ({api_key_env_var}) not found in environment variables.")
        if not self.base_url:
            logging.warning(f"Base URL for {default_model} ({base_url_env_var}) not found. Using default OpenAI base URL.")
            self.base_url = "https://api.openai.com/v1" # Fallback to OpenAI default

        if openai is None:
            raise ImportError("OpenAI library not installed. Please run 'pip install openai'")

        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        logging.info(f"Initialized OpenAI compatible client for model: {self.model_name} with base URL: {self.base_url}")

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                timeout=30.0, # 30秒超时
            )
            return response.choices[0].message.content
        except openai.APIConnectionError as e:
            logging.error(f"OpenAI API connection error: {e}")
            return f"AI 助手连接失败，请检查网络或 Base URL 配置: {e}"
        except openai.RateLimitError as e:
            logging.error(f"OpenAI API rate limit exceeded: {e}")
            return "AI 助手繁忙，请稍后再试或检查您的配额。"
        except openai.AuthenticationError as e:
            logging.error(f"OpenAI API authentication error: {e}")
            return "AI 助手认证失败，请检查您的 API Key 是否有效。"
        except openai.APIStatusError as e:
            logging.error(f"OpenAI API status error (code {e.status_code}): {e}")
            return f"AI 助手服务异常，状态码 {e.status_code}。"
        except Exception as e:
            logging.error(f"An unexpected error occurred with OpenAI API: {e}")
            return f"AI 助手遇到未知错误: {e}"

class GPTClient(OpenAICompatibleClient):
    def __init__(self):
        super().__init__("OPENAI_API_KEY", "OPENAI_BASE_URL", os.getenv("GPT_MODEL_NAME", "gpt-4o"))

class BasicClient(OpenAICompatibleClient):
    def __init__(self):
        super().__init__("BASIC_MODEL_API_KEY", "BASIC_MODEL_BASE_URL", os.getenv("BASIC_MODEL_NAME", "deepseek-chat"))

class ClaudeClient(BaseClient):
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model_name = os.getenv("CLAUDE_MODEL_NAME", "claude-3-5-sonnet-20240620")

        if not self.api_key:
            raise ValueError("API Key for Claude (ANTHROPIC_API_KEY) not found in environment variables.")

        if anthropic is None:
            raise ImportError("Anthropic library not installed. Please run 'pip install anthropic'")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        logging.info(f"Initialized Anthropic client for model: {self.model_name}")

    def generate_response(self, prompt: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=30.0, # 30秒超时
            )
            return response.content[0].text
        except anthropic.APIConnectionError as e:
            logging.error(f"Anthropic API connection error: {e}")
            return f"Claude 助手连接失败，请检查网络或 Base URL 配置: {e}"
        except anthropic.RateLimitError as e:
            logging.error(f"Anthropic API rate limit exceeded: {e}")
            return "Claude 助手繁忙，请稍后再试或检查您的配额。"
        except anthropic.AuthenticationError as e:
            logging.error(f"Anthropic API authentication error: {e}")
            return "Claude 助手认证失败，请检查您的 API Key 是否有效。"
        except anthropic.APIStatusError as e:
            logging.error(f"Anthropic API status error (code {e.response.status_code}): {e}")
            return f"Claude 助手服务异常，状态码 {e.response.status_code}。"
        except Exception as e:
            logging.error(f"An unexpected error occurred with Anthropic API: {e}")
            return f"Claude 助手遇到未知错误: {e}"