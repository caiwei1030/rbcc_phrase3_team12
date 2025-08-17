"""
服务模块主入口文件 - 导入所有服务功能
保持向后兼容性，同时提供模块化结构
"""

# 导入所有服务功能以保持向后兼容性
from services import *

# 为了向后兼容，也可以直接从这里导入
from services.llm_service import llm_client
