import os
import re
from datetime import datetime
import logging
from ai_client_app.core.api_clients import BasicClient # 假设 BasicClient 可以用于总结
from ai_client_app.core.config import MD_FILE_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemoryManager:
    def __init__(self):
        self.conversation_history = []
        self.conversation_round_count = 0
        self.basic_client = BasicClient() # 用于生成总结



    def add_message(self, sender: str, message: str):
        """
        添加对话消息到历史记录。
        """
        self.conversation_history.append({"sender": sender, "message": message})
        logging.debug(f"Added message: {sender}: {message}")

    def increment_round_count(self):
        """
        增加对话轮次计数。
        """
        self.conversation_round_count += 1
        logging.info(f"对话轮次增加，当前：{self.conversation_round_count}")

    def _generate_summary(self) -> str:
        """
        模拟或实际生成对话总结。
        目前使用 BasicClient 生成一个简单的总结。
        """
        # 提取最近几轮对话进行总结
        recent_history = self.conversation_history[-6:] # 取最近3轮对话 (用户+AI)
        
        prompt = "请根据以下对话，总结出项目当前进度、核心解决思路和遗留问题，以Markdown格式返回。如果信息不足，可以保持通用性。\\n\\n"
        for entry in recent_history:
            prompt += f"{entry['sender']}: {entry['message']}\\n"

        logging.info("开始生成对话总结...")
        try:
            summary_content = self.basic_client.generate_response(prompt)
            # 确保总结内容是Markdown格式，并且包含所需标题
            if "## 项目当前进度" not in summary_content:
                summary_content = "## 项目当前进度\\n- 暂无明确进度更新，等待进一步对话。\\n\\n" + summary_content
            if "## 核心解决思路" not in summary_content:
                summary_content += "\\n\\n## 核心解决思路\\n- 延续多模型路由和动态记忆策略."
            if "## 遗留问题" not in summary_content:
                summary_content += "\\n\\n## 遗留问题\\n- 暂无."
            return summary_content
        except Exception as e:
            logging.error(f"生成总结时调用 BasicClient 失败: {e}")
            return f"## 总结生成失败\\n- 无法生成最新总结: {e}"


    def _overwrite_project_status_file(self, summary_md: str):
        """
        覆盖更新 project_status.md 文件，只更新总结部分，保持文件顶部不变。
        """
        try:
            with open(MD_FILE_PATH, 'r', encoding='utf-8') as f:
                current_content = f.read()

            # 找到第一个 ## 项目当前进度 的位置，从那里开始替换
            # 如果文件结构改变，这里可能需要调整
            match = re.search(r'## 项目当前进度', current_content)
            if match:
                header = current_content[:match.start()]
                # 更新时间戳
                header = re.sub(
                    r'## 最后更新时间: .*',
                    f"## 最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    header
                )
                new_content = header + summary_md + "\n\n---\n\n"
            else:
                # 如果没找到标记，则直接追加
                new_content = current_content + f"\\n\\n## 对话总结 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n" + summary_md + "\n\n---\n\n"

            with open(MD_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logging.info(f"project_status.md 文件已更新: {MD_FILE_PATH}")
        except Exception as e:
            logging.error(f"更新 project_status.md 文件失败: {e}")


    def check_and_summarize(self) -> bool:
        """
        检查是否达到总结条件，如果达到则进行总结并返回True。
        """
        if self.conversation_round_count > 0 and self.conversation_round_count % 3 == 0:
            logging.info("达到总结条件，开始生成总结...")
            summary_content = self._generate_summary()
            self._overwrite_project_status_file(summary_content)
            return True
        return False