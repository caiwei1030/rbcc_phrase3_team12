import streamlit as st
import pandas as pd
import base64
import time
from services import (
    find_parts_for_product,
    search_fastgpt_kb,
    start_camera_recognition,
    stop_camera_recognition,
    get_current_camera_frame,
    is_camera_active,
    is_ai_recognition_active,
    get_latest_recognition_result,
    clear_recognition_result,
    diagnose_model_config,
    test_alternative_vision_models,
    auto_fix_vision_model,
    get_camera_status_debug
)
import database
from utils import show_info_message, show_error_message, show_success_message, show_warning_message

def show_parts_query():
    """显示零件查询界面，集成成品分解与智能搜索"""
    st.subheader("🤖 智能零件查找")
    show_info_message("您可以选择分解成品来查找零件、进行智能语义搜索，或使用摄像头识别成品并自动分解。")

    search_mode = st.radio(
        "选择搜索模式:",
        ("分解成品 (AI)", "智能语义搜索", "摄像头识别+分解 (AI)"),
        key="search_mode_radio",
        horizontal=True
    )

    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)

        search_query_label = "" # Placeholder for label
        search_query_placeholder = "" # Placeholder for placeholder
        search_button_label = "" # Placeholder for button label

        if search_mode == "分解成品 (AI)":
            search_query_label = "💬 请输入成品名称"
            search_query_placeholder = "例如：一个带抽屉的木制书桌"
            search_button_label = "🤖 AI智能分解并查找零件"
        elif search_mode == "智能语义搜索":
            search_query_label = "💬 请输入您的需求"
            search_query_placeholder = "例如：一个用于固定的六边形法兰"
            search_button_label = "🧠 AI智能搜索"
        else: # 摄像头识别+分解 (AI)
            search_query_label = "📹 摄像头成品识别与分解"
            search_query_placeholder = ""
            search_button_label = "📸 识别成品并分解"

        # 根据模式显示不同的输入界面
        search_query = ""
        if search_mode == "摄像头识别+分解 (AI)":
            # 摄像头识别模式的特殊UI - 使用st.camera_input
            st.markdown("### 📹 AI智能摄像头 - 拍照识别与分解")
            
            # 创建居中的摄像头区域
            camera_col1, camera_col2, camera_col3 = st.columns([1, 3, 1])
            with camera_col2:
                # 使用st.camera_input进行拍照
                st.markdown("#### 📸 拍照识别")
                st.info("请点击下方按钮拍照，AI将自动识别照片中的成品")
                
                # 摄像头输入组件
                camera_photo = st.camera_input(
                    "📷 点击拍照进行AI识别",
                    key="camera_input",
                    help="点击拍照按钮，AI将自动识别照片中的成品"
                )
                
                # 如果拍照了，进行识别
                if camera_photo is not None:
                    with st.spinner("🤖 AI正在识别照片中的成品..."):
                        # 导入新的识别函数
                        from services.camera_service import capture_and_recognize_from_image, set_recognition_result
                        
                        # 进行识别
                        result = capture_and_recognize_from_image(camera_photo)
                        
                        if result.get('success'):
                            # 保存识别结果
                            set_recognition_result(result)
                            st.success("✅ 识别完成！")
                        else:
                            st.error(f"❌ 识别失败: {result.get('error', '未知错误')}")
            
            # 在摄像头下方显示识别结果
            with camera_col2:
                # 检查并显示最新识别结果
                latest_result = get_latest_recognition_result()
                
                # 系统状态显示
                st.markdown("#### 🔍 识别状态")
                
                if latest_result and latest_result.get('success'):
                    st.success("🤖 AI识别：已完成")
                else:
                    st.info("📷 等待拍照识别...")
                
                if latest_result and latest_result.get('success'):
                    recognized_products = latest_result.get('products', [])
                    if recognized_products:
                        st.markdown(f"""
                        <div class="recognition-result">
                            <h4>🎯 检测到 {len(recognized_products)} 个成品：</h4>
                            <ul>
                        """, unsafe_allow_html=True)
                        
                        for i, product in enumerate(recognized_products, 1):
                            st.markdown(f"<li><strong>{i}. {product}</strong></li>", unsafe_allow_html=True)
                        
                        st.markdown("</ul></div>", unsafe_allow_html=True)
                        
                        # 按钮行
                        btn_col1, btn_col2 = st.columns(2)
                        
                        with btn_col1:
                            decompose_btn = st.button("🤖 自动分解所有成品", key="auto_decompose", use_container_width=True)
                        
                        with btn_col2:
                            clear_btn = st.button("🗑️ 清除结果", key="clear_result", use_container_width=True)
                        
                        # 处理分解按钮
                        if decompose_btn:
                            with st.spinner("🔧 AI正在自动分解成品..."):
                                # 对所有识别到的成品进行分解
                                all_results = {}
                                all_errors = []
                                
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for i, product in enumerate(recognized_products):
                                    status_text.text(f"🔧 正在分解: {product} ({i+1}/{len(recognized_products)})")
                                    progress_bar.progress(i / len(recognized_products))
                                    
                                    try:
                                        results, errors = find_parts_for_product(product)
                                        
                                        if errors:
                                            all_errors.extend(errors)
                                        
                                        if results:
                                            for component, parts in results.items():
                                                component_key = f"{product} → {component}"
                                                all_results[component_key] = parts
                                    except Exception as e:
                                        all_errors.append({"content": product, "error": str(e)})
                                
                                progress_bar.progress(1.0)
                                status_text.text("✅ 分解完成！")
                                progress_bar.empty()
                                status_text.empty()
                                
                                # 显示分解结果
                                if all_results:
                                    total_parts = sum(len(parts) for parts in all_results.values())
                                    show_success_message(f"🎉 找到 {total_parts} 个相关零件！")
                                    
                                    for component_key, parts in all_results.items():
                                        st.markdown(f"### 🔍 {component_key}")
                                        if parts:
                                            _display_search_results(parts)
                                        else:
                                            show_warning_message("未找到该组件的匹配零件")
                                        st.markdown("<hr>", unsafe_allow_html=True)
                                
                                # 清空识别结果
                                clear_recognition_result()
                        
                        # 处理清除按钮
                        if clear_btn:
                            clear_recognition_result()
                            st.success("🗑️ 识别结果已清除")
                            st.rerun()
                    else:
                        st.warning("⚠️ 未识别到任何成品")
                else:
                    st.info("📷 请拍照进行AI识别")
                    
                    # 添加使用说明
                    with st.expander("❓ 使用说明", expanded=True):
                        st.markdown("""
                        **📋 使用步骤：**
                        
                        1. 点击上方的 **"📷 点击拍照进行AI识别"** 按钮
                        2. 允许浏览器访问摄像头权限
                        3. 对准要识别的成品，点击拍照
                        4. AI将自动识别照片中的成品
                        5. 点击"🤖 自动分解所有成品"进行零件分解
                        
                        **💡 使用建议：**
                        
                        - 💡 光线充足的环境效果更佳
                        - 📐 将成品完整放置在画面中心
                        - 🚫 避免遮挡，确保产品轮廓清晰
                        - 📱 拍照后等待AI识别完成再进行下一步
                        """)
                        
                        # 检查AI模型状态
                        st.markdown("**🔍 AI模型状态：**")
                        try:
                            from services.llm_service import llm_client
                            if llm_client:
                                st.success("✅ AI模型客户端已初始化")
                            else:
                                st.error("❌ AI模型客户端未初始化")
                        except Exception as e:
                            st.error(f"❌ AI模型检查失败: {e}")
            
            # 设置区域
            st.markdown("---")
            st.markdown("#### ⚙️ AI识别设置")
            
            col1, col2 = st.columns(2)
            with col1:
                recognition_confidence = st.slider(
                    "🎯 识别置信度", 
                    0.1, 1.0, 0.7, 0.05,
                    help="设置AI识别的置信度阈值，值越高识别越严格"
                )
            
            with col2:
                # 调试按钮
                debug_btn = st.button("🐛 调试状态", key="debug_btn")
                
                # 模拟测试按钮
                col_sim1, col_sim2 = st.columns(2)
                with col_sim1:
                    simulate_btn = st.button("🎭 模拟识别", key="simulate_btn")
                with col_sim2:
                    clear_sim_btn = st.button("🧹 清空模拟", key="clear_sim_btn")
        else:
            # 原有的文本输入模式
            search_query = st.text_input(search_query_label, placeholder=search_query_placeholder,
                                         key="search_input")
        
        # 只有在智能语义搜索模式下显示相似度滑块
        similarity_threshold = 0.5 # Default value
        if search_mode == "智能语义搜索":
            similarity_threshold = st.slider("🎯 匹配灵敏度 (值越低越模糊)", 0.1, 1.0, 0.5, 0.05)

        # 根据模式显示不同的按钮和处理逻辑
        if search_mode == "摄像头识别+分解 (AI)":
            # 处理按钮操作
            if simulate_btn:
                # 模拟识别结果
                mock_products = ["电脑鼠标", "键盘", "显示器"]
                simulation_result = {
                    "success": True,
                    "products": mock_products,
                    "image_base64": "simulation"
                }
                from services.camera_service import set_recognition_result
                set_recognition_result(simulation_result)
                st.success(f"🎭 模拟识别成功: {', '.join(mock_products)}")
                st.rerun()
            
            elif clear_sim_btn:
                clear_recognition_result()
                st.success("🧹 模拟结果已清空")
                st.rerun()
            
            elif debug_btn:
                st.info("🐛 系统状态调试信息")
                debug_status = get_camera_status_debug()
                st.json(debug_status)
                
                # 显示当前状态和解决方案
                with st.expander("📋 功能状态说明", expanded=True):
                    st.markdown("""
                    **🎯 当前功能状态：**
                    
                    - 📹 **摄像头拍照**：✅ 使用st.camera_input，无需启动
                    - 🤖 **AI识别**：✅ 拍照后自动识别
                    - 🔧 **自动分解**：✅ 正常工作
                    - 🔍 **零件搜索**：✅ 正常工作
                    
                    **💡 使用流程：**
                    
                    1. 点击拍照按钮进行拍照
                    2. AI自动识别照片中的成品
                    3. 点击"自动分解"进行零件分解
                    4. 系统搜索匹配的零件
                    """)
                    
                    # 功能状态说明
                    st.info("💡 使用st.camera_input，无需复杂的摄像头启动流程")
        
        else:
            # 原有的文本搜索按钮
            if st.button(search_button_label, type="primary", key="search_btn", use_container_width=True):
                if search_query:
                    if search_mode == "分解成品 (AI)":
                        with st.spinner("正在分解成品并查找零件，请稍候..."):
                            results, errors = find_parts_for_product(search_query)

                        if errors:
                            for error in errors:
                                show_error_message(f"{error.get('content')}: {error.get('error')}")
                        
                        if results:
                            total_parts_found = sum(len(parts) for parts in results.values())
                            show_success_message(f"分解完成！为 {len(results)} 个组件找到了 {total_parts_found} 个相关零件。")

                            for component, parts in results.items():
                                st.markdown(f"### 搜索组件: **`{component}`**")
                                if not parts:
                                    show_warning_message("未找到该组件的匹配零件。")
                                    continue

                                for i, part in enumerate(parts):
                                    with st.container():
                                        try:
                                            part_number_safe = str(part.get('part_number', 'N/A'))
                                            part_name_safe = str(part.get('part_name', 'N/A'))
                                            description_safe = str(part.get('description', '无描述'))
                                            operator_safe = str(part.get('operator', 'N/A'))
                                            created_time_safe = str(part.get('created_time', 'N/A'))
                                            score_safe = float(part.get('score', 0.0))

                                            # 获取增强的显示信息
                                            relevance_reason = part.get('relevance_reason', '语义相似')
                                            rerank_score = part.get('rerank_score', 0)
                                            embedding_score = part.get('embedding_score', 0)
                                            
                                            # 确定显示的分数和颜色
                                            display_score = rerank_score if rerank_score > 0 else embedding_score
                                            score_color = "#28a745" if display_score > 0.7 else "#ffc107" if display_score > 0.5 else "#6c757d"
                                            
                                            st.markdown(f"""
                                            <div class="report-card fade-in">
                                                <div class="report-header">
                                                    <div class="report-title">🏷️ {part_number_safe} - {part_name_safe}</div>
                                                    <div style="text-align: right;">
                                                        <span style="background-color: {score_color}; color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; margin-right: 5px;">
                                                            相似度: {display_score:.4f}
                                                        </span>
                                                        <span style="background-color: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">
                                                            {relevance_reason}
                                                        </span>
                                                    </div>
                                                </div>
                                                <p><strong>📄 描述:</strong> {description_safe}</p>
                                                <p><strong>👤 操作员:</strong> {operator_safe}</p>
                                                <p><strong>📅 创建时间:</strong> {created_time_safe}</p>
                                            </div>
                                            """, unsafe_allow_html=True)

                                            image_data = part.get('image')
                                            if image_data:
                                                try:
                                                    st.image(f"data:image/jpeg;base64,{image_data}", caption="零件图片",
                                                             use_column_width=True)
                                                except Exception as img_error:
                                                    st.warning(f"图片显示失败: {img_error}")

                                            if i < len(parts) - 1:
                                                st.markdown("---")

                                        except Exception as display_error:
                                            st.error(f"显示零件 '{part.get('part_name')}' 时出错: {display_error}")
                                            st.json(part)
                                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)

                        elif not errors:
                            show_warning_message("未找到任何匹配的零件。请尝试更详细地描述您的成品。")

                    else: # 智能语义搜索模式
                        with st.spinner("正在进行向量搜索，请稍候..."):
                            results, errors = search_fastgpt_kb(search_query, similarity_threshold)

                        if errors:
                            show_error_message(f"搜索过程中出现错误: {errors[0]['error']}")
                        elif results:
                            show_success_message(f"搜索完成，找到 {len(results)} 个匹配的零件")

                            for i, part in enumerate(results):
                                with st.container():
                                    try:
                                        part_number_safe = str(part.get('part_number', 'N/A'))
                                        part_name_safe = str(part.get('part_name', 'N/A'))
                                        description_safe = str(part.get('description', '无描述'))
                                        operator_safe = str(part.get('operator', 'N/A'))
                                        created_time_safe = str(part.get('created_time', 'N/A'))
                                        score_safe = float(part.get('score', 0.0))

                                        # 获取增强的显示信息
                                        relevance_reason = part.get('relevance_reason', '语义相似')
                                        rerank_score = part.get('rerank_score', 0)
                                        embedding_score = part.get('embedding_score', 0)
                                        
                                        # 确定显示的分数和颜色
                                        display_score = rerank_score if rerank_score > 0 else embedding_score
                                        score_color = "#28a745" if display_score > 0.7 else "#ffc107" if display_score > 0.5 else "#6c757d"
                                        
                                        st.markdown(f"""
                                        <div class="report-card fade-in">
                                            <div class="report-header">
                                                <div class="report-title">🏷️ {part_number_safe} - {part_name_safe}</div>
                                                <div style="text-align: right;">
                                                    <span style="background-color: {score_color}; color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; margin-right: 5px;">
                                                        相似度: {display_score:.4f}
                                                    </span>
                                                    <span style="background-color: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">
                                                        {relevance_reason}
                                                    </span>
                                                </div>
                                            </div>
                                            <p><strong>📄 描述:</strong> {description_safe}</p>
                                            <p><strong>👤 操作员:</strong> {operator_safe}</p>
                                            <p><strong>📅 创建时间:</strong> {created_time_safe}</p>
                                        </div>
                                        """, unsafe_allow_html=True)

                                        image_data = part.get('image')
                                        if image_data:
                                            try:
                                                st.image(f"data:image/jpeg;base64,{image_data}", caption="零件图片",
                                                         use_column_width=True)
                                            except Exception as img_error:
                                                st.warning(f"图片显示失败: {img_error}")

                                        if i < len(results) - 1:
                                            st.markdown("---")

                                    except Exception as display_error:
                                        st.error(f"显示第 {i + 1} 个结果时出错: {display_error}")
                                        st.json(part)
                        else:
                            show_warning_message("未找到匹配的零件。请尝试调整搜索词或降低匹配灵敏度。")
                else:
                    show_warning_message("请输入您的需求描述。")

        st.markdown('</div>', unsafe_allow_html=True)


