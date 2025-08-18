#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试LOGO显示问题
"""

import streamlit as st
import base64
import os

# 设置页面配置
st.set_page_config(
    page_title="Logo Debug",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 LOGO显示调试")

# 测试1: 直接显示图片
st.subheader("测试1: 直接显示图片")
logo_path = "imgs/ZICUS LOGO.png"
if os.path.exists(logo_path):
    st.success(f"✅ LOGO文件存在: {logo_path}")
    try:
        st.image(logo_path, caption="直接显示的LOGO", width=200)
        st.success("✅ 直接显示成功")
    except Exception as e:
        st.error(f"❌ 直接显示失败: {e}")
else:
    st.error(f"❌ LOGO文件不存在: {logo_path}")

# 测试2: Base64编码
st.subheader("测试2: Base64编码测试")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as image_file:
            image_data = image_file.read()
            encoded_string = base64.b64encode(image_data).decode()
            st.success(f"✅ Base64编码成功，长度: {len(encoded_string)} 字符")
            st.info(f"前100个字符: {encoded_string[:100]}...")
    except Exception as e:
        st.error(f"❌ Base64编码失败: {e}")

# 测试3: HTML水印测试
st.subheader("测试3: HTML水印测试")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as image_file:
            image_data = image_file.read()
            encoded_string = base64.b64encode(image_data).decode()
            
            # 测试不同的HTML格式
            html_formats = [
                # 格式1: 标准data URI
                f'<div style="position: fixed; top: 15px; left: 15px; z-index: 1000; opacity: 0.5;"><img src="data:image/png;base64,{encoded_string}" alt="LOGO" style="width: 100px; height: auto;"></div>',
                
                # 格式2: 简化版本
                f'<img src="data:image/png;base64,{encoded_string}" alt="LOGO" style="position: fixed; top: 15px; left: 15px; z-index: 1000; opacity: 0.5; width: 100px; height: auto;">',
                
                # 格式3: 使用CSS类
                f'<div class="watermark"><img src="data:image/png;base64,{encoded_string}" alt="LOGO"></div>'
            ]
            
            for i, html in enumerate(html_formats, 1):
                st.markdown(f"**格式 {i}:**")
                st.code(html[:100] + "..." if len(html) > 100 else html)
                st.markdown(html, unsafe_allow_html=True)
                st.divider()
                
    except Exception as e:
        st.error(f"❌ HTML水印测试失败: {e}")

# 测试4: CSS样式测试
st.subheader("测试4: CSS样式测试")
css_test = """
<style>
.watermark {
    position: fixed !important;
    top: 15px !important;
    left: 15px !important;
    z-index: 9999 !important;
    opacity: 0.7 !important;
    background-color: rgba(255,255,255,0.1) !important;
    padding: 10px !important;
    border-radius: 5px !important;
}
.watermark img {
    width: 100px !important;
    height: auto !important;
    display: block !important;
}
</style>
"""
st.markdown(css_test, unsafe_allow_html=True)

# 测试5: 环境信息
st.subheader("测试5: 环境信息")
st.info(f"当前工作目录: {os.getcwd()}")
st.info(f"LOGO文件绝对路径: {os.path.abspath(logo_path)}")
st.info(f"Streamlit版本: {st.__version__}")

# 测试6: 文件信息
st.subheader("测试6: 文件信息")
if os.path.exists(logo_path):
    file_stat = os.stat(logo_path)
    st.info(f"文件大小: {file_stat.st_size} 字节")
    st.info(f"文件权限: {oct(file_stat.st_mode)}")
    
    # 检查文件头
    try:
        with open(logo_path, "rb") as f:
            header = f.read(8)
            st.info(f"文件头: {header.hex()}")
            if header.startswith(b'\x89PNG\r\n\x1a\n'):
                st.success("✅ 确认是有效的PNG文件")
            else:
                st.warning("⚠️ 文件头不是标准PNG格式")
    except Exception as e:
        st.error(f"❌ 读取文件头失败: {e}")
