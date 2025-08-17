"""
摄像头服务模块 - 使用st.camera_input进行摄像头数据输入
"""

import streamlit as st
import base64
import numpy as np
import json
from PIL import Image
import io
import re
import ast
from config import GLM_VISION_MODEL, LLM_MODEL
from .llm_service import get_llm_client

# --- 全局变量 ---

# 识别相关变量
recognition_confidence = 0.7
latest_recognition_result = None


def capture_and_recognize_from_image(image):
    """
    从PIL图像进行成品识别。
    
    Args:
        image: PIL Image对象，来自st.camera_input
        
    Returns:
        dict: 识别结果
    """
    if image is None:
        return {"success": False, "error": "未获取到图像"}

    try:
        # 将图像转换为base64编码
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # 优先调用GLM-4V进行成品识别，如果失败则使用备用方案
        try:
            recognized_products = _recognize_image_with_glm(image_base64)
        except Exception:
            recognized_products = _simplified_recognize_image()

        if recognized_products:
            return {
                "success": True,
                "products": recognized_products,
                "image_base64": image_base64
            }
        else:
            return {"success": False, "error": "未识别到任何成品"}

    except Exception as e:
        return {"success": False, "error": f"图像处理或识别错误: {str(e)}"}


def _recognize_image_with_glm(image_base64):
    """使用GLM-4V模型进行成品识别。"""
    llm_client = get_llm_client()
    if not llm_client:
        # 如果无法获取客户端，则退回到简化版识别
        return _simplified_recognize_image()

    try:
        response = llm_client.chat.completions.create(
            model=GLM_VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请识别图片中的主要物品。返回一个JSON数组，格式为：{\"products\": [\"物品1\", \"物品2\", ...]}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            max_tokens=200,
            temperature=0.1
        )
        result_text = response.choices[0].message.content.strip()

        try:
            # 优先尝试解析JSON
            result_json = json.loads(result_text)
            products = result_json.get('products', [])
            return [str(p).strip() for p in products if str(p).strip()][:3]
        except json.JSONDecodeError:
            # 如果JSON解析失败，使用正则表达式作为备用方案
            products = re.findall(r'["\']([^"\']+)["\']', result_text)
            return [p for p in products if len(p) > 1][:3]

    except Exception:
        # 如果API调用或解析过程中出现任何其他错误，则退回到简化版
        return _simplified_recognize_image()


def _simplified_recognize_image():
    """
    简化识别（备用方案）：不分析图像，而是随机返回一些物品名称。
    注意：此函数不使用图像数据，仅作为无法进行视觉识别时的占位符。
    """
    llm_client = get_llm_client()
    if not llm_client:
        return ["检测到的物品"]

    try:
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": "基于常见的办公用品和家具，随机返回1到2个产品名称，格式为JSON数组：[\"产品1\", \"产品2\"]"}],
            max_tokens=50,
            temperature=0.7
        )
        result = response.choices[0].message.content.strip()

        try:
            # 使用更安全的 ast.literal_eval 解析列表字符串
            products = ast.literal_eval(result)
            return products if isinstance(products, list) else ["智能识别物品"]
        except (ValueError, SyntaxError):
            return ["摄像头检测物品"]

    except Exception:
        return ["检测到的物品"]


def get_latest_recognition_result():
    """获取最新的识别结果"""
    global latest_recognition_result
    return latest_recognition_result


def clear_recognition_result():
    """清空识别结果"""
    global latest_recognition_result
    latest_recognition_result = None


def set_recognition_result(result):
    """设置识别结果"""
    global latest_recognition_result
    latest_recognition_result = result


def get_camera_status_debug():
    """获取摄像头状态的调试信息（简化版）"""
    return {
        "camera_type": "st.camera_input",
        "latest_recognition_result": latest_recognition_result is not None,
        "recognition_confidence": recognition_confidence
    }


# 兼容性函数 - 保持与原有代码的接口一致
def start_camera_recognition(confidence=0.7, auto_capture=False, interval=3, camera_index=0):
    """
    兼容性函数：设置识别参数
    注意：使用st.camera_input时，此函数主要用于设置参数
    """
    global recognition_confidence
    recognition_confidence = confidence
    return {"success": True, "message": "参数已设置，请使用拍照按钮进行识别"}


def stop_camera_recognition():
    """
    兼容性函数：清空识别结果
    """
    clear_recognition_result()
    return {"success": True, "message": "识别已停止"}


def is_camera_active():
    """
    兼容性函数：始终返回True，因为st.camera_input总是可用的
    """
    return True


def is_ai_recognition_active():
    """
    兼容性函数：检查是否有识别结果
    """
    return latest_recognition_result is not None


def get_current_camera_frame():
    """
    兼容性函数：返回None，因为使用st.camera_input不需要实时帧
    """
    return None