# AI Agent Client: 智能多模型协同桌面应用

## 🚀 项目简介

**AI Agent Client** 是一个基于 PyQt6 构建的创新型 Windows 本地 AI 聚合客户端。它开创性地引入了“**多模型调度与动态记忆**”架构，旨在高效平衡大型语言模型（LLM）的卓越高级推理能力与实际应用中的 Token 成本。通过智能地将任务分发给最适合的模型，并实时维护项目状态，本客户端极大地提升了用户与 AI 交互的效率和深度，为复杂项目管理和智能辅助提供了前所未有的解决方案。

## ✨ 核心特性

-   **🧠 软路由网关 (Soft-Router Gateway)**
    *   **任务难度评估机制**：
        *   包含“架构”、“算法”、“分析”、“设计模式”、“分布式”、“高并发”、“优化”等关键词，或用户输入长度超过 50 字，被评估为 **8-10 分（高难度）**。
        *   包含“代码”、“修改”、“实现”、“功能”、“调试”、“bug”等关键词，被评估为 **4-7 分（中等难度）**。
        *   其他常规问题或简单指令，被评估为 **1-3 分（低难度）**。
    *   **大模型分发策略**：
        *   **8-10 分（高难度）**：由 `ClaudeClient` (对应 Claude 3.5 Sonnet 等顶尖模型) 处理，以确保高质量的复杂推理。
        *   **4-7 分（中等难度）**：由 `GPTClient` (对应 GPT-4o 等中高端模型) 处理，平衡性能与成本。
        *   **1-3 分（低难度）**：由 `BasicClient` (对应 DeepSeek、Qwen 等经济高效模型) 处理，实现成本优化。
    *   确保“好钢用在刀刃上”，显著优化了 Token 消耗和计算资源。

-   **📝 状态化动态记忆 (Stateful Dynamic Memory)**
    *   打破了传统大模型无状态对话的限制，实现了持久化项目记忆。
    *   每隔 **3 轮对话**，后台会自动触发总结机制，凝练当前项目进度、核心解决思路和遗留问题。
    *   总结内容实时更新到 `data/project_status.md` 文件，形成一份可追溯、可读性强的项目动态文档。

-   **📊 实时可视化与现代化 UI (Real-time Visualization & Modern UI)**
    *   客户端左侧面板**实时渲染 `project_status.md` 的 Markdown 内容**，直观展示项目全局进展和关键信息。
    *   右侧聊天界面采用**现代化气泡聊天 UI** 设计，提供类似微信或 ChatGPT 的流畅交互体验。
    *   通过精心设计的 CSS 样式，确保了卓越的视觉效果和用户体验。

## 🛠️ 环境与安装

本项目推荐使用 `conda` 创建虚拟环境进行管理。

-   **Python 版本要求**: Python 3.10+

1.  **克隆仓库**:
    ```bash
    git clone https://github.com/your_username/AI-Agent-Client.git
    cd AI-Agent-Client
    ```
2.  **创建并激活 Conda 虚拟环境**:
    ```bash
    conda create -n ai_client_env python=3.10 -y
    conda activate ai_client_env
    ```
3.  **安装项目依赖**:
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ 如何配置与运行

1.  **配置 API Keys**:
    *   在项目根目录下创建 `.env` 文件。
    *   根据您所使用的模型，配置相应的 API Key。本项目支持 OpenAI 兼容接口的模型（如 DeepSeek, Qwen, OpenAI GPT系列）和 Anthropic Claude 系列模型。
    *   `.env` 文件示例:
        ```ini
        OPENAI_API_KEY="your_openai_compatible_api_key_for_gpt_client"
        OPENAI_BASE_URL="https://api.openai.com/v1" # 或您的自定义 OpenAI 兼容接口地址 (例如 DeepSeek, Qwen)
        GPT_MODEL_NAME="gpt-4o" # GPTClient 使用的模型名称

        BASIC_MODEL_API_KEY="your_openai_compatible_api_key_for_basic_client"
        BASIC_MODEL_BASE_URL="https://api.deepseek.com/v1" # 例如 DeepSeek API Base URL
        BASIC_MODEL_NAME="deepseek-chat" # BasicClient 使用的模型名称

        ANTHROPIC_API_KEY="your_anthropic_api_key_for_claude_client"
        CLAUDE_MODEL_NAME="claude-3-5-sonnet-20240620" # ClaudeClient 使用的模型名称
        ```
    *   请确保将 `your_..._api_key` 替换为您的实际 API Key。

2.  **启动应用程序**:
    ```bash
    python -m ai_client_app.main
    ```

## 📦 关于打包

本项目已配置 **GitHub Actions** 自动化工作流。当代码推送到 `main` 分支或打上 `v*.*.*` 格式的 Tag 时，GitHub Actions 将自动在云端编译项目为 Windows `.exe` 可执行文件。您可以在 GitHub 仓库的 Actions 页面下载生成的制品（Artifacts）。

---

