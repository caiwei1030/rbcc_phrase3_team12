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
    """Display parts query interface, integrating product decomposition with intelligent search"""
    st.subheader("🤖 Intelligent Parts Finder")
    show_info_message("You can choose to decompose products to find parts, perform intelligent semantic search, or use camera recognition to automatically decompose products.")

    search_mode = st.radio(
        "Select Search Mode:",
        ("Product Decomposition (AI)", "Intelligent Semantic Search", "Camera Recognition + Decomposition (AI)"),
        key="search_mode_radio",
        horizontal=True
    )

    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)

        search_query_label = "" # Placeholder for label
        search_query_placeholder = "" # Placeholder for placeholder
        search_button_label = "" # Placeholder for button label

        if search_mode == "Product Decomposition (AI)":
            search_query_label = "💬 Please enter product name"
            search_query_placeholder = "e.g., A wooden desk with drawers"
            search_button_label = "🤖 AI Intelligent Decomposition and Parts Search"
        elif search_mode == "Intelligent Semantic Search":
            search_query_label = "💬 Please enter your requirements"
            search_query_placeholder = "e.g., A hexagonal flange for fixing"
            search_button_label = "🧠 AI Intelligent Search"
        else: # Camera Recognition + Decomposition (AI)
            search_query_label = "📹 Camera Product Recognition and Decomposition"
            search_query_placeholder = ""
            search_button_label = "📸 Recognize Products and Decompose"

        # Display different input interfaces based on mode
        search_query = ""
        if search_mode == "Camera Recognition + Decomposition (AI)":
            # Special UI for camera recognition mode - using st.camera_input
            st.markdown("### 📹 AI Smart Camera - Photo Recognition and Decomposition")
            
            # Create centered camera area
            camera_col1, camera_col2, camera_col3 = st.columns([1, 3, 1])
            with camera_col2:
                # Use st.camera_input for photo capture
                st.markdown("#### 📸 Photo Recognition")
                st.info("Please click the button below to take a photo, AI will automatically recognize products in the photo")
                
                # Camera input component
                camera_photo = st.camera_input(
                    "📷 Click to take photo for AI recognition",
                    key="camera_input",
                    help="Click the photo button, AI will automatically recognize products in the photo"
                )
                
                # If photo is taken, perform recognition
                if camera_photo is not None:
                    with st.spinner("🤖 AI is recognizing products in the photo..."):
                        # Import new recognition functions
                        from services.camera_service import capture_and_recognize_from_image, set_recognition_result
                        
                        # Perform recognition
                        result = capture_and_recognize_from_image(camera_photo)
                        
                        if result.get('success'):
                            # Save recognition result
                            set_recognition_result(result)
                            st.success("✅ Recognition completed!")
                        else:
                            st.error(f"❌ Recognition failed: {result.get('error', 'Unknown error')}")
            
            # Display recognition results below camera
            with camera_col2:
                # Check and display latest recognition result
                latest_result = get_latest_recognition_result()
                
                # System status display
                st.markdown("#### 🔍 Recognition Status")
                
                if latest_result and latest_result.get('success'):
                    st.success("🤖 AI Recognition: Completed")
                else:
                    st.info("📷 Waiting for photo recognition...")
                
                if latest_result and latest_result.get('success'):
                    recognized_products = latest_result.get('products', [])
                    if recognized_products:
                        st.markdown(f"""
                        <div class="recognition-result">
                            <h4>🎯 Detected {len(recognized_products)} products:</h4>
                            <ul>
                        """, unsafe_allow_html=True)
                        
                        for i, product in enumerate(recognized_products, 1):
                            st.markdown(f"<li><strong>{i}. {product}</strong></li>", unsafe_allow_html=True)
                        
                        st.markdown("</ul></div>", unsafe_allow_html=True)
                        
                        # Button row
                        btn_col1, btn_col2 = st.columns(2)
                        
                        with btn_col1:
                            decompose_btn = st.button("🤖 Auto-decompose All Products", key="auto_decompose", use_container_width=True)
                        
                        with btn_col2:
                            clear_btn = st.button("🗑️ Clear Results", key="clear_result", use_container_width=True)
                        
                        # Handle decomposition button
                        if decompose_btn:
                            with st.spinner("🔧 AI is automatically decomposing products..."):
                                # Decompose all recognized products
                                all_results = {}
                                all_errors = []
                                
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for i, product in enumerate(recognized_products):
                                    status_text.text(f"🔧 Decomposing: {product} ({i+1}/{len(recognized_products)})")
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
                                status_text.text("✅ Decomposition completed!")
                                progress_bar.empty()
                                status_text.empty()
                                
                                # Display decomposition results
                                if all_results:
                                    total_parts = sum(len(parts) for parts in all_results.values())
                                    show_success_message(f"🎉 Found {total_parts} related parts!")
                                    
                                    for component_key, parts in all_results.items():
                                        st.markdown(f"### 🔍 {component_key}")
                                        if parts:
                                            _display_search_results(parts)
                                        else:
                                            show_warning_message("No matching parts found for this component")
                                        st.markdown("<hr>", unsafe_allow_html=True)
                                
                                # Clear recognition results
                                clear_recognition_result()
                        
                        # Handle clear button
                        if clear_btn:
                            clear_recognition_result()
                            st.success("🗑️ Recognition results cleared")
                            st.rerun()
                    else:
                        st.warning("⚠️ No products recognized")
                else:
                    st.info("📷 Please take a photo for AI recognition")
                    
                    # Add usage instructions
                    with st.expander("❓ Usage Instructions", expanded=True):
                        st.markdown("""
                        **📋 Usage Steps:**
                        
                        1. Click the **"📷 Click to take photo for AI recognition"** button above
                        2. Allow browser access to camera permissions
                        3. Aim at the product to be recognized, click to take photo
                        4. AI will automatically recognize products in the photo
                        5. Click "🤖 Auto-decompose All Products" for parts decomposition
                        
                        **💡 Usage Tips:**
                        
                        - 💡 Better results in well-lit environments
                        - 📐 Place the complete product in the center of the frame
                        - 🚫 Avoid obstructions, ensure clear product outline
                        - 📱 Wait for AI recognition to complete before proceeding
                        """)
                        
                        # Check AI model status
                        st.markdown("**🔍 AI Model Status:**")
                        try:
                            from services.llm_service import llm_client
                            if llm_client:
                                st.success("✅ AI model client initialized")
                            else:
                                st.error("❌ AI model client not initialized")
                        except Exception as e:
                            st.error(f"❌ AI model check failed: {e}")
            
            # Settings area
            st.markdown("---")
            st.markdown("#### ⚙️ AI Recognition Settings")
            
            col1, col2 = st.columns(2)
            with col1:
                recognition_confidence = st.slider(
                    "🎯 Recognition Confidence", 
                    0.1, 1.0, 0.7, 0.05,
                    help="Set AI recognition confidence threshold, higher values mean stricter recognition"
                )
            
            with col2:
                # Debug button
                debug_btn = st.button("🐛 Debug Status", key="debug_btn")
                
                # Simulation test buttons
                col_sim1, col_sim2 = st.columns(2)
                with col_sim1:
                    simulate_btn = st.button("🎭 Simulate Recognition", key="simulate_btn")
                with col_sim2:
                    clear_sim_btn = st.button("🧹 Clear Simulation", key="clear_sim_btn")
        else:
            # Original text input mode
            search_query = st.text_input(search_query_label, placeholder=search_query_placeholder,
                                         key="search_input")
        
        # Only show similarity slider in intelligent semantic search mode
        similarity_threshold = 0.5 # Default value
        if search_mode == "Intelligent Semantic Search":
            similarity_threshold = st.slider("🎯 Match Sensitivity (lower values = more fuzzy)", 0.1, 1.0, 0.5, 0.05)

        # Display different buttons and processing logic based on mode
        if search_mode == "Camera Recognition + Decomposition (AI)":
            # Handle button operations
            if simulate_btn:
                # Simulate recognition results
                mock_products = ["Computer Mouse", "Keyboard", "Monitor"]
                simulation_result = {
                    "success": True,
                    "products": mock_products,
                    "image_base64": "simulation"
                }
                from services.camera_service import set_recognition_result
                set_recognition_result(simulation_result)
                st.success(f"🎭 Simulation recognition successful: {', '.join(mock_products)}")
                st.rerun()
            
            elif clear_sim_btn:
                clear_recognition_result()
                st.success("🧹 Simulation results cleared")
                st.rerun()
            
            elif debug_btn:
                st.info("🐛 System Status Debug Information")
                debug_status = get_camera_status_debug()
                st.json(debug_status)
                
                # Display current status and solutions
                with st.expander("📋 Function Status Description", expanded=True):
                    st.markdown("""
                    **🎯 Current Function Status:**
                    
                    - 📹 **Camera Photo**: ✅ Using st.camera_input, no startup required
                    - 🤖 **AI Recognition**: ✅ Automatic recognition after photo
                    - 🔧 **Auto-decomposition**: ✅ Working normally
                    - 🔍 **Parts Search**: ✅ Working normally
                    
                    **💡 Usage Flow:**
                    
                    1. Click photo button to take photo
                    2. AI automatically recognizes products in photo
                    3. Click "Auto-decompose" for parts decomposition
                    4. System searches for matching parts
                    """)
                    
                    # Function status description
                    st.info("💡 Using st.camera_input, no complex camera startup process required")
        
        else:
            # Original text search button
            if st.button(search_button_label, type="primary", key="search_btn", use_container_width=True):
                if search_query:
                    if search_mode == "Product Decomposition (AI)":
                        with st.spinner("Decomposing products and searching for parts, please wait..."):
                            results, errors = find_parts_for_product(search_query)

                        if errors:
                            for error in errors:
                                show_error_message(f"{error.get('content')}: {error.get('error')}")
                        
                        if results:
                            total_parts_found = sum(len(parts) for parts in results.values())
                            show_success_message(f"Decomposition completed! Found {total_parts_found} related parts for {len(results)} components.")

                            for component, parts in results.items():
                                st.markdown(f"### Search Component: **`{component}`**")
                                if not parts:
                                    show_warning_message("No matching parts found for this component.")
                                    continue

                                for i, part in enumerate(parts):
                                    with st.container():
                                        try:
                                            part_number_safe = str(part.get('part_number', 'N/A'))
                                            part_name_safe = str(part.get('part_name', 'N/A'))
                                            description_safe = str(part.get('description', 'No description'))
                                            operator_safe = str(part.get('operator', 'N/A'))
                                            created_time_safe = str(part.get('created_time', 'N/A'))
                                            score_safe = float(part.get('score', 0.0))

                                            # Get enhanced display information
                                            relevance_reason = part.get('relevance_reason', 'Semantic similarity')
                                            rerank_score = part.get('rerank_score', 0)
                                            embedding_score = part.get('embedding_score', 0)
                                            
                                            # Determine display score and color
                                            display_score = rerank_score if rerank_score > 0 else embedding_score
                                            score_color = "#28a745" if display_score > 0.7 else "#ffc107" if display_score > 0.5 else "#6c757d"
                                            
                                            st.markdown(f"""
                                            <div class="report-card fade-in">
                                                <div class="report-header">
                                                    <div class="report-title">🏷️ {part_number_safe} - {part_name_safe}</div>
                                                    <div style="text-align: right;">
                                                        <span style="background-color: {score_color}; color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; margin-right: 5px;">
                                                            Similarity: {display_score:.4f}
                                                        </span>
                                                        <span style="background-color: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">
                                                            {relevance_reason}
                                                        </span>
                                                    </div>
                                                </div>
                                                <p><strong>📄 Description:</strong> {description_safe}</p>
                                                <p><strong>👤 Operator:</strong> {operator_safe}</p>
                                                <p><strong>📅 Created Time:</strong> {created_time_safe}</p>
                                            </div>
                                            """, unsafe_allow_html=True)

                                            # 显示零件图片（如果有）
                                            image_data = part.get('image')
                                            if image_data:
                                                try:
                                                    # 使用列布局来更好地控制图片大小
                                                    col1, col2, col3 = st.columns([1, 2, 1])
                                                    with col2:
                                                        st.image(f"data:image/jpeg;base64,{image_data}", 
                                                                 caption="Part Image",
                                                                 width=400,  # 固定宽度，适应网页展示
                                                                 use_column_width=False)  # 不使用列宽，保持固定尺寸
                                                except Exception as img_error:
                                                    st.warning(f"Image display failed: {img_error}")
                                            
                                            # 显示CAD图片（如果有）
                                            cad_image_data = part.get('cad_image')
                                            if cad_image_data:
                                                st.markdown("---")
                                                st.markdown("### 🎨 CAD设计图")
                                                try:
                                                    st.image(f"data:image/png;base64,{cad_image_data}", 
                                                             caption=f"CAD Design: {part.get('part_name', 'N/A')}",
                                                             use_column_width=True)
                                                except Exception as cad_img_error:
                                                    st.warning(f"CAD image display failed: {cad_img_error}")
                                            
                                            # 显示CAD图片路径信息（调试用）
                                            if part.get('has_cad_image'):
                                                with st.expander("🔍 CAD图片信息", expanded=False):
                                                    st.info(f"**CAD图片路径:** {part.get('cad_image_path', 'N/A')}")
                                                    st.info(f"**零件ID:** {part.get('part_number', 'N/A')}")
                                                    st.info(f"**源文件:** {part.get('source_file', 'N/A')}")

                                            if i < len(parts) - 1:
                                                st.markdown("---")

                                        except Exception as display_error:
                                            st.error(f"Error displaying part '{part.get('part_name')}': {display_error}")
                                            st.json(part)
                                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)

                        elif not errors:
                            show_warning_message("No matching parts found. Please try describing your product in more detail.")

                    else: # Intelligent semantic search mode
                        with st.spinner("Performing vector search, please wait..."):
                            results, errors = search_fastgpt_kb(search_query, similarity_threshold)

                        if errors:
                            show_error_message(f"Error occurred during search: {errors[0]['error']}")
                        elif results:
                            show_success_message(f"Search completed, found {len(results)} matching parts")

                            for i, part in enumerate(results):
                                with st.container():
                                    try:
                                        part_number_safe = str(part.get('part_number', 'N/A'))
                                        part_name_safe = str(part.get('part_name', 'N/A'))
                                        description_safe = str(part.get('description', 'No description'))
                                        operator_safe = str(part.get('operator', 'N/A'))
                                        created_time_safe = str(part.get('created_time', 'N/A'))
                                        score_safe = float(part.get('score', 0.0))

                                        # Get enhanced display information
                                        relevance_reason = part.get('relevance_reason', 'Semantic similarity')
                                        rerank_score = part.get('rerank_score', 0)
                                        embedding_score = part.get('embedding_score', 0)
                                        
                                        # Determine display score and color
                                        display_score = rerank_score if rerank_score > 0 else embedding_score
                                        score_color = "#28a745" if display_score > 0.7 else "#ffc107" if display_score > 0.5 else "#6c757d"
                                        
                                        st.markdown(f"""
                                        <div class="report-card fade-in">
                                            <div class="report-header">
                                                <div class="report-title">🏷️ {part_number_safe} - {part_name_safe}</div>
                                                <div style="text-align: right;">
                                                    <span style="background-color: {score_color}; color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; margin-right: 5px;">
                                                        Similarity: {display_score:.4f}
                                                    </span>
                                                    <span style="background-color: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">
                                                        {relevance_reason}
                                                    </span>
                                                </div>
                                            </div>
                                            <p><strong>📄 Description:</strong> {description_safe}</p>
                                            <p><strong>👤 Operator:</strong> {operator_safe}</p>
                                            <p><strong>📅 Created Time:</strong> {created_time_safe}</p>
                                        </div>
                                        """, unsafe_allow_html=True)

                                        # 显示零件图片（如果有）
                                        image_data = part.get('image')
                                        if image_data:
                                            try:
                                                # 使用列布局来更好地控制图片大小
                                                col1, col2, col3 = st.columns([1, 2, 1])
                                                with col2:
                                                    st.image(f"data:image/jpeg;base64,{image_data}", 
                                                             caption="Part Image",
                                                             width=400,  # 固定宽度，适应网页展示
                                                             use_column_width=False)  # 不使用列宽，保持固定尺寸
                                            except Exception as img_error:
                                                st.warning(f"Image display failed: {img_error}")
                                        
                                        # 显示CAD图片（如果有）
                                        cad_image_data = part.get('cad_image')
                                        if cad_image_data:
                                            st.markdown("---")
                                            st.markdown("### 🎨 CAD设计图")
                                            try:
                                                st.image(f"data:image/png;base64,{cad_image_data}", 
                                                         caption=f"CAD Design: {part.get('part_name', 'N/A')}",
                                                         use_column_width=True)
                                            except Exception as cad_img_error:
                                                st.warning(f"CAD image display failed: {cad_img_error}")
                                        
                                        # 显示CAD图片路径信息（调试用）
                                        if part.get('has_cad_image'):
                                            with st.expander("🔍 CAD图片信息", expanded=False):
                                                st.info(f"**CAD图片路径:** {part.get('cad_image_path', 'N/A')}")
                                                st.info(f"**零件ID:** {part.get('part_number', 'N/A')}")
                                                st.info(f"**源文件:** {part.get('source_file', 'N/A')}")

                                        if i < len(results) - 1:
                                            st.markdown("---")

                                    except Exception as display_error:
                                        st.error(f"Error displaying part '{part.get('part_name')}': {display_error}")
                                        st.json(part)
                        else:
                            show_warning_message("No matching parts found. Please try a different search term.")
                else:
                    show_warning_message("Please enter a search query.")

        st.markdown('</div>', unsafe_allow_html=True)


