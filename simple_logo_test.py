#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的LOGO测试
"""

import streamlit as st
import base64
import os

st.set_page_config(page_title="LOGO测试", layout="wide")

st.title("🔍 简单LOGO测试")

# 测试1: 直接显示
st.subheader("测试1: 直接显示LOGO")
logo_path = "imgs/ZICUS LOGO.png"
if os.path.exists(logo_path):
    st.success(f"✅ 文件存在: {logo_path}")
    st.image(logo_path, width=200)
else:
    st.error(f"❌ 文件不存在: {logo_path}")

# 测试2: Base64显示
st.subheader("测试2: Base64显示")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
            st.success(f"✅ Base64编码成功，长度: {len(encoded)}")
            
            # 尝试显示base64图片
            st.markdown(f'<img src="data:image/png;base64,{encoded}" width="200">', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"❌ 失败: {e}")

# 测试3: 水印效果
st.subheader("测试3: 水印效果")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
            
            # 创建水印
            watermark = f'''
            <div style="
                position: fixed;
                top: 20px;
                left: 20px;
                z-index: 9999;
                opacity: 0.3;
                background: rgba(255,255,255,0.1);
                padding: 10px;
                border-radius: 5px;
            ">
                <img src="data:image/png;base64,{encoded}" 
                     alt="LOGO" 
                     style="width: 100px; height: auto;">
            </div>
            '''
            
            st.markdown(watermark, unsafe_allow_html=True)
            st.success("✅ 水印HTML已创建")
            
    except Exception as e:
        st.error(f"❌ 失败: {e}")

# 测试4: 使用st.image的base64
st.subheader("测试4: st.image + base64")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
            
            # 使用st.image显示base64
            st.image(f"data:image/png;base64,{encoded}", width=200)
            st.success("✅ st.image + base64 成功")
            
    except Exception as e:
        st.error(f"❌ 失败: {e}")

# 测试5: 文件信息
st.subheader("测试5: 文件信息")
if os.path.exists(logo_path):
    size = os.path.getsize(logo_path)
    st.info(f"文件大小: {size} 字节")
    
    # 检查文件头
    with open(logo_path, "rb") as f:
        header = f.read(8)
        if header.startswith(b'\x89PNG\r\n\x1a\n'):
            st.success("✅ 有效的PNG文件")
        else:
            st.warning("⚠️ 不是标准PNG文件")
            st.code(header.hex())
