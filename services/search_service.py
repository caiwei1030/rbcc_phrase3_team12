"""
搜索服务模块 - 处理产品分解和零件搜索功能
"""

import streamlit as st
import requests
import json
import os
from config import LLM_MODEL, FASTGPT_API_KEY, FASTGPT_DATASET_ID
from .llm_service import get_llm_client, _generate_fallback_components, _calculate_relevance_reason


def _get_cad_image_path(part_id, source_file):
    """
    根据零件ID和源文件名查找对应的CAD图片路径
    """
    # CAD图片目录路径 - 更新为正确的路径
    cad_images_dir = "cad2png/cad/cad/cad/images"
    
    # 尝试多种可能的图片文件名
    possible_names = [
        f"{part_id}.png",
        f"{source_file.replace('.json', '.png')}",
        f"{part_id.lower()}.png",
        f"{source_file.replace('.json', '').lower()}.png"
    ]
    
    # 检查文件是否存在
    for img_name in possible_names:
        img_path = os.path.join(cad_images_dir, img_name)
        if os.path.exists(img_path):
            return img_path
    
    return None


def _load_cad_image_as_base64(image_path):
    """
    将CAD图片加载为base64编码，用于在Streamlit中显示
    """
    try:
        import base64
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            return img_base64
    except Exception as e:
        st.warning(f"无法加载CAD图片 {image_path}: {e}")
        return None


def _enhance_part_with_cad_image(part_data):
    """
    为零件数据添加CAD图片信息
    """
    part_id = part_data.get('part_number', part_data.get('id', ''))
    source_file = part_data.get('source_file', '')
    
    # 查找对应的CAD图片
    cad_image_path = _get_cad_image_path(part_id, source_file)
    
    if cad_image_path:
        # 加载图片为base64
        cad_image_base64 = _load_cad_image_as_base64(cad_image_path)
        if cad_image_base64:
            part_data['cad_image'] = cad_image_base64
            part_data['cad_image_path'] = cad_image_path
            part_data['has_cad_image'] = True
        else:
            part_data['has_cad_image'] = False
    else:
        part_data['has_cad_image'] = False
    
    return part_data


