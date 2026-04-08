import sys
import os

def get_base_path():
    """
    获取应用程序的绝对基准路径。
    如果程序打包成 exe 运行，则返回 exe 所在的目录。
    否则，返回当前脚本所在的项目根目录。
    """
    if getattr(sys, 'frozen', False):
        # 当程序被 PyInstaller 打包成单个文件时
        base_path = os.path.dirname(sys.executable)
    else:
        # 当程序作为脚本运行时
        # ai_client_app/utils/paths.py -> ai_client_app/utils -> ai_client_app -> project_root
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return base_path