def _display_search_results(results):
    """显示搜索结果的辅助函数"""
    for i, part in enumerate(results):
        with st.container():
            try:
                part_number_safe = str(part.get('part_number', 'N/A'))
                part_name_safe = str(part.get('part_name', 'N/A'))
                description_safe = str(part.get('description', '无描述'))
                operator_safe = str(part.get('operator', 'N/A'))
                created_time_safe = str(part.get('created_time', 'N/A'))
                
                # 获取增强的显示信息
                relevance_reason = part.get('relevance_reason', '摄像头识别')
                rerank_score = part.get('rerank_score', 0)
                embedding_score = part.get('embedding_score', 0)
                
                # 确定显示的分数和颜色
                display_score = rerank_score if rerank_score > 0 else embedding_score
                score_color = "#28a745" if display_score > 0.7 else "#ffc107" if display_score > 0.5 else "#6c757d"
                
                st.markdown(f"""
                <div class="report-card fade-in">
                    <div class="report-header">
                        <div class="report-title">🏷️ {part_number_safe} - {part_name_safe}</div>
                        <div style="text-align: right;">
                            <span style="background-color: {score_color}; color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; margin-right: 5px;">
                                相似度: {display_score:.4f}
                            </span>
                            <span style="background-color: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">
                                {relevance_reason}
                            </span>
                        </div>
                    </div>
                    <p><strong>📄 描述:</strong> {description_safe}</p>
                    <p><strong>👤 操作员:</strong> {operator_safe}</p>
                    <p><strong>📅 创建时间:</strong> {created_time_safe}</p>
                </div>
                """, unsafe_allow_html=True)

                image_data = part.get('image')
                if image_data:
                    try:
                        st.image(f"data:image/jpeg;base64,{image_data}", caption="零件图片",
                                 use_column_width=True)
                    except Exception as img_error:
                        st.warning(f"图片显示失败: {img_error}")

                if i < len(results) - 1:
                    st.markdown("---")

            except Exception as display_error:
                st.error(f"显示搜索结果时出错: {display_error}")
                st.json(part)