def find_parts_for_product(product_description: str):
    """
    增强的产品分解功能：
    第一步：LLM智能分解产品为零件清单。
    第二步：对每个零件进行多轮搜索和优化。
    第三步：基于搜索结果进一步优化组件列表。
    """
    llm_client = get_llm_client()
    if not llm_client:
        st.error("LLM服务不可用，无法分解产品。")
        return {}, [{"content": "LLM服务不可用"}]

    # --- Step 1: Enhanced Product Decomposition ---
    st.info(f"🔍 正在智能分析产品: {product_description}...")
    
    # 更详细和智能的分解提示
    decomposition_prompt = (
        "你是一个资深的制造工程师、产品设计师和供应链专家。\n"
        f"请将以下成品进行专业的零件分解: '{product_description}'\n\n"
        "分解原则:\n"
        "1. 按照制造和装配的逻辑层次分解\n"
        "2. 识别核心功能组件、结构组件和连接组件\n"
        "3. 考虑材料类型、加工工艺和装配方式\n"
        "4. 优先列出可采购的标准件和定制件\n"
        "5. 忽略过于通用的标准件（如普通螺丝），除非有特殊规格要求\n"
        "6. 使用准确的工业术语和规范名称\n"
        "7. 考虑产品的主要功能和使用场景\n\n"
        "输出要求:\n"
        "- 严格使用JSON格式: {\"components\": [\"组件1\", \"组件2\", ...]}\n"
        "- 组件名称要具体明确，便于搜索\n"
        "- 按重要性排序，核心组件在前\n"
        "- 控制在5-15个关键组件\n"
        "- 使用简体中文"
    )

    response_text = ""
    component_list = []
    
    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": decomposition_prompt}
            ],
            max_tokens=1500,  # 增加token限制
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        response_text = resp.choices[0].message.content.strip()
        response_json = json.loads(response_text)
        
        # 改进的JSON解析逻辑
        if isinstance(response_json, dict):
            # 查找包含组件列表的键
            possible_keys = ['components', 'parts', 'items', 'list', '组件', '零件']
            for key in possible_keys:
                if key in response_json and isinstance(response_json[key], list):
                    component_list = response_json[key]
                    break
            
            # 如果没找到，尝试取第一个列表值
            if not component_list:
                for value in response_json.values():
                    if isinstance(value, list) and value:
                        component_list = value
                        break
        elif isinstance(response_json, list):
            component_list = response_json
        
        # 验证和清理组件列表
        if component_list:
            component_list = [str(item).strip() for item in component_list if str(item).strip()]
            component_list = list(dict.fromkeys(component_list))  # 去重保持顺序
        
        if not component_list:
            raise ValueError("未能从AI返回的JSON中提取出有效的组件列表")

    except (json.JSONDecodeError, ValueError) as e:
        st.error(f"🚫 AI分解产品失败: {e}")
        st.error(f"返回内容: {response_text}")
        
        # Fallback: 尝试基于产品描述生成基础组件列表
        fallback_components = _generate_fallback_components(product_description)
        if fallback_components:
            st.warning(f"🔄 使用备用分解方案，识别出 {len(fallback_components)} 个基础组件")
            component_list = fallback_components
        else:
            return {}, [{"content": "AI分解产品失败", "error": f"{e} | 返回内容: {response_text}"}]
            
    except Exception as e:
        st.error(f"🚫 调用LLM时发生未知错误: {e}")
        return {}, [{"content": "调用LLM失败", "error": str(e)}]

    st.success(f"✅ 产品分解完成，识别出 {len(component_list)} 个核心组件: {', '.join(component_list)}")

    # --- Step 2: Enhanced Multi-round Search for Components ---
    final_results = {}
    errors = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, component in enumerate(component_list):
        status_text.text(f"🔍 正在为组件 '{component}' 搜索匹配的零件... ({i+1}/{len(component_list)})")
        
        try:
            # 增强搜索策略，使用多个搜索尝试提高召回率
            all_parts = []
            search_attempts = [
                (component, 0.2),  # 降低相似度阈值
                (component, 0.3),  # 中等相似度阈值
                (f"{component} 零件", 0.2),  # 添加"零件"关键词
                (f"{component} 配件", 0.2),  # 添加"配件"关键词
            ]
            
            seen_part_numbers = set()  # 去重用
            
            for search_query, similarity in search_attempts:
                try:
                    parts, search_errors = search_fastgpt_kb(search_query, similarity=similarity)
                    if search_errors:
                        errors.extend(search_errors)
                    if parts:
                        # 去重合并结果，基于part_number
                        for part in parts:
                            part_number = part.get('part_number', '')
                            if part_number not in seen_part_numbers:
                                seen_part_numbers.add(part_number)
                                all_parts.append(part)
                except Exception as e:
                    continue
            
            # 按分数排序，保留更相关的结果
            if all_parts:
                all_parts.sort(key=lambda x: x.get('score', 0), reverse=True)
                final_results[component] = all_parts
                
        except Exception as e:
            errors.append({"content": f"搜索组件 '{component}' 时出错", "error": str(e)})
            
        progress_bar.progress((i + 1) / len(component_list))

    progress_bar.empty()
    status_text.empty()
    
    # --- Step 3: Results Summary and Optimization ---
    total_parts_found = sum(len(parts) for parts in final_results.values())
    
    if final_results:
        st.info(f"🎯 搜索完成！为 {len(final_results)} 个组件找到了 {total_parts_found} 个相关零件")
        
        # 显示搜索统计
        with st.expander("📊 搜索结果统计", expanded=False):
            for component, parts in final_results.items():
                st.write(f"• **{component}**: {len(parts)} 个零件")
    
    return final_results, errors