def _display_search_results(results):
    """Display helper function for search results"""
    for i, part in enumerate(results):
        with st.container():
            try:
                part_number_safe = str(part.get('part_number', 'N/A'))
                part_name_safe = str(part.get('part_name', 'N/A'))
                description_safe = str(part.get('description', 'No description'))
                operator_safe = str(part.get('operator', 'N/A'))
                created_time_safe = str(part.get('created_time', 'N/A'))
                
                # Get enhanced display information
                relevance_reason = part.get('relevance_reason', 'Camera Recognition')
                rerank_score = part.get('rerank_score', 0)
                embedding_score = part.get('embedding_score', 0)
                
                # Determine display score and color
                display_score = rerank_score if rerank_score > 0 else embedding_score
                score_color = "#28a745" if display_score > 0.7 else "#ffc107" if display_score > 0.5 else "#6c757d"
                
                st.markdown(f"""
                <div class="report-card fade-in">
                    <div class="report-header">
                        <div class="report-title">🏷️ {part_number_safe} - {part_name_safe}</div>
                        <div style="text-align: right;">
                            <span style="background-color: {score_color}; color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; margin-right: 5px;">
                                Similarity: {display_score:.4f}
                            </span>
                            <span style="background-color: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">
                                {relevance_reason}
                            </span>
                        </div>
                    </div>
                    <p><strong>📄 Description:</strong> {description_safe}</p>
                    <p><strong>👤 Operator:</strong> {operator_safe}</p>
                    <p><strong>📅 Created Time:</strong> {created_time_safe}</p>
                </div>
                """, unsafe_allow_html=True)

                # 显示零件图片（如果有）
                image_data = part.get('image')
                if image_data:
                    try:
                        # 使用列布局来更好地控制图片大小
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.image(f"data:image/jpeg;base64,{image_data}", 
                                     caption="Part Image",
                                     width=400,  # 固定宽度，适应网页展示
                                     use_column_width=False)  # 不使用列宽，保持固定尺寸
                    except Exception as img_error:
                        st.warning(f"Image display failed: {img_error}")
                
                # 显示CAD图片（如果有）
                cad_image_data = part.get('cad_image')
                if cad_image_data:
                    st.markdown("---")
                    st.markdown("### 🎨 CAD设计图")
                    try:
                        # 使用列布局来更好地控制图片大小
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.image(f"data:image/png;base64,{cad_image_data}", 
                                     caption=f"CAD Design: {part.get('part_name', 'N/A')}",
                                     width=400,  # 固定宽度，适应网页展示
                                     use_column_width=False)  # 不使用列宽，保持固定尺寸
                    except Exception as cad_img_error:
                        st.warning(f"CAD image display failed: {cad_img_error}")
                
                # 显示CAD图片路径信息（调试用）
                if part.get('has_cad_image'):
                    with st.expander("🔍 CAD图片信息", expanded=False):
                        st.info(f"**CAD图片路径:** {part.get('cad_image_path', 'N/A')}")
                        st.info(f"**零件ID:** {part.get('part_number', 'N/A')}")
                        st.info(f"**源文件:** {part.get('source_file', 'N/A')}")
                        # 添加图片预览
                        if part.get('cad_image'):
                            st.image(f"data:image/png;base64,{part['cad_image']}", 
                                     caption="CAD图片预览",
                                     width=300,
                                     use_column_width=False)

                if i < len(results) - 1:
                    st.markdown("---")

            except Exception as display_error:
                st.error(f"Error displaying search results: {display_error}")
                st.json(part)


