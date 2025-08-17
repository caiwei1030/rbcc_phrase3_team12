"""
LLM服务模块 - 处理LLM客户端初始化和通用分析功能
"""

import streamlit as st
import httpx
from openai import OpenAI
import json
from config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

# --- LLM Client Initialization ---
try:
    llm_client = OpenAI(
        base_url=LLM_BASE_URL,
        api_key=LLM_API_KEY,
        http_client=httpx.Client(trust_env=False, timeout=httpx.Timeout(20.0, read=180.0))
    )
except Exception as e:
    st.error(f"LLM客户端初始化失败: {e}")
    llm_client = None


def get_llm_client():
    """获取LLM客户端实例"""
    return llm_client


def analyze_json_with_llm(json_content: str, user_question: str) -> str:
    """
    使用LLM分析JSON数据并回答用户问题（通用版）。
    """
    if not llm_client:
        return "LLM服务不可用"

    system_prompt = (
        "你是一个通用的JSON数据分析助手。\n"
        "请仔细阅读用户提供的JSON数据和问题，并根据你的理解提取关键信息或回答问题。\n"
        "如果用户在寻找特定的零件或物品，请根据数据判断相关性。"
    )

    user_prompt = f"用户问题：{user_question}\n\nJSON数据：\n{json_content}"

    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=8000,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f'{{"error": "LLM分析失败: {str(e)}"}}'


def _generate_fallback_components(product_description: str) -> list:
    """
    当AI分解失败时，仅返回最基础的通用组件
    """
    return ["主要部件", "辅助部件", "连接件"]


def _calculate_relevance_reason(query: str, part_data: dict) -> str:
    """
    计算零件与查询的相关性原因
    """
    reasons = []
    query_lower = query.lower()
    
    part_name = str(part_data.get('part_name', '')).lower()
    description = str(part_data.get('description', '')).lower()
    keywords = str(part_data.get('keywords', '')).lower()
    
    # 检查名称匹配
    if any(word in part_name for word in query_lower.split()):
        reasons.append("名称匹配")
    
    # 检查描述匹配
    if any(word in description for word in query_lower.split()):
        reasons.append("描述匹配")
    
    # 检查关键词匹配
    if any(word in keywords for word in query_lower.split()):
        reasons.append("关键词匹配")
    
    return "、".join(reasons) if reasons else "语义相似"


def _enhance_search_query(query: str) -> str:
    """
    直接返回原始查询，不做任何增强处理
    """
    return query.strip()