def search_fastgpt_kb(query: str, similarity: float = 0.5):
    """
    调用FastGPT知识库进行搜索，并按向量相似度排序。
    增强的RAG搜索功能，支持多轮查询和结果优化。
    """
    # 检查配置是否完整
    if not FASTGPT_API_KEY:
        error_msg = "FastGPT API密钥未配置。请在Streamlit Cloud的环境变量中设置FASTGPT_API_KEY，或在本地创建.streamlit/secrets.toml文件。"
        st.error(error_msg)
        return [], [{"content": "配置错误", "error": error_msg}]
    
    if not FASTGPT_DATASET_ID:
        error_msg = "FastGPT数据集ID未配置。请在Streamlit Cloud的环境变量中设置FASTGPT_DATASET_ID，或在本地创建.streamlit/secrets.toml文件。"
        st.error(error_msg)
        return [], [{"content": "配置错误", "error": error_msg}]

    # 直接使用原始查询，不做任何预处理
    search_url = "https://cloud.fastgpt.cn/api/core/dataset/searchTest"
    headers = {
        "Authorization": f"Bearer {FASTGPT_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 使用增强的搜索参数，提高召回率
    data = {
        "datasetId": FASTGPT_DATASET_ID,
        "text": query,
        "limit": 100,  # 大幅增加搜索结果数量限制
        "similarity": max(0.1, similarity - 0.2),  # 降低相似度阈值提高召回率
        "searchMode": "mixedRecall",
        "usingReRank": True,
        "datasetSearchUsingExtensionQuery": True,  # 开启查询扩展以提高匹配
        "datasetSearchExtensionModel": "",
        "datasetSearchExtensionBg": ""
    }

    try:
        response = requests.post(search_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            st.error(f"FastGPT API响应不是有效的JSON格式: {response.text}")
            return [], [{"content": "API响应格式错误", "error": response.text}]

        if not isinstance(response_data, dict):
            error_msg = str(response_data)
            st.error(f"FastGPT API返回了非预期的格式: {error_msg}")
            return [], [{"content": "API返回格式错误", "error": error_msg}]

        if response_data.get("code") == 200:
            data_payload = response_data.get("data", {})
            search_results = data_payload.get("list", [])

            if not search_results:
                return [], []

            processed_results = []
            for result in search_results:
                try:
                    # 改进的分数处理逻辑
                    score_list = result.get('score', [])
                    final_score = 0.0
                    rerank_score = 0.0
                    
                    if isinstance(score_list, list):
                        for score_item in score_list:
                            score_type = score_item.get('type', '')
                            score_value = score_item.get('value', 0.0)
                            
                            if score_type == 'embedding':
                                final_score = score_value
                            elif score_type == 'rerank':
                                rerank_score = score_value
                    elif isinstance(score_list, (int, float)):
                        final_score = score_list
                    
                    # 综合评分：优先使用rerank分数，fallback到embedding分数
                    combined_score = rerank_score if rerank_score > 0 else final_score

                    q_content = result.get('q', '').strip()
                    if not q_content:
                        continue
                    
                    json_start_index = q_content.find('{')
                    if json_start_index == -1:
                        continue
                    json_string = q_content[json_start_index:]
                    part_data = json.loads(json_string)

                    # 增强数据提取和清理
                    normalized_part = {
                        'part_number': str(part_data.get('part_number', part_data.get('id', 'N/A'))),
                        'part_name': str(part_data.get('part_name', part_data.get('source_file', 'N/A'))),
                        'description': str(part_data.get('description', '无描述')),
                        'operator': str(part_data.get('operator', '系统')),
                        'created_time': str(part_data.get('created_time', '未知')),
                        'image': part_data.get('image'),
                        'source_file': str(part_data.get('source_file', '')),
                        'keywords': str(part_data.get('keywords', '')),
                        'score': combined_score,
                        'embedding_score': final_score,
                        'rerank_score': rerank_score,
                        'original_score': final_score,
                        'llm_analyzed': False,
                        'relevance_reason': _calculate_relevance_reason(query, part_data)
                    }
                    
                    # 增强零件数据，添加CAD图片信息
                    normalized_part = _enhance_part_with_cad_image(normalized_part)
                    
                    # 保留所有结果，让FastGPT的相似度阈值起作用
                    processed_results.append(normalized_part)
                        
                except (json.JSONDecodeError, TypeError) as e:
                    st.warning(f"跳过一个无法解析的结果: {e}")
                    continue
            
            # 简单排序：按综合分数降序
            processed_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return processed_results, []
        else:
            error_msg = response_data.get('message', '未知API错误')
            st.error(f"FastGPT API 错误: {error_msg}")
            return [], [{"content": "API返回错误", "error": error_msg}]

    except requests.exceptions.RequestException as e:
        st.error(f"请求FastGPT失败: {e}")
        return [], [{"content": "请求失败", "error": str(e)}]
    except Exception as e:
        st.error(f"处理FastGPT结果时发生未知错误: {e}")
        return [], [{"content": "处理过程中发生未知错误", "error": str(e)}]