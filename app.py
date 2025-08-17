import streamlit as st
import pandas as pd
import datetime
import os
import json
from PIL import Image
import base64
import hashlib
from config import LOGO_PATH
from utils import ensure_data_directory, show_success_message, show_error_message, show_warning_message, show_info_message
from database import load_parts_data, add_part, update_part, delete_part, search_parts
from ui import show_parts_query, show_statistics

# 设置页面配置
st.set_page_config(
    page_title="Zicus-AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 参考app_1.py的样式
st.markdown("""
<style>
    .watermark {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
        opacity: 0.7;
        padding: 30px;
        background-color: rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }
    .watermark img {
        width: auto;
        height: auto;
        max-width: 350px;
        max-height: 300px;
    }
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .form-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .data-table {
        margin-top: 30px;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .report-card {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .report-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .report-title {
        font-weight: bold;
        color: #1f77b4;
    }
    .report-actions {
        display: flex;
        gap: 10px;
    }
    
    /* 响应式logo样式 */
    @media (max-width: 768px) {
        .watermark {
            top: 10px;
            left: 10px;
            padding: 20px;
        }
        .watermark img {
            max-width: 300px;
            max-height: 250px;
        }
    }
    
    @media (max-width: 480px) {
        .watermark {
            top: 5px;
            left: 5px;
            padding: 15px;
        }
        .watermark img {
            max-width: 250px;
            max-height: 200px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 数据文件路径
REPORTS_FILE = "dataset/reports.json"
DATA_DIR = "dataset/reports"
USERS_FILE = "dataset/users.json"

def ensure_data_directory():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REPORTS_FILE), exist_ok=True)
    # 初始化用户文件
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
    
    # 检查是否需要创建默认管理员账号
    users = load_users()
    admin_exists = any(u.get('role') == 'admin' for u in users)
    
    if not admin_exists:
        # 创建默认管理员账号
        default_admin = {
            'username': 'admin',
            'password_hash': hash_password('admin123'),
            'role': 'admin',
            'created_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        users.append(default_admin)
        save_users(users)
        print("Default admin account created: admin / admin123")

def load_reports():
    """加载报表列表"""
    if os.path.exists(REPORTS_FILE):
        try:
            with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_reports(reports):
    """保存报表列表"""
    os.makedirs(os.path.dirname(REPORTS_FILE), exist_ok=True)
    with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

def load_users():
    """加载用户列表"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_users(users):
    """保存用户列表"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """对密码进行简单哈希"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username, password, role="user"):
    """注册新用户"""
    username = str(username).strip()
    if not username or not password:
        return False, "Username or password cannot be empty"
    users = load_users()
    if any(u['username'] == username for u in users):
        return False, "Username already exists"
    users.append({
        'username': username,
        'password_hash': hash_password(password),
        'role': role,  # 用户角色：user 或 admin
        'created_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_users(users)
    return True, "Registration successful"

def authenticate_user(username, password):
    """用户登录校验"""
    username = str(username).strip()
    users = load_users()
    for u in users:
        if u['username'] == username and u['password_hash'] == hash_password(password):
            return True, u.get('role', 'user')  # 返回认证状态和用户角色
    return False, None

def main():
    # 水印图片
    st.markdown("""
    <div class="watermark">
        <img src="data:image/png;base64,{}" alt="Logo">
    </div>
    """.format(base64.b64encode(open("imgs/ZICUS LOGO.png", "rb").read()).decode()), unsafe_allow_html=True)
    
    # 主标题
    st.markdown('<h1 class="main-header">Non-standard Part Approval AI Retrieval System</h1>', unsafe_allow_html=True)
    
    # 确保数据目录存在
    ensure_data_directory()
    
    # 侧边栏 - 账号管理
    if 'user' not in st.session_state:
        st.session_state.user = None

    st.sidebar.title("Account")
    if st.session_state.user:
        user_role = st.session_state.user.get('role', 'user')
        role_display = "👑 Admin" if user_role == 'admin' else "👤 User"
        st.sidebar.success(f"Logged in: {st.session_state.user['username']}")
        st.sidebar.info(f"Role: {role_display}")
        if st.sidebar.button("Logout"):
            st.session_state.user = None
            st.rerun()
    else:
        auth_tabs = st.sidebar.tabs(["Login", "Register"])
        with auth_tabs[0]:
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", key="login_button"):
                auth_result, user_role = authenticate_user(login_username, login_password)
                if auth_result:
                    st.session_state.user = { 
                        'username': login_username.strip(),
                        'role': user_role
                    }
                    st.sidebar.success(f"Login successful! Role: {'Admin' if user_role == 'admin' else 'User'}")
                    st.rerun()
                else:
                    st.sidebar.error("Incorrect username or password")
        with auth_tabs[1]:
            reg_username = st.text_input("New Username", key="reg_username")
            reg_password = st.text_input("New Password", type="password", key="reg_password")
            reg_password2 = st.text_input("Confirm Password", type="password", key="reg_password2")
            
            # 角色选择（默认用户）
            reg_role = st.selectbox(
                "User Role",
                ["user", "admin"],
                format_func=lambda x: "👤 Regular User" if x == "user" else "👑 Administrator",
                key="reg_role"
            )
            
            if st.button("Register", key="register_button"):
                if reg_password != reg_password2:
                    st.sidebar.error("Passwords do not match")
                else:
                    ok, msg = register_user(reg_username, reg_password, reg_role)
                    if ok:
                        st.sidebar.success(msg)
                    else:
                        st.sidebar.error(msg)

    # 未登录则不展示功能菜单与主界面功能
    if not st.session_state.user:
        st.header("Please Login First")
        st.info("After logging in, data management and query functions will be displayed. Please complete login or registration in the left sidebar.")
        st.markdown("---")
        st.markdown("©智库zicus-ai| Technical Support: RBCC-phrase3-Team12")
        return

    # 侧边栏 - 功能菜单（根据用户角色显示）
    st.sidebar.title("Function Menu")
    user_role = st.session_state.user.get('role', 'user')
    
    if user_role == 'admin':
        # 管理员：完整功能
        menu = st.sidebar.selectbox(
            "Select Function",
            ["Part Management", "Part Query", "AI Query", "Statistics"]
        )
    else:
        # 用户：只读功能
        menu = st.sidebar.selectbox(
            "Select Function",
            ["Part Query", "AI Query", "Statistics"]
        )
    
    if menu == "Part Management":
        # 检查用户权限
        if st.session_state.user.get('role') != 'admin':
            st.error("⚠️ Insufficient permissions! Only administrators can access part management functions.")
            st.info("Please login with an administrator account.")
            return
        
        st.header("🔧 Part Management")
        
        # 子菜单
        management_tabs = st.tabs(["Add Part", "Edit Part", "Delete Part"])
        
        # 添加零件
        with management_tabs[0]:
            st.subheader("➕ Add New Part")
            
            with st.container():
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    part_number = st.text_input("Part Number", placeholder="Enter part number", key="add_part_number")
                    part_name = st.text_input("Part Name", placeholder="Enter part name", key="add_part_name")
                with col2:
                    operator = st.text_input("Operator", value=st.session_state.user['username'], disabled=True, key="add_operator")
                
                description = st.text_area("Description", placeholder="Enter part description", key="add_description")
                
                # 图片上传
                uploaded_image = st.file_uploader("Upload Part Image", type=['png', 'jpg', 'jpeg'], key="add_image")
                
                if st.button("Add Part", type="primary", key="add_part_btn"):
                    if not part_number or not part_name or not description:
                        st.markdown('<div class="error-message">⚠️ Please fill in all information!</div>', unsafe_allow_html=True)
                    else:
                        # 处理图片数据
                        image_data = None
                        if uploaded_image is not None:
                            image_bytes = uploaded_image.getvalue()
                            image_data = base64.b64encode(image_bytes).decode('utf-8')
                        
                        success, message = add_part(part_number, part_name, description, image_data, st.session_state.user['username'])
                        if success:
                            st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
                            st.balloons()
                            st.rerun()
                        else:
                            st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 编辑零件
        with management_tabs[1]:
            st.subheader("✏️ Edit Part Information")
            
            parts = load_parts_data()
            if parts:
                selected_part = st.selectbox(
                    "Select Part to Edit",
                    parts,
                    format_func=lambda x: f"{x['part_number']} - {x['part_name']}",
                    key="edit_part_select"
                )
                
                if selected_part:
                    with st.container():
                        st.markdown('<div class="form-container">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_part_number = st.text_input("Part Number", value=selected_part['part_number'], key="edit_part_number")
                            new_part_name = st.text_input("Part Name", value=selected_part['part_name'], key="edit_part_name")
                        with col2:
                            new_operator = st.text_input("Operator", value=st.session_state.user['username'], disabled=True, key="edit_operator")
                        
                        new_description = st.text_area("Description", value=selected_part['description'], key="edit_description")
                        
                        # 显示当前图片
                        if selected_part.get('image'):
                            st.image(f"data:image/jpeg;base64,{selected_part['image']}", caption="Current Image", width=200)
                        
                        # 新图片上传（可选）
                        new_image = st.file_uploader("Upload New Image (Optional)", type=['png', 'jpg', 'jpeg'], key="edit_image")
                        
                        if st.button("Update Part", type="primary", key="update_part_btn"):
                            if not new_part_number or not new_part_name or not new_description:
                                st.markdown('<div class="error-message">⚠️ Please fill in all information!</div>', unsafe_allow_html=True)
                            else:
                                # 处理新图片数据
                                new_image_data = None
                                if new_image is not None:
                                    image_bytes = new_image.getvalue()
                                    new_image_data = base64.b64encode(image_bytes).decode('utf-8')
                                
                                success, message = update_part(selected_part['id'], new_part_number, new_part_name, new_description, new_image_data, st.session_state.user['username'])
                                if success:
                                    st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
                                    st.rerun()
                                else:
                                    st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No part data available.")
        
        # 删除零件
        with management_tabs[2]:
            st.subheader("🗑️ Delete Part")
            
            parts = load_parts_data()
            if parts:
                selected_part = st.selectbox(
                    "Select Part to Delete",
                    parts,
                    format_func=lambda x: f"{x['part_number']} - {x['part_name']}",
                    key="delete_part_select"
                )
                
                if selected_part:
                    st.warning(f"You are about to delete the following part:")
                    st.write(f"Part Number: {selected_part['part_number']}")
                    st.write(f"Part Name: {selected_part['part_name']}")
                    st.write(f"Description: {selected_part['description']}")
                    st.write(f"Operator: {selected_part['operator']}")
                    st.write(f"Created Time: {selected_part['created_time']}")
                    
                    if selected_part.get('image'):
                        st.image(f"data:image/jpeg;base64,{selected_part['image']}", caption="Part Image", width=200)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Confirm Delete", type="secondary", key="confirm_delete_part"):
                            if delete_part(selected_part['id']):
                                st.markdown('<div class="success-message">✅ Part deleted successfully!</div>', unsafe_allow_html=True)
                                st.rerun()
                            else:
                                st.markdown('<div class="error-message">❌ Part deletion failed!</div>', unsafe_allow_html=True)
                    with col2:
                        if st.button("Cancel Delete", key="cancel_delete_part"):
                            st.rerun()
            else:
                st.info("No part data available.")
    
    elif menu == "Part Query":
        # 所有用户都可以查询零件
        st.header("🔍 Part Query")
        
        # 搜索选项
        search_tabs = st.tabs(["Search Parts", "Browse All Parts"])
        
        # 搜索零件
        with search_tabs[0]:
            st.subheader("🔍 Search Parts")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                search_query = st.text_input("Search Keywords", placeholder="Enter part number, name or description", key="search_input")
            with col2:
                search_type = st.selectbox(
                    "Search Type",
                    ["all", "part_number", "description"],
                    format_func=lambda x: {"all": "All", "part_number": "Part Number", "description": "Description"}[x],
                    key="search_type"
                )
            
            if st.button("🔍 Search", type="primary", key="search_btn"):
                if search_query:
                    results = search_parts(search_query, search_type)
                    if results:
                        st.success(f"Found {len(results)} matching parts")
                        
                        # 显示搜索结果
                        for part in results:
                            with st.container():
                                st.markdown(f"""
                                <div class="report-card">
                                    <div class="report-header">
                                        <div class="report-title">{part['part_number']} - {part['part_name']}</div>
                                    </div>
                                    <p><strong>Description:</strong> {part['description']}</p>
                                    <p><strong>Operator:</strong> {part['operator']}</p>
                                    <p><strong>Created Time:</strong> {part['created_time']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # 显示图片
                                if part.get('image'):
                                    st.image(f"data:image/jpeg;base64,{part['image']}", caption="Part Image", width=300)
                                
                                st.markdown("---")
                    else:
                        st.warning("No matching parts found")
                else:
                    st.warning("Please enter search keywords")
        
        # 浏览所有零件
        with search_tabs[1]:
            st.subheader("📋 Browse All Parts")
            
            parts = load_parts_data()
            if parts:
                # 统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Parts", len(parts))
                with col2:
                    st.metric("Operators", len(set(part['operator'] for part in parts)))
                with col3:
                    st.metric("Parts with Images", len([part for part in parts if part.get('image')]))
                
                # 显示所有零件
                for part in parts:
                    with st.container():
                        st.markdown(f"""
                        <div class="report-card">
                            <div class="report-header">
                                <div class="report-title">{part['part_number']} - {part['part_name']}</div>
                            </div>
                            <p><strong>Description:</strong> {part['description']}</p>
                            <p><strong>Operator:</strong> {part['operator']}</p>
                            <p><strong>Created Time:</strong> {part['created_time']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 显示图片
                        if part.get('image'):
                            st.image(f"data:image/jpeg;base64,{part['image']}", caption="Part Image", width=300)
                        
                        st.markdown("---")
                
                # 导出功能
                if parts:
                    # 转换为DataFrame用于导出
                    df_data = []
                    for part in parts:
                        df_data.append({
                            'Part Number': part['part_number'],
                            'Part Name': part['part_name'],
                            'Description': part['description'],
                            'Operator': part['operator'],
                            'Created Time': part['created_time']
                        })
                    
                    df = pd.DataFrame(df_data)
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 Export All Parts Data (CSV)",
                        data=csv,
                        file_name=f"Parts_Database_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No part data available.")
    
    elif menu == "AI Query":
        # AI查询功能 - 保持原有功能
        show_parts_query()
    
    elif menu == "Statistics":
        # 统计分析功能 - 保持原有功能
        show_statistics()
    
    # 页脚
    st.markdown("---")
    st.markdown("©智库zicus-ai| Technical Support: RBCC-phrase3-Team12")

def require_admin():
    """检查用户是否为管理员"""
    if 'user' not in st.session_state or st.session_state.user.get('role') != 'admin':
        st.error("⚠️ Insufficient permissions! This function requires administrator privileges.")
        st.info("Please login with an administrator account.")
        return False
    return True

if __name__ == "__main__":
    main()