def show_statistics():
    """显示统计分析界面"""
    st.subheader("📊 数据统计分析")

    parts = database.load_parts_data()
    if parts:
        # 基础统计
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f'''
<div class="metric-card">
    <h2>{len(parts)}</h2>
    <p>📦 总零件数</p>
</div>
            ''', unsafe_allow_html=True)

        with col2:
            operators = set(part['operator'] for part in parts)
            st.markdown(f'''
<div class="metric-card">
    <h2>{len(operators)}</h2>
    <p>👥 操作员数量</p>
</div>
            ''', unsafe_allow_html=True)

        with col3:
            with_images = len([part for part in parts if part.get('image')])
            st.markdown(f'''
<div class="metric-card">
    <h2>{with_images}</h2>
    <p>📷 有图片零件</p>
</div>
            ''', unsafe_allow_html=True)

        with col4:
            image_rate = f"{(with_images / len(parts) * 100):.1f}%"
            st.markdown(f'''
<div class="metric-card">
    <h2>{image_rate}</h2>
    <p>📊 图片覆盖率</p>
</div>
            ''', unsafe_allow_html=True)

        st.markdown("---")

        # 操作员统计
        st.subheader("👥 操作员统计")
        operator_stats = {}
        for part in parts:
            operator = part['operator']
            if operator not in operator_stats:
                operator_stats[operator] = 0
            operator_stats[operator] += 1

        operator_df = pd.DataFrame(list(operator_stats.items()), columns=['操作员', '零件数量'])
        operator_df = operator_df.sort_values('零件数量', ascending=False)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(operator_df, use_container_width=True)

        with col2:
            # 简单的柱状图展示
            for _, row in operator_df.iterrows():
                percentage = (row['零件数量'] / len(parts)) * 100
                st.markdown(f"**{row['操作员']}**: {row['零件数量']} 个 ({percentage:.1f}%)")
                st.progress(percentage / 100)

        st.markdown("---")

        # 最近添加的零件
        st.subheader("🕒 最近添加的零件")
        recent_parts = sorted(parts, key=lambda x: x['created_time'], reverse=True)[:5]

        for part in recent_parts:
            st.markdown(f'''
<div class="report-card">
    <div class="report-header">
        <div class="report-title">🏷️ {part['part_number']} - {part['part_name']}</div>
    </div>
    <p><strong>📅 创建时间:</strong> {part['created_time']}</p>
    <p><strong>👤 操作员:</strong> {part['operator']}</p>
</div>
            ''', unsafe_allow_html=True)
    else:
        show_info_message("暂无本地零件数据。")