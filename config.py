import streamlit as st
import os

# ========== LLM配置 ==========
# 您可以将这些配置添加到 secrets.toml 中
try:
    # 优先从secrets中读取配置
    LLM_BASE_URL = st.secrets.get("LLM_BASE_URL", "https://api.siliconflow.cn/v1")
    LLM_API_KEY = st.secrets.get("LLM_API_KEY", "sk-gbrvxyqodxyaqanixmembtvfxypgtcvtdmfjluxivnyqdzsd")
    LLM_MODEL = st.secrets.get("LLM_MODEL", "Pro/deepseek-ai/DeepSeek-R1")
    # GLM-4.5V 视觉模型配置
    GLM_VISION_MODEL = st.secrets.get("GLM_VISION_MODEL", "zai-org/GLM-4.5V")
    FASTGPT_API_KEY = st.secrets.get("FASTGPT_API_KEY", "")
    FASTGPT_DATASET_ID = st.secrets.get("FASTGPT_DATASET_ID", "")
except Exception:
    # 备用配置
    LLM_BASE_URL = "https://api.siliconflow.cn/v1"
    LLM_API_KEY = "sk-gbrvxyqodxyaqanixmembtvfxypgtcvtdmfjluxivnyqdzsd"
    LLM_MODEL = "Qwen/Qwen3-30B-A3B-Thinking-2507"
    GLM_VISION_MODEL = "zai-org/GLM-4.5V"
    FASTGPT_API_KEY = ""
    FASTGPT_DATASET_ID = ""


# 数据文件路径
DATA_DIR = "dataset/reports"
REPORTS_FILE = os.path.join("dataset", "reports.json")
PARTS_FILE = os.path.join("dataset", "parts.json")

# 图片路径
LOGO_PATH = "imgs/logo.png"
