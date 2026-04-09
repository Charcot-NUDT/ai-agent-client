import sys
import os
import markdown
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QSplitter, QTextBrowser,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCursor, QFont
import logging

# 导入核心业务逻辑模块
from core.router import Router
from core.memory import MemoryManager
from core.config import MD_FILE_PATH

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MarkdownPreview(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)

    def update_content(self):
        # 注入现代化的 Markdown CSS
        md_css = """
        <style>
            body {
                font-family: "Segoe UI", "Microsoft YaHei", "Arial", sans-serif; /* 全局字体 */
                line-height: 1.7; /* 增加行高，在 1.6 到 1.8 之间 */
                color: #34495e; /* 现代深灰色文本 */
                padding: 25px; /* 增加整体 padding */
                margin: 0; /* 移除默认 body 外边距 */
            }
            h1, h2, h3, h4, h5, h6 {
                color: #2c3e50; /* 现代深灰色标题 */
                margin-top: 1em; /* 减少上边距 */
                margin-bottom: 0.5em; /* 减少下边距 */
                padding-bottom: 0.3em; /* 保持与之前类似的 padding-bottom */
            }
            h1 {
                font-size: 2em; /* 保持字号，符合“稍微减小”的相对意义，相对于默认浏览器H1 */
                border-bottom: 2px solid #e1e4e8; /* 浅灰色底部分割线，类似 GitHub */
            }
            h2 { font-size: 1.6em; }
            h3 { font-size: 1.3em; }
            p {
                margin-bottom: 1em; /* 段落间距 */
                color: #34495e; /* 现代深灰色文本 */
            }
            ul, ol {
                margin-left: 25px; /* 确保列表对齐，增加缩进 */
                padding-left: 0;
                color: #34495e; /* 现代深灰色列表文本 */
            }
            li {
                margin-bottom: 0.6em; /* 列表项行高 */
            }
            blockquote {
                border-left: 4px solid #b2bec3; /* 块引用边框颜色 */
                margin-left: 0;
                padding-left: 15px;
                color: #636e72;
                font-style: italic;
            }
            pre {
                background-color: #f8f8f8;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 12px;
                overflow-x: auto;
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
                font-size: 0.9em;
            }
            code {
                font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
                background-color: #f0f0f0;
                padding: 2px 5px;
                border-radius: 4px;
                font-size: 0.9em;
            }
            pre code {
                background-color: transparent;
                padding: 0;
            }
            a {
                color: #0984e3;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
        """

        try:
            with open(MD_FILE_PATH, 'r', encoding='utf-8') as f:
                md_content = f.read()
            html_content = markdown.markdown(md_content)
            self.setHtml(md_css + html_content) # 拼接 CSS 和 HTML
        except FileNotFoundError:
            self.setHtml(md_css + "<h2>错误</h2><p><code>project_status.md</code> 文件未找到。</p>")
        except Exception as e:
            self.setHtml(md_css + f"<h2>加载文件错误</h2><p>{e}</p>")


