import os
import sys

def get_base_path():
    """获取程序运行的真实外层绝对路径，彻底告别 _MEI 临时目录"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的 exe，返回 exe 文件所在的物理目录
        return os.path.dirname(sys.executable)
    else:
        # 如果是开发环境，返回项目根目录 (假设 utils 放在 core 下，根目录就是上一级)
        # ai_client_app/core/utils.py -> ai_client_app/core -> ai_client_app
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
