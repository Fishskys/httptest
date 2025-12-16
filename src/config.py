import customtkinter as ctk

# 颜色定义
COLOR_ORANGE = "#FF9933"
COLOR_YELLOW = "#FFFF00"
COLOR_BLUE = "#3366CC"
COLOR_GRAY = "#CCCCCC"
COLOR_GREEN = "#2CC985"
COLOR_RED = "#FF4B4B"

TEXT_BLACK = "#000000"
TEXT_BLUE = "#0099CC"
TEXT_WHITE = "#FFFFFF"

# 路径配置
LOG_DIR = "log"
COLLECTION_FILE = "collections.json"


# 初始化 CTK 设置
def init_app_settings():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
