"你现在是一个资深的 Python 桌面应用架构师。我要开发一个基于 PyQt6 的 Windows 本地 AI 聚合客户端。
核心需求：

界面分为左右两栏：左侧是 Markdown 实时预览窗口（读取本地 project_status.md），右侧是多模型聊天窗口。

实现一个路由模块：用户输入内容后，系统首先悄悄调用一个轻量级大模型API评估难度（1-10分），并根据分数自动选择 Claude、GPT 或普通模型进行回答。

实现一个后台记忆模块：每隔 3 轮对话，自动调用轻量级模型总结最近的上下文，并覆盖更新到 project_status.md 中，重点记录项目结构、当前进度和核心问题。

第一步：请先帮我搭建整个项目的文件结构，并写出 PyQt6 的前端 UI 框架代码（包含左右分栏、输入框、发送按钮），暂时不需要接入真正的 API，用假数据测试 UI 是否跑通。请提供详细代码。"



---


你现在是一个资深的 Python 桌面应用架构师。我已经搭建好了项目的基本目录结构：
ai_agent_client/
├── main.py
├── ui/
│   ├── __init__.py
│   └── main_window.py
├── core/
│   ├── __init__.py
│   ├── router.py
│   ├── api_clients.py
│   └── memory.py
├── data/
│   └── project_status.md
└── requirements.txt

现在，请帮我按以下详细要求，实现 `core` 目录下的三个核心业务逻辑文件：

1. **实现 `core/api_clients.py`**：
   - 创建一个基类或统一接口，包含一个 `generate_response(prompt: str) -> str` 方法。
   - 实现三个子类代表不同梯队的模型：`ClaudeClient` (最聪明)、`GPTClient` (中等)、`BasicClient` (最基础)。
   - **注意**：目前不需要接入真实的外部网络 API。请在 `generate_response` 中使用 `time.sleep` 模拟 1-2 秒的网络延迟，并返回带有模型标识的 Mock（假数据）字符串，以便我进行系统联调。

2. **实现 `core/router.py`**：
   - 编写一个调度器类。它接收用户的输入文本，评估任务难度（1-10分）。
   - 评估逻辑可以暂时用简单的规则替代（例如：包含“架构”、“算法”、“分析”等词或字数超过50字记为8-10分；包含“代码”、“修改”记为4-7分；其他记为1-3分）。
   - 根据分数路由到 `api_clients.py` 中对应的模型实例：8-10分用 Claude，4-7分用 GPT，1-3分用 Basic模型。返回模型名称、评估分数和最终的回答内容。

3. **实现 `core/memory.py`**：
   - 编写一个记忆管理类。它需要维护一个对话历史列表，记录每次的用户输入和模型输出。
   - 提供一个 `check_and_summarize()` 方法：当对话历史新增达到 3 轮时，触发总结逻辑。
   - 总结逻辑：调用 `BasicClient`（此时也可以用一段 mock 的固定文本代替），生成一段包含“项目当前进度”、“核心解决思路”、“遗留问题”的 Markdown 格式文本，并**覆盖写入**到 `data/project_status.md` 文件中。

请给出这三个文件的完整 Python 代码，要求代码结构清晰，带有详细的中文注释。


---


非常好。后台核心逻辑已经就绪。现在请帮我完善界面并连接这些逻辑。

1. **重构 `ui/main_window.py`**：
   - 使用 PyQt6 编写主窗口代码。界面分为左右两栏：左侧是 QTextBrowser 用于实时预览 `data/project_status.md` 的内容（需要使用 markdown 库解析 HTML）；右侧包含聊天历史记录框、输入框和发送按钮。
   - 引入 `core.router` 和 `core.memory` 模块。
   - 当用户点击发送按钮时：
     a. 在聊天框显示用户输入。
     b. 调用 Router 模块获取难度评分和对应模型的回复，并在聊天框打印。
     c. 将这轮对话交给 Memory 模块。如果 Memory 模块触发了总结并更新了 MD 文件，主界面需要自动读取最新的 MD 文件并刷新左侧的预览窗口。

2. **实现 `main.py`**：
   - 作为程序的唯一入口，只负责实例化 QApplication，启动并显示 main_window 中的主界面。

请给出 `ui/main_window.py` 和 `main.py` 的完整代码。注意要处理好耗时操作，确保调用模型时 UI 不会卡死（可以使用 QThread 或 QTimer 简单处理）。


