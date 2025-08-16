import streamlit as st
import pandas as pd
import datetime
import os
import json
from PIL import Image
import base64
import hashlib

# 设置页面配置
st.set_page_config(
    page_title="Zicus-AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .watermark {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
        opacity: 0.8;
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
        # object-fit: contain;
        # display: block;
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
        print("已创建默认管理员账号：admin / admin123")

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
        return False, "用户名或密码不能为空"
    users = load_users()
    if any(u['username'] == username for u in users):
        return False, "用户名已存在"
    users.append({
        'username': username,
        'password_hash': hash_password(password),
        'role': role,  # 用户角色：user 或 admin
        'created_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_users(users)
    return True, "注册成功"

def authenticate_user(username, password):
    """用户登录校验"""
    username = str(username).strip()
    users = load_users()
    for u in users:
        if u['username'] == username and u['password_hash'] == hash_password(password):
            return True, u.get('role', 'user')  # 返回认证状态和用户角色
    return False, None

def load_parts_data():
    """加载零件数据库"""
    parts_file = "dataset/parts.json"
    if os.path.exists(parts_file):
        try:
            with open(parts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_parts_data(parts):
    """保存零件数据库"""
    parts_file = "dataset/parts.json"
    os.makedirs(os.path.dirname(parts_file), exist_ok=True)
    with open(parts_file, 'w', encoding='utf-8') as f:
        json.dump(parts, f, ensure_ascii=False, indent=2)

# 移除不再需要的报表相关函数

def get_next_part_id():
    """获取下一个零件ID"""
    parts = load_parts_data()
    if not parts:
        return 1
    return max(part['id'] for part in parts) + 1

def add_part(part_number, part_name, description, image_data, operator):
    """添加新零件"""
    parts = load_parts_data()
    
    # 检查零件编号是否已存在
    if any(part['part_number'] == part_number for part in parts):
        return False, "零件编号已存在"
    
    new_part = {
        'id': get_next_part_id(),
        'part_number': part_number,
        'part_name': part_name,
        'description': description,
        'image': image_data,
        'operator': operator,
        'created_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    parts.append(new_part)
    save_parts_data(parts)
    return True, "零件添加成功"

def update_part(part_id, part_number, part_name, description, image_data, operator):
    """更新零件信息"""
    parts = load_parts_data()
    
    for part in parts:
        if part['id'] == part_id:
            # 检查零件编号是否与其他零件重复
            if any(p['part_number'] == part_number and p['id'] != part_id for p in parts):
                return False, "零件编号与其他零件重复"
            
            part['part_number'] = part_number
            part['part_name'] = part_name
            part['description'] = description
            if image_data:  # 只有当有新图片时才更新
                part['image'] = image_data
            part['operator'] = operator
            part['updated_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    
    save_parts_data(parts)
    return True, "零件更新成功"

def delete_part(part_id):
    """删除零件"""
    parts = load_parts_data()
    parts = [part for part in parts if part['id'] != part_id]
    save_parts_data(parts)
    return True

def search_parts(query, search_type="all"):
    """搜索零件"""
    parts = load_parts_data()
    if not query:
        return parts
    
    query = query.lower().strip()
    results = []
    
    for part in parts:
        if search_type == "all":
            # 在所有字段中搜索
            if (query in part['part_number'].lower() or 
                query in part['part_name'].lower() or 
                query in part['description'].lower()):
                results.append(part)
        elif search_type == "part_number":
            # 只在零件编号中搜索
            if query in part['part_number'].lower():
                results.append(part)
        elif search_type == "description":
            # 只在描述中搜索
            if query in part['description'].lower():
                results.append(part)
    
    return results

# 移除不再需要的报表相关函数

def main():
    # 水印图片
    st.markdown("""
    <div class="watermark">
        <img src="data:image/png;base64,{}" alt="Logo">
    </div>
    """.format(base64.b64encode(open("imgs/logo/ZICUS LOGO.png", "rb").read()).decode()), unsafe_allow_html=True)
    
    # 主标题
    st.markdown('<h1 class="main-header">Non-standard Part Approval AI Retrieval System</h1>', unsafe_allow_html=True)
    
    # 确保数据目录存在
    ensure_data_directory()
    
    # 侧边栏 - 账号管理
    if 'user' not in st.session_state:
        st.session_state.user = None

    st.sidebar.title("账号")
    if st.session_state.user:
        user_role = st.session_state.user.get('role', 'user')
        role_display = "👑 管理员" if user_role == 'admin' else "👤 用户"
        st.sidebar.success(f"已登录：{st.session_state.user['username']}")
        st.sidebar.info(f"角色：{role_display}")
        if st.sidebar.button("注销"):
            st.session_state.user = None
            st.rerun()
    else:
        auth_tabs = st.sidebar.tabs(["登录", "注册"])
        with auth_tabs[0]:
            login_username = st.text_input("用户名", key="login_username")
            login_password = st.text_input("密码", type="password", key="login_password")
            if st.button("登录", key="login_button"):
                auth_result, user_role = authenticate_user(login_username, login_password)
                if auth_result:
                    st.session_state.user = { 
                        'username': login_username.strip(),
                        'role': user_role
                    }
                    st.sidebar.success(f"登录成功！角色：{'管理员' if user_role == 'admin' else '用户'}")
                    st.rerun()
                else:
                    st.sidebar.error("用户名或密码不正确")
        with auth_tabs[1]:
            reg_username = st.text_input("新用户名", key="reg_username")
            reg_password = st.text_input("新密码", type="password", key="reg_password")
            reg_password2 = st.text_input("确认密码", type="password", key="reg_password2")
            
            # 角色选择（默认用户）
            reg_role = st.selectbox(
                "用户角色",
                ["user", "admin"],
                format_func=lambda x: "👤 普通用户" if x == "user" else "👑 管理员",
                key="reg_role"
            )
            
            if st.button("注册", key="register_button"):
                if reg_password != reg_password2:
                    st.sidebar.error("两次输入的密码不一致")
                else:
                    ok, msg = register_user(reg_username, reg_password, reg_role)
                    if ok:
                        st.sidebar.success(msg)
                    else:
                        st.sidebar.error(msg)

    # 未登录则不展示功能菜单与主界面功能
    if not st.session_state.user:
        st.header("请先登录")
        st.info("登录后将显示数据管理和查询功能。请在左侧侧边栏完成登录或注册。")
        st.markdown("---")
        st.markdown("©智库zicus-ai| 技术支持：RBCC-phrase3-Team12-蔡伟")
        return

    # 侧边栏 - 功能菜单（根据用户角色显示）
    st.sidebar.title("功能菜单")
    user_role = st.session_state.user.get('role', 'user')
    
    if user_role == 'admin':
        # 管理员：完整功能
        menu = st.sidebar.selectbox(
            "选择功能",
            ["零件管理", "零件查询"]
        )
    else:
        # 用户：只读功能
        menu = st.sidebar.selectbox(
            "选择功能",
            ["零件查询"]
        )
    
    if menu == "零件管理":
        # 检查用户权限
        if st.session_state.user.get('role') != 'admin':
            st.error("⚠️ 权限不足！只有管理员可以访问零件管理功能。")
            st.info("请使用管理员账号登录。")
            return
        
        st.header("🔧 零件管理")
        
        # 子菜单
        management_tabs = st.tabs(["添加零件", "编辑零件", "删除零件"])
        
        # 添加零件
        with management_tabs[0]:
            st.subheader("➕ 添加新零件")
            
            with st.container():
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    part_number = st.text_input("零件编号", placeholder="请输入零件编号", key="add_part_number")
                    part_name = st.text_input("零件名称", placeholder="请输入零件名称", key="add_part_name")
                with col2:
                    operator = st.text_input("操作员", value=st.session_state.user['username'], disabled=True, key="add_operator")
                
                description = st.text_area("描述信息", placeholder="请输入零件描述信息", key="add_description")
                
                # 图片上传
                uploaded_image = st.file_uploader("上传零件图片", type=['png', 'jpg', 'jpeg'], key="add_image")
                
                if st.button("添加零件", type="primary", key="add_part_btn"):
                    if not part_number or not part_name or not description:
                        st.markdown('<div class="error-message">⚠️ 请填写完整信息！</div>', unsafe_allow_html=True)
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
            st.subheader("✏️ 编辑零件信息")
            
            parts = load_parts_data()
            if parts:
                selected_part = st.selectbox(
                    "选择要编辑的零件",
                    parts,
                    format_func=lambda x: f"{x['part_number']} - {x['part_name']}",
                    key="edit_part_select"
                )
                
                if selected_part:
                    with st.container():
                        st.markdown('<div class="form-container">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_part_number = st.text_input("零件编号", value=selected_part['part_number'], key="edit_part_number")
                            new_part_name = st.text_input("零件名称", value=selected_part['part_name'], key="edit_part_name")
                        with col2:
                            new_operator = st.text_input("操作员", value=st.session_state.user['username'], disabled=True, key="edit_operator")
                        
                        new_description = st.text_area("描述信息", value=selected_part['description'], key="edit_description")
                        
                        # 显示当前图片
                        if selected_part.get('image'):
                            st.image(f"data:image/jpeg;base64,{selected_part['image']}", caption="当前图片", width=200)
                        
                        # 新图片上传（可选）
                        new_image = st.file_uploader("上传新图片（可选）", type=['png', 'jpg', 'jpeg'], key="edit_image")
                        
                        if st.button("更新零件", type="primary", key="update_part_btn"):
                            if not new_part_number or not new_part_name or not new_description:
                                st.markdown('<div class="error-message">⚠️ 请填写完整信息！</div>', unsafe_allow_html=True)
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
                st.info("暂无零件数据。")
        
        # 删除零件
        with management_tabs[2]:
            st.subheader("🗑️ 删除零件")
            
            parts = load_parts_data()
            if parts:
                selected_part = st.selectbox(
                    "选择要删除的零件",
                    parts,
                    format_func=lambda x: f"{x['part_number']} - {x['part_name']}",
                    key="delete_part_select"
                )
                
                if selected_part:
                    st.warning(f"您即将删除以下零件：")
                    st.write(f"零件编号: {selected_part['part_number']}")
                    st.write(f"零件名称: {selected_part['part_name']}")
                    st.write(f"描述: {selected_part['description']}")
                    st.write(f"操作员: {selected_part['operator']}")
                    st.write(f"创建时间: {selected_part['created_time']}")
                    
                    if selected_part.get('image'):
                        st.image(f"data:image/jpeg;base64,{selected_part['image']}", caption="零件图片", width=200)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("确认删除", type="secondary", key="confirm_delete_part"):
                            if delete_part(selected_part['id']):
                                st.markdown('<div class="success-message">✅ 零件删除成功！</div>', unsafe_allow_html=True)
                                st.rerun()
                            else:
                                st.markdown('<div class="error-message">❌ 零件删除失败！</div>', unsafe_allow_html=True)
                    with col2:
                        if st.button("取消删除", key="cancel_delete_part"):
                            st.rerun()
            else:
                st.info("暂无零件数据。")
    
    elif menu == "零件查询":
        # 所有用户都可以查询零件
        st.header("🔍 零件查询")
        
        # 搜索选项
        search_tabs = st.tabs(["搜索零件", "浏览所有零件"])
        
        # 搜索零件
        with search_tabs[0]:
            st.subheader("🔍 搜索零件")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                search_query = st.text_input("搜索关键词", placeholder="输入零件编号、名称或描述信息", key="search_input")
            with col2:
                search_type = st.selectbox(
                    "搜索类型",
                    ["all", "part_number", "description"],
                    format_func=lambda x: {"all": "全部", "part_number": "零件编号", "description": "描述信息"}[x],
                    key="search_type"
                )
            
            if st.button("🔍 搜索", type="primary", key="search_btn"):
                if search_query:
                    results = search_parts(search_query, search_type)
                    if results:
                        st.success(f"找到 {len(results)} 个匹配的零件")
                        
                        # 显示搜索结果
                        for part in results:
                            with st.container():
                                st.markdown(f"""
                                <div class="report-card">
                                    <div class="report-header">
                                        <div class="report-title">{part['part_number']} - {part['part_name']}</div>
                                    </div>
                                    <p><strong>描述:</strong> {part['description']}</p>
                                    <p><strong>操作员:</strong> {part['operator']}</p>
                                    <p><strong>创建时间:</strong> {part['created_time']}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # 显示图片
                                if part.get('image'):
                                    st.image(f"data:image/jpeg;base64,{part['image']}", caption="零件图片", width=300)
                                
                                st.markdown("---")
                    else:
                        st.warning("未找到匹配的零件")
                else:
                    st.warning("请输入搜索关键词")
        
        # 浏览所有零件
        with search_tabs[1]:
            st.subheader("📋 浏览所有零件")
            
            parts = load_parts_data()
            if parts:
                # 统计信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总零件数", len(parts))
                with col2:
                    st.metric("操作员数", len(set(part['operator'] for part in parts)))
                with col3:
                    st.metric("有图片的零件", len([part for part in parts if part.get('image')]))
                
                # 显示所有零件
                for part in parts:
                    with st.container():
                        st.markdown(f"""
                        <div class="report-card">
                            <div class="report-header">
                                <div class="report-title">{part['part_number']} - {part['part_name']}</div>
                            </div>
                            <p><strong>描述:</strong> {part['description']}</p>
                            <p><strong>操作员:</strong> {part['operator']}</p>
                            <p><strong>创建时间:</strong> {part['created_time']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 显示图片
                        if part.get('image'):
                            st.image(f"data:image/jpeg;base64,{part['image']}", caption="零件图片", width=300)
                        
                        st.markdown("---")
                
                # 导出功能
                if parts:
                    # 转换为DataFrame用于导出
                    df_data = []
                    for part in parts:
                        df_data.append({
                            '零件编号': part['part_number'],
                            '零件名称': part['part_name'],
                            '描述信息': part['description'],
                            '操作员': part['operator'],
                            '创建时间': part['created_time']
                        })
                    
                    df = pd.DataFrame(df_data)
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 导出所有零件数据(CSV)",
                        data=csv,
                        file_name=f"零件数据库_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("暂无零件数据。")
    
# 移除旧的数据查询功能，已被零件查询替代
    
    # 页脚
    st.markdown("---")
    st.markdown("©智库zicus-ai| 技术支持：RBCC-phrase3-Team12-蔡伟")

def require_admin():
    """检查用户是否为管理员"""
    if 'user' not in st.session_state or st.session_state.user.get('role') != 'admin':
        st.error("⚠️ 权限不足！此功能需要管理员权限。")
        st.info("请使用管理员账号登录。")
        return False
    return True

if __name__ == "__main__":
    main()
