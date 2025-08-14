import base64
import json
from openai import OpenAI
import httpx
import os
import cv2  # 引入OpenCV库
import time  # 引入time库用于延时

# 配置
BASE_URL = "https://api.siliconflow.cn/v1"
API_KEY = os.getenv("SILICONFLOW_API_KEY", "sk-gbrvxyqodxyaqanixmembtvfxypgtcvtdmfjluxivnyqdzsd")  # 从环境变量获取API密钥
MODEL = "zai-org/GLM-4.5V"  # 支持图片识别的模型

# 检查API密钥是否设置
if not API_KEY or API_KEY == "sk-gbrvxyqodxyaqanixmembtvfxypgtcvtdmfjluxivnyqdzsd":
    print("警告: 请设置 SILICONFLOW_API_KEY 环境变量")

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    http_client=httpx.Client(trust_env=False, timeout=60.0)
)


def frame_to_base64(frame):
    """将OpenCV捕获的帧（NumPy数组）转换为Base64编码的字符串"""
    # 1. 将图像帧编码为JPEG格式的字节流
    # imencode返回两个值，第一个是bool表示是否成功，第二个是编码后的数据
    success, buffer = cv2.imencode(".jpg", frame)
    if not success:
        return None

    # 2. 将字节流进行Base64编码
    return base64.b64encode(buffer).decode("utf-8")


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


def capture_and_classify(options):
    """
    从摄像头捕获图像并进行分类。
    """
    # 1. 打开默认摄像头 (通常索引为0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return "错误：无法打开摄像头。请检查摄像头是否连接并被系统识别。"

    print("摄像头已启动。请在预览窗口中对准零件...")
    print("窗口将在3秒后自动关闭并捕获图像，或按 'q' 键立即捕获。")

    start_time = time.time()
    frame_to_classify = None

    while True:
        # 2. 读取一帧图像
        ret, frame = cap.read()
        if not ret:
            print("错误：无法从摄像头读取帧。")
            break

        # 3. 显示预览窗口
        # 在图像上添加提示文字
        elapsed_time = time.time() - start_time
        countdown = 3 - int(elapsed_time)
        display_text = f"Capture in {countdown}s or press 'q'"
        cv2.putText(frame, display_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow('Camera Preview - Press "q" to capture', frame)

        # 4. 等待按键或超时
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or elapsed_time > 3:
            frame_to_classify = frame  # 保存当前帧用于识别
            break

    # 5. 释放摄像头资源并关闭所有OpenCV窗口
    cap.release()
    cv2.destroyAllWindows()

    if frame_to_classify is None:
        return "未能成功捕获图像。"

    print("\n图像已捕获，正在进行Base64编码...")
    # 6. 将捕获的帧转换为Base64
    image_b64 = frame_to_base64(frame_to_classify)
    if image_b64 is None:
        return "错误：图像编码失败。"

    print("编码完成，正在发送至API进行识别...")
    # 7. 调用API进行分类
    result = classify_part_from_b64(image_b64, options)
    return result