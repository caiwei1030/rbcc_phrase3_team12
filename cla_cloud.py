import base64
import json
from openai import OpenAI
import httpx
import os
import time

# 配置
BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = os.getenv("SILICONFLOW_API_KEY", "sk-gbrvxyqodxyaqanixmembtvfxypgtcvtdmfjluxivnyqdzsd")
MODEL = "zai-org/GLM-4.5V"  # 支持图片识别的模型

# 检查API密钥是否设置
if not API_KEY or API_KEY == "sk-gbrvxyqodxyaqanixmembtvfxypgtcvtdmfjluxivnyqdzsd":
    print("警告: 请设置 SILICONFLOW_API_KEY 环境变量")

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    http_client=httpx.Client(trust_env=False, timeout=60.0)
)

def classify_part_from_b64(image_b64, options):
    """
    使用多模态模型对Base64编码的图片进行分类。

    :param image_b64: Base64编码的图片字符串。
    :param options: 备选的零件类别列表。
    :return: 模型的识别结果字符串。
    """
    # 1. 准备API请求的 messages
    system_prompt = "你是一个工业零件识别助手，请根据图片，从给定的零件类型中选择最接近的一类，并只返回类别名称。"
    user_message = f"备选零件类别：\n{json.dumps(options, ensure_ascii=False)}"

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                        }
                    ]
                }
            ],
            max_tokens=200,
            temperature=0.0
        )
        return resp.choices[0].message.content
    except Exception as e:
        # 增加异常捕获，方便调试
        return f"API调用失败: {e}"

def classify_part_from_file(image_file, options):
    """
    从文件对象识别零件（Streamlit兼容版本）
    
    :param image_file: Streamlit上传的文件对象
    :param options: 备选的零件类别列表
    :return: 识别结果
    """
    try:
        # 将文件转换为base64
        image_bytes = image_file.getvalue()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # 调用识别API
        return classify_part_from_b64(image_b64, options)
    except Exception as e:
        return f"文件处理失败: {e}"

# 兼容性函数
def frame_to_base64(frame):
    """兼容性函数，在云环境中不可用"""
    return None

def capture_and_classify(options):
    """兼容性函数，在云环境中不可用"""
    return "此功能在云环境中不可用，请使用拍照识别功能。"
