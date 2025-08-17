"""
服务模块初始化文件 - 统一导入所有服务功能
"""

# LLM服务
from .llm_service import (
    get_llm_client,
    analyze_json_with_llm
)

# 搜索服务
from .search_service import (
    find_parts_for_product,
    search_fastgpt_kb
)

# 摄像头服务
from .camera_service import (
    start_camera_recognition,
    stop_camera_recognition,
    capture_and_recognize_from_image,
    get_current_camera_frame,
    is_camera_active,
    is_ai_recognition_active,
    get_latest_recognition_result,
    clear_recognition_result,
    set_recognition_result,
    get_camera_status_debug
)

# 诊断服务
from .diagnostic_service import (
    diagnose_model_config,
    test_alternative_vision_models,
    auto_fix_vision_model
)

# 为了保持向后兼容性，导出所有函数
__all__ = [
    # LLM服务
    'get_llm_client',
    'analyze_json_with_llm',
    
    # 搜索服务
    'find_parts_for_product', 
    'search_fastgpt_kb',
    
    # 摄像头服务
    'start_camera_recognition',
    'stop_camera_recognition', 
    'capture_and_recognize_from_image',
    'get_current_camera_frame',
    'is_camera_active',
    'is_ai_recognition_active',
    'get_latest_recognition_result',
    'clear_recognition_result',
    'set_recognition_result',
    'get_camera_status_debug',
    
    # 诊断服务
    'diagnose_model_config',
    'test_alternative_vision_models',
    'auto_fix_vision_model'
]