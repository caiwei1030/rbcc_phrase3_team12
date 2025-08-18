#!/usr/bin/env python3
"""
FastGPT配置检查工具
用于诊断Streamlit应用中的FastGPT配置问题
"""

import os
import streamlit as st
import requests
import json

def check_fastgpt_config():
    """检查FastGPT配置状态"""
    st.title("🔧 FastGPT配置检查工具")
    st.markdown("---")
    
    # 检查环境变量
    st.subheader("📋 环境变量检查")
    
    fastgpt_api_key = os.environ.get("FASTGPT_API_KEY")
    fastgpt_dataset_id = os.environ.get("FASTGPT_DATASET_ID")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if fastgpt_api_key:
            st.success("✅ FASTGPT_API_KEY 已设置")
            st.code(fastgpt_api_key[:20] + "..." if len(fastgpt_api_key) > 20 else fastgpt_api_key)
        else:
            st.error("❌ FASTGPT_API_KEY 未设置")
            st.info("请在环境变量中设置FASTGPT_API_KEY")
    
    with col2:
        if fastgpt_dataset_id:
            st.success("✅ FASTGPT_DATASET_ID 已设置")
            st.code(fastgpt_dataset_id)
        else:
            st.error("❌ FASTGPT_DATASET_ID 未设置")
            st.info("请在环境变量中设置FASTGPT_DATASET_ID")
    
    # 检查Streamlit secrets
    st.subheader("🔐 Streamlit Secrets检查")
    
    try:
        secrets_api_key = st.secrets.get("FASTGPT_API_KEY", "")
        secrets_dataset_id = st.secrets.get("FASTGPT_DATASET_ID", "")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if secrets_api_key:
                st.success("✅ secrets.toml中的FASTGPT_API_KEY已设置")
                st.code(secrets_api_key[:20] + "..." if len(secrets_api_key) > 20 else secrets_api_key)
            else:
                st.warning("⚠️ secrets.toml中未找到FASTGPT_API_KEY")
        
        with col2:
            if secrets_dataset_id:
                st.success("✅ secrets.toml中的FASTGPT_DATASET_ID已设置")
                st.code(secrets_dataset_id)
            else:
                st.warning("⚠️ secrets.toml中未找到FASTGPT_DATASET_ID")
                
    except Exception as e:
        st.error(f"❌ 读取secrets失败: {e}")
    
    # 最终配置状态
    st.subheader("🎯 最终配置状态")
    
    final_api_key = fastgpt_api_key or secrets_api_key
    final_dataset_id = fastgpt_dataset_id or secrets_dataset_id
    
    if final_api_key and final_dataset_id:
        st.success("🎉 FastGPT配置完整！")
        
        # 测试API连接
        if st.button("🧪 测试FastGPT API连接"):
            test_fastgpt_connection(final_api_key, final_dataset_id)
    else:
        st.error("❌ FastGPT配置不完整")
        
        if not final_api_key:
            st.error("缺少FASTGPT_API_KEY")
        if not final_dataset_id:
            st.error("缺少FASTGPT_DATASET_ID")
        
        st.info("💡 解决方案：")
        st.markdown("""
        1. **Streamlit Cloud部署：** 在应用设置中添加环境变量
        2. **本地开发：** 创建 `.streamlit/secrets.toml` 文件
        3. **检查拼写：** 确保环境变量名称完全正确
        """)
    
    # 配置建议
    st.subheader("💡 配置建议")
    st.markdown("""
    ### 推荐配置方式（Streamlit Cloud）
    ```
    FASTGPT_API_KEY=your_api_key_here
    FASTGPT_DATASET_ID=your_dataset_id_here
    ```
    
    ### 本地开发配置
    创建 `.streamlit/secrets.toml` 文件：
    ```toml
    FASTGPT_API_KEY = "your_api_key_here"
    FASTGPT_DATASET_ID = "your_dataset_id_here"
    ```
    
    ### 环境变量优先级
    1. 环境变量（最高优先级）
    2. Streamlit secrets
    3. 默认值（最低优先级）
    """)

def test_fastgpt_connection(api_key, dataset_id):
    """测试FastGPT API连接"""
    st.subheader("🧪 API连接测试")
    
    try:
        url = "https://cloud.fastgpt.cn/api/core/dataset/searchTest"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "datasetId": dataset_id,
            "text": "test",
            "limit": 1,
            "similarity": 0.5
        }
        
        with st.spinner("正在测试API连接..."):
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
        if response.status_code == 200:
            st.success("✅ API连接成功！")
            try:
                response_data = response.json()
                if response_data.get("code") == 200:
                    st.success("✅ API响应正常")
                    st.json(response_data)
                else:
                    st.warning(f"⚠️ API返回错误代码: {response_data.get('code')}")
                    st.json(response_data)
            except json.JSONDecodeError:
                st.warning("⚠️ API响应不是有效的JSON格式")
                st.text(response.text)
        else:
            st.error(f"❌ API连接失败，状态码: {response.status_code}")
            st.text(response.text)
            
    except requests.exceptions.Timeout:
        st.error("❌ API请求超时")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API请求失败: {e}")
    except Exception as e:
        st.error(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    check_fastgpt_config()
