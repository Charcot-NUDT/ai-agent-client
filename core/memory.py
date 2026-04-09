import os
import re
from typing import List, Dict
from datetime import datetime
from core.api_clients import BasicClient
from core.config import MD_FILE_PATH

class MemoryManager:
    """
    记忆管理类，负责维护对话历史，并在特定条件触发时生成总结并写入到文件。
    """
    def __init__(self):
        """
        初始化记忆管理器。
        """
        self.conversation_history: List[Dict[str, str]] = []
        self.conversation_round_count = 0
        self.summary_client = BasicClient() # 用于生成总结的客户端，这里使用 BasicClient

        # 确保 project_status.md 文件存在
        if not os.path.exists(MD_FILE_PATH):
            self._create_initial_project_status_file()

    def _create_initial_project_status_file(self):
        """
        如果 project_status.md 不存在，则创建它并写入初始内容。
        """
        initial_content = (
            "# 项目状态报告\n\n"
            f"最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "## 项目概述\n\n"
            "这是一个基于 PyQt6 的 AI 聚合客户端项目，旨在通过智能路由和记忆功能，"
            "提高AI模型的使用效率和项目管理能力。\n\n"
            "## 核心解决思路\n\n"
            "1.  **UI 模块**: 基于 PyQt6 构建，提供 Markdown 预览和聊天交互界面。\n"
            "2.  **路由模块**: 根据用户输入难度，智能选择合适的AI模型进行响应。\n"
            "3.  **记忆模块**: 定期总结对话内容，更新项目状态，形成动态文档。\n"
            "4.  **API 客户端**: 封装不同AI模型的API调用，提供统一接口。\n\n"
            "## 当前进度\n\n"
            "-   项目基本目录结构已搭建完成。\n"
            "-   UI 框架已初步实现，并支持 Markdown 预览和聊天功能。\n"
            "-   模拟的路由和记忆功能已集成到 UI 中进行初步测试。\n"
            "-   核心业务逻辑模块 (router, api_clients, memory) 已创建占位文件。\n\n"
            "## 遗留问题与待办事项\n\n"
            "-   实现 core/api_clients.py 中的真实模型API调用。\n"
            "-   实现 core/router.py 中的高级难度评估和模型选择逻辑。\n"
            "-   实现 core/memory.py 中的智能总结逻辑。\n"
            "-   将模拟功能替换为核心模块的真实实现。\n"
        )
        with open(MD_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(initial_content)
        print(f"[DEBUG] Created initial project_status.md at {MD_FILE_PATH}")

    def add_message(self, sender: str, message: str):
        """
        向对话历史中添加一条消息。
        """
        self.conversation_history.append({"sender": sender, "message": message})

    def increment_round_count(self):
        """
        增加对话轮数计数。
        """
        self.conversation_round_count += 1

    def _generate_summary(self) -> str:
        """
        生成对话总结。
        这里暂时使用 BasicClient 进行模拟总结，未来可以替换为更智能的总结逻辑。
        """
        # 获取最近几轮的对话，用于总结
        # 考虑到每轮是用户+AI两条消息，如果3轮，就是6条消息
        recent_conversation_text = "\n".join(
            [f"{item['sender']}: {item['message']}" for item in self.conversation_history[-6:]]
        )
        prompt_for_summary = (
            f"请根据以下最近的对话内容，生成一份关于项目状态的Markdown总结，内容包括："
            f"当前项目进度、核心解决思路和遗留问题。\n\n对话内容：\n{recent_conversation_text}"
        )
        # 调用 BasicClient 模拟总结，实际应根据需求调用合适的模型
        summary = self.summary_client.generate_response(prompt_for_summary)
        
        # 格式化总结为 Markdown
        formatted_summary = (
            f"\n## 对话总结 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"**本次总结基于最近 {min(len(self.conversation_history) // 2, 3)} 轮对话。**\n\n"
            f"{summary}\n"
        )
        return formatted_summary

    def check_and_summarize(self) -> bool:
        """
        检查是否达到总结条件 (每3轮对话)，如果达到则生成总结并写入文件。
        :return: 如果进行了总结，返回 True，否则返回 False。
        """
        if self.conversation_round_count > 0 and self.conversation_round_count % 3 == 0:
            print("[DEBUG] Reached summary threshold. Generating summary...")
            summary_content = self._generate_summary()
            self._overwrite_project_status_file(summary_content)
            return True
        return False

    def _overwrite_project_status_file(self, new_summary: str):
        """
        覆盖写入 project_status.md 文件。
        """
        try:
            # 读取现有内容，并替换旧的总结部分，或者追加
            # 为了简化，这里直接在文件末尾追加新总结，并更新“最后更新时间”
            # 在实际应用中，可能需要更复杂的Markdown解析和更新逻辑
            with open(MD_FILE_PATH, 'r+', encoding='utf-8') as f:
                content = f.read()
                f.seek(0) # 回到文件开头
                # 更新“最后更新时间”
                updated_time_line = f"最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                content = re.sub(r'最后更新时间: .*\n', updated_time_line, content, 1)
                
                # 将新总结添加到文件末尾
                f.write(content.strip() + "\n\n" + new_summary.strip() + "\n")
                f.truncate() # 截断文件，以防新内容比旧内容短
            print(f"[DEBUG] project_status.md updated successfully at {MD_FILE_PATH}")
        except Exception as e:
            print(f"[ERROR] Failed to update project_status.md: {e}")
