"""
诊断服务模块 - 处理模型配置检测和修复功能
"""

import base64
from PIL import Image
import io
from config import LLM_MODEL, GLM_VISION_MODEL
from .llm_service import get_llm_client


def diagnose_model_config():
    """诊断模型配置并测试连接"""
    llm_client = get_llm_client()
    
    # 检查客户端初始化
    if not llm_client:
        return False
    
    # 测试文本模型连接
    try:
        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": "请说'连接测试成功'"}],
            max_tokens=50,
            temperature=0.1
        )
        result = response.choices[0].message.content.strip()
    except Exception as e:
        pass
    
    # 测试视觉模型连接（简单测试）
    try:
        # 创建一个小的测试图像（1x1像素的白色图像）
        test_img = Image.new('RGB', (1, 1), color='white')
        buffer = io.BytesIO()
        test_img.save(buffer, format='JPEG')
        test_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        response = llm_client.chat.completions.create(
            model=GLM_VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "这是什么颜色？请只回答颜色名称。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{test_base64}"}}
                ]
            }],
            max_tokens=20,
            temperature=0.1
        )
        result = response.choices[0].message.content.strip()
        return True
    except Exception as e:
        return False


def test_alternative_vision_models():
    """测试备选的视觉模型"""
    llm_client = get_llm_client()
    if not llm_client:
        return None
        
    alternative_models = [
        "OpenGVLab/InternVL2-8B",
        "OpenGVLab/InternVL2-4B", 
        "stepfun-ai/GOT-OCR2_0",
        "Qwen/Qwen2-VL-72B-Instruct",
        "Qwen/Qwen2-VL-7B-Instruct"
    ]
    
    # 创建测试图像
    test_img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    test_img.save(buffer, format='JPEG')
    test_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    for model in alternative_models:
        try:
            response = llm_client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "这是什么颜色？"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{test_base64}"}}
                    ]
                }],
                max_tokens=20,
                temperature=0.1
            )
            result = response.choices[0].message.content.strip()
            return model
        except Exception as e:
            continue
    
    return None


def auto_fix_vision_model():
    """自动修复视觉模型配置"""
    working_model = test_alternative_vision_models()
    if working_model:
        try:
            # 读取当前配置文件
            config_path = "/home/jxr/rbcc_phrase3_team12/config.py"
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换GLM_VISION_MODEL配置
            import re
            
            # 查找并替换GLM_VISION_MODEL的赋值
            pattern = r'GLM_VISION_MODEL\s*=\s*["\'][^"\']+["\']'
            replacement = f'GLM_VISION_MODEL = "{working_model}"'
            
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                
                # 备份原文件
                import shutil
                shutil.copy(config_path, f"{config_path}.backup")
                
                # 写入新配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
            else:
                return False
                
        except Exception as e:
            return False
    else:
        return False