def show_statistics():
    """Display statistical analysis interface"""
    st.subheader("📊 Data Statistical Analysis")

    parts = database.load_parts_data()
    if parts:
        # Basic statistics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f'''
<div class="metric-card">
    <h2>{len(parts)}</h2>
    <p>📦 Total Parts</p>
</div>
            ''', unsafe_allow_html=True)

        with col2:
            operators = set(part['operator'] for part in parts)
            st.markdown(f'''
<div class="metric-card">
    <h2>{len(operators)}</h2>
    <p>👥 Number of Operators</p>
</div>
            ''', unsafe_allow_html=True)

        with col3:
            with_images = len([part for part in parts if part.get('image')])
            st.markdown(f'''
<div class="metric-card">
    <h2>{with_images}</h2>
    <p>📷 Parts with Images</p>
</div>
            ''', unsafe_allow_html=True)

        with col4:
            image_rate = f"{(with_images / len(parts) * 100):.1f}%"
            st.markdown(f'''
<div class="metric-card">
    <h2>{image_rate}</h2>
    <p>📊 Image Coverage</p>
</div>
            ''', unsafe_allow_html=True)

        st.markdown("---")

        # Operator statistics
        st.subheader("👥 Operator Statistics")
        operator_stats = {}
        for part in parts:
            operator = part['operator']
            if operator not in operator_stats:
                operator_stats[operator] = 0
            operator_stats[operator] += 1

        operator_df = pd.DataFrame(list(operator_stats.items()), columns=['Operator', 'Number of Parts'])
        operator_df = operator_df.sort_values('Number of Parts', ascending=False)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.dataframe(operator_df, use_container_width=True)

        with col2:
            # Simple bar chart display
            for _, row in operator_df.iterrows():
                percentage = (row['Number of Parts'] / len(parts)) * 100
                st.markdown(f"**{row['Operator']}**: {row['Number of Parts']} parts ({percentage:.1f}%)")
                st.progress(percentage / 100)

        st.markdown("---")

        # Recently added parts
        st.subheader("🕒 Recently Added Parts")
        recent_parts = sorted(parts, key=lambda x: x['created_time'], reverse=True)[:5]

        for part in recent_parts:
            st.markdown(f'''
<div class="report-card">
    <div class="report-header">
        <div class="report-title">🏷️ {part['part_number']} - {part['part_name']}</div>
    </div>
    <p><strong>📅 Created Time:</strong> {part['created_time']}</p>
    <p><strong>👤 Operator:</strong> {part['operator']}</p>
</div>
            ''', unsafe_allow_html=True)
    else:
        show_info_message("No local part data available.")