---


"太棒了，本地 UI 和路由的 Mock 测试已经完美跑通。现在我们要把 core/api_clients.py 接入真实的 API。

请帮我引入 openai 等必要的官方库（如果需要请告诉我 pip install 什么），并按以下要求重构：

环境隔离：不要把 API Key 写死在代码里，请使用 os.getenv 从 .env 文件中读取。

GPTClient / BasicClient：请使用 OpenAI 的 SDK 格式，因为现在很多轻量级/中等模型（比如 DeepSeek 或 Qwen）都兼容 OpenAI 的接口格式。请允许自定义 base_url、api_key 和 model_name。

ClaudeClient：请引入 anthropic 库，接入真实的 Claude 3.5 Sonnet API。

错误处理：在请求网络时加入 try-except，如果超时或 Key 报错，返回一段友好的错误提示字符串，不要让程序崩溃。

请给出重构后的 core/api_clients.py 完整代码，并告诉我 .env 文件应该怎么写。"




---
现在程序的后台逻辑已经跑通了，但是前端 UI（特别是左侧的 Markdown 渲染）非常简陋难看。请帮我全面优化 `ui/main_window.py` 的视觉体验。

核心要求如下：
1. **注入 Markdown CSS**：在 `update_md_preview` 方法中，不要只把 raw HTML 塞给 QTextBrowser。请在生成的 HTML 前面拼接一段现代化的 CSS `<style>`。
   - 字体使用非衬线体 (如 "Segoe UI", "Microsoft YaHei", sans-serif)。
   - 标题 (h1, h2, h3) 颜色使用深灰色 (如 #2c3e50)，底部加一条细细的分割线。
   - 增加整体的 padding，让文本有呼吸感。
   - 列表 (ul, li) 增加适当的行高。
2. **全局 QSS 美化**：在 `init_ui` 中，为整个应用程序或主要控件编写 QSS (Qt Style Sheets)。
   - 整个窗口背景色设置为非常浅的灰白色 (如 #f5f6fa)。
   - 左侧和右侧的 QTextBrowser 背景设为纯白 (#ffffff)，并加上淡淡的边框和圆角。
   - 右下角的输入框 (`QTextEdit`) 和发送按钮 (`QPushButton`) 也要现代化。按钮背景设为主色调 (如科技蓝 #0984e3)，文字纯白，悬停时颜色变浅，去掉默认的丑陋边框。
3. **聊天框排版优化**：右侧的对话框在追加文本时，也请使用 HTML 格式。用户的发言和 AI 的发言请用不同的颜色或加粗来区分，让对话流看起来更像微信或 ChatGPT 的网页版。

请直接给我修改后完整的 `ui/main_window.py` 代码。

---

整个应用程序的QSS全局美化（右侧和整体框架）非常棒，达到了预期的现代科技感。现在，我需要你像素级地修补左侧的`QTextBrowser`（项目状态面板）。它容器内部渲染的HTML内容依然是丑陋的默认serif字体，且没有间距。

为了彻底治愈这种丑陋，请修改 `ui/main_window.py` 中的 `update_md_preview` 方法。你需要在生成的 raw HTML 字符串之前，直接拼接一段专业的、现代化的 `<style>` 代码块。

左侧 Markdown 注入 CSS 的具体要求如下：
1. **全局字体**：将字体家族改为 clean 的非衬线体 stack。例如：`"Segoe UI", "Microsoft YaHei", "Arial", sans-serif`。
2. **Padding**：给整个 Markdown 内容添加 `25px` 的内边距 (Padding)，让文本具有“呼吸感”，不紧贴容器边缘。
3. **颜色与标题**：
   - 标题 (`h1`, `h2`, `h3`) 的颜色改为现代深灰色 (`#2c3e50`)。
   - 标题 (`h1`) 需要稍微减小字号，并且**加一条浅灰色底部分割线** (`border-bottom: 2px solid #e1e4e8;`)，样式类似 GitHub 的文档页面。
   - 所有标题统一减少上、下边距 (margins)。
4. **列表与文本**：
   - 列表 (`ul`, `li`) 和普通文本 (`p`) 的颜色改为现代深灰色 (`#34495e`)。
   - **核心：增加行高**。将文本的 `line-height` 设置为 `#1.6` 到 `#1.8` 之间，极大地提高阅读舒适度。
   - 确保列表对齐且无丑陋的默认对齐错误。

请给出修改后完整的 `ui/main_window.py` 代码。这将使左侧看起来像一个专业的文档页面，完美匹配右侧的现代风格。


---


目前项目接入真实 API 后运行良好，但右侧的聊天界面（QTextBrowser）区分度太低，用户和 AI 的消息混在一起，体验不好。

请帮我重构 UI 模块中负责在聊天框追加文本的代码（通常在 handle_send 或类似处理模型回复的逻辑中），将其改为类似微信或 ChatGPT 的“聊天气泡”样式。

因为 QTextBrowser 对现代 CSS 支持有限，请严格遵循以下 HTML 结构和内联样式注入文本：

1. **用户发出的消息 (右侧/绿色气泡风格)**：
   - 使用包含 margin 的 div，使其靠右视觉对齐或凸显。
   - 样式参考：`<div style="background-color: #dcf8c6; color: #000000; padding: 12px; margin: 10px 10px 10px 50px; border-radius: 8px; font-family: 'Segoe UI', sans-serif;"><b>🧑‍💻 你:</b><br> {user_text} </div>`

2. **AI 返回的消息 (左侧/浅灰气泡风格)**：
   - 样式参考：`<div style="background-color: #f1f1f1; color: #212529; padding: 12px; margin: 10px 50px 10px 10px; border-radius: 8px; font-family: 'Segoe UI', sans-serif;"><b>🤖 AI ({model_name}):</b><br> {ai_response} </div>`

3. **系统提示文字 (居中/浅色小字)**：
   - 像“正在思考...”或路由评估状态，使用：`<div style="text-align: center; color: #adb5bd; font-size: 12px; margin: 5px;"><i> {system_text} </i></div>`

请确保每一次对话追加时，都插入适当的空行或换行 `<br>` 避免气泡粘连。请直接给出修改后的相关代码片段（不需要输出整个文件，只输出追加聊天记录的方法即可）。


---


"请帮我为当前项目编写一份专业、详尽的 README.md 文件。
这个项目是我开发的一个基于 PyQt6 的 Windows 本地 AI 聚合客户端（多智能体协同架构）。

请在 README 中包含以下板块，格式要求美观清晰：

项目简介：强调其首创的“多模型调度与动态记忆”架构，旨在平衡大模型的高级推理能力与 Token 成本。

核心特性：

软路由网关：根据用户输入难度（1-10分）自动分配不同梯队的大模型（如 DeepSeek、Claude 等）执行。

状态化动态记忆：每隔 3 轮对话自动触发后台总结，打破大模型无状态限制。

实时可视化：左侧 Markdown 面板实时渲染项目全局进度，右侧采用现代化气泡聊天 UI。

环境与安装：说明需要 Python 3.10+，并提供 pip install -r requirements.txt 的安装指令。

如何配置与运行：说明需要配置哪些 API Key，以及执行 python main.py 即可启动。

关于打包：说明项目已配置 GitHub Actions，可自动在云端编译为 Windows .exe 可执行文件。

请直接输出完整的 Markdown 内容。"



---


"项目打包成 PyInstaller --onefile 的 exe 后，在 Windows 运行报错：
FileNotFoundError: [Errno 2] No such file or directory: '...AppData\\Local\\Temp\\_MEI497242\\ui\\..\\data\\project_status.md'

这是经典的 PyInstaller 路径问题。请帮我重构项目中所有涉及文件读写（特别是 core/memory.py 和 ui/main_window.py 等处理 data 目录和 .env 的地方）的路径逻辑。

修改要求：

在项目核心位置（比如写一个独立的 utils/paths.py 或直接在调用的地方）编写一个获取绝对基准路径的函数：
如果 getattr(sys, 'frozen', False) 为真，则基准路径为 os.path.dirname(sys.executable)（即 exe 所在的真实目录）。
否则，基准路径为当前脚本所在的项目根目录。

将所有的相对路径硬编码（如 "data/project_status.md"、".env"）全部改为基于这个基准路径的绝对路径 (os.path.join(base_path, "data", "project_status.md"))。

确保程序启动时，如果绝对路径下不存在 data 目录，能使用 os.makedirs 正确创建。

请直接帮我修改相关代码文件，彻底解决这个打包后的相对路径问题。"