class ChatWindow(QWidget):
    def __init__(self, markdown_preview_widget, parent=None):
        super().__init__(parent)
        self.markdown_preview = markdown_preview_widget

        # 实例化 Router 和 MemoryManager
        try:
            self.router = Router()
            self.memory_manager = MemoryManager()
        except ValueError as e:
            QMessageBox.critical(self, "配置错误", f"初始化 API 客户端失败: {e}\n请检查 .env 文件中的 API Key 配置。")
            logging.critical(f"初始化 API 客户端失败: {e}")
            sys.exit(1) # 严重错误，退出应用程序

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.chat_display = QTextBrowser()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入你的消息...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        self.add_initial_message()

    def add_initial_message(self):
        self.append_message("System", "欢迎使用 AI 聚合客户端！请开始您的对话。", is_system=True)

    def append_message(self, sender, message, is_system=False, model_name=None):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

        html_message = ""
        if sender == "User":
            html_message = f"""<div style="background-color: #dcf8c6; color: #000000; padding: 12px; margin: 10px 10px 10px 50px; border-radius: 8px; font-family: 'Segoe UI', sans-serif;"><b>🧑‍💻 你:</b><br> {message} </div><br>"""
        elif sender == "AI":
            display_model_name = f" ({model_name})" if model_name else ""
            html_message = f"""<div style="background-color: #f1f1f1; color: #212529; padding: 12px; margin: 10px 50px 10px 10px; border-radius: 8px; font-family: 'Segoe UI', sans-serif;"><b>🤖 AI{display_model_name}:</b><br> {message} </div><br>"""
        elif is_system:
             html_message = f"""<div style="text-align: center; color: #adb5bd; font-size: 12px; margin: 5px;"><i> {message} </i></div><br>"""
        else:
            # Fallback for unexpected sender, though current logic handles User/AI/System
            html_message = f"""<div style="margin: 5px; padding: 10px; background-color: #f9f9f9; border-radius: 5px; clear: both;">
                           <p style="margin: 0; font-weight: bold;">{sender}</p>
                           <p style="margin: 0;">{message}</p>
                           </div><br>"""
        
        self.chat_display.insertHtml(html_message)
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())


    def send_message(self):
        user_message = self.message_input.text().strip()
        if not user_message:
            return

        self.append_message("User", user_message)
        self.message_input.clear()
        self.send_button.setEnabled(False)

        self.memory_manager.add_message("User", user_message)

        # 使用 QTimer.singleShot 模拟异步处理
        self.append_message("System", "AI 正在思考...", is_system=True)
        QTimer.singleShot(100, lambda: self._process_ai_response(user_message))

    def _process_ai_response(self, user_message):
        model_name, difficulty_score, ai_response_content = self.router.route_and_generate_response(user_message)

        # Display difficulty assessment as a system message
        difficulty_message = f"（难度评估：{difficulty_score}/10，由 {model_name} 处理）"
        self.append_message("System", difficulty_message, is_system=True)

        # Display AI response in a chat bubble, passing model_name separately
        self.append_message("AI", ai_response_content, model_name=model_name)

        self.memory_manager.add_message("AI", ai_response_content)
        self.memory_manager.increment_round_count()

        if self.memory_manager.check_and_summarize():
            self.append_message("System", "（后台记忆）：`project_status.md` 已更新。", is_system=True)
            self.markdown_preview.update_content()

        self.send_button.setEnabled(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 聚合客户端")
        self.setGeometry(100, 100, 1200, 800)

        self.apply_global_qss() # 应用全局 QSS

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout()
        self.central_widget.setLayout(main_layout)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Left Panel: Markdown Preview
        self.markdown_preview = MarkdownPreview()
        self.splitter.addWidget(self.markdown_preview)

        # Right Panel: Chat Window
        self.chat_window = ChatWindow(self.markdown_preview)
        self.splitter.addWidget(self.chat_window)

        # Set initial sizes for splitter
        self.splitter.setSizes([self.width() // 3, 2 * self.width() // 3])

        # Load initial markdown content
        self.markdown_preview.update_content()

    def apply_global_qss(self):
        qss = """
        QMainWindow {
            background-color: #f5f6fa; /* 浅灰白色背景 */
        }
        QTextBrowser {
            background-color: #ffffff; /* 纯白背景 */
            border: 1px solid #e0e0e0; /* 淡淡的边框 */
            border-radius: 8px; /* 圆角 */
            padding: 10px;
        }
        QLineEdit {
            border: 1px solid #dcdcdc;
            border-radius: 8px;
            padding: 8px 10px;
            font-size: 14px;
            background-color: #ffffff;
        }
        QPushButton {
            background-color: #0984e3; /* 科技蓝 */
            color: #ffffff; /* 纯白文字 */
            border: none; /* 去掉默认边框 */
            border-radius: 8px;
            padding: 8px 15px;
            font-size: 14px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #74b9ff; /* 悬停时颜色变浅 */
        }
        QPushButton:disabled {
            background-color: #cccccc;
        }
        QSplitter::handle {
            background-color: #ccc;
        }
        QSplitter::handle:hover {
            background-color: #aaa;
        }
        """
        self.setStyleSheet(qss)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置全局字体 (可选，QSS 优先级更高)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
