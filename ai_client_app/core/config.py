import os
import sys

# 强制判断是否为打包后的 exe 运行环境
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # 严格指向 exe 文件所在的物理目录
else:
    # 假设 config.py 在 core 目录下，往上一级就是项目根目录
    # ai_client_app/core/config.py -> ai_client_app/core -> ai_client_app
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
MD_FILE_PATH = os.path.join(DATA_DIR, "project_status.md")

# 在模块加载时就强制确保物理目录存在
os.makedirs(DATA_DIR, exist_ok=True)
