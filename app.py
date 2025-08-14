import streamlit as st
import pandas as pd
import datetime
import os
import json
from PIL import Image
import base64
import hashlib
from cla import classify_part_from_b64

# 设置页面配置
st.set_page_config(
    page_title="智能打包核对数字化系统",
    page_icon="📦",
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
    }
    .watermark img {
        width: 80px;
        height: auto;
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

def register_user(username, password):
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
            return True
    return False

def load_report_data(report_id):
    """加载指定报表的数据"""
    data_file = os.path.join(DATA_DIR, f"{report_id}.csv")
    if os.path.exists(data_file):
        try:
            return pd.read_csv(data_file)
        except:
            return pd.DataFrame(columns=['id', 'part_name', 'quantity', 'operator', 'time'])
    return pd.DataFrame(columns=['id', 'part_name', 'quantity', 'operator', 'time'])

def save_report_data(report_id, df):
    """保存指定报表的数据"""
    data_file = os.path.join(DATA_DIR, f"{report_id}.csv")
    df.to_csv(data_file, index=False)

def get_next_report_id(reports):
    """获取下一个报表ID"""
    if not reports:
        return 1
    return max(report['id'] for report in reports) + 1

def get_next_record_id(df):
    """获取下一个记录ID"""
    if df.empty:
        return 1
    return df['id'].max() + 1

def create_report(report_name, description, creator):
    """创建新报表"""
    reports = load_reports()
    new_report = {
        'id': get_next_report_id(reports),
        'name': report_name,
        'description': description,
        'creator': creator,
        'created_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'last_modified': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    reports.append(new_report)
    save_reports(reports)
    
    # 创建空的CSV文件
    df = pd.DataFrame(columns=['id', 'part_name', 'quantity', 'operator', 'time'])
    save_report_data(new_report['id'], df)
    return True

def delete_report(report_id):
    """删除报表"""
    reports = load_reports()
    reports = [r for r in reports if r['id'] != report_id]
    save_reports(reports)
    
    # 删除对应的CSV文件
    data_file = os.path.join(DATA_DIR, f"{report_id}.csv")
    if os.path.exists(data_file):
        os.remove(data_file)
    return True

def update_report(report_id, name, description):
    """更新报表信息"""
    reports = load_reports()
    for report in reports:
        if report['id'] == report_id:
            report['name'] = name
            report['description'] = description
            report['last_modified'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_reports(reports)
    return True

def add_record_to_report(report_id, part_name, operator):
    """向指定报表添加记录"""
    df = load_report_data(report_id)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 规范化零件名，避免前后空格导致重复
    normalized_part_name = str(part_name).strip()
    if 'part_name' in df.columns:
        mask = df['part_name'].astype(str).str.strip() == normalized_part_name
    else:
        mask = pd.Series([False] * len(df))
    
    if mask.any():
        # 若已存在相同零件名称，则在现有表项上数量+1，并更新操作员与时间
        target_index = df[mask].index[-1]
        try:
            current_quantity = int(df.at[target_index, 'quantity']) if pd.notna(df.at[target_index, 'quantity']) else 0
        except Exception:
            current_quantity = 0
        df.at[target_index, 'quantity'] = current_quantity + 1
        df.at[target_index, 'operator'] = operator
        df.at[target_index, 'time'] = current_time
        save_report_data(report_id, df)
    else:
        # 若不存在，则新增一条记录
        next_id = get_next_record_id(df)
        new_record = {
            'id': next_id,
            'part_name': normalized_part_name,
            'quantity': 1,
            'operator': operator,
            'time': current_time
        }
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        save_report_data(report_id, df)
    
    # 更新报表的最后修改时间
    reports = load_reports()
    for report in reports:
        if report['id'] == report_id:
            report['last_modified'] = current_time
            break
    save_reports(reports)
    return True

def delete_record_from_report(report_id, record_id):
    """从指定报表删除记录"""
    df = load_report_data(report_id)
    df = df[df['id'] != record_id]
    save_report_data(report_id, df)
    
    # 更新报表的最后修改时间
    reports = load_reports()
    for report in reports:
        if report['id'] == report_id:
            report['last_modified'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_reports(reports)
    return True

def update_record_in_report(report_id, record_id, part_name, quantity, operator):
    """更新指定报表中的记录"""
    df = load_report_data(report_id)
    mask = df['id'] == record_id
    if mask.any():
        df.loc[mask, 'part_name'] = part_name
        df.loc[mask, 'quantity'] = quantity
        df.loc[mask, 'operator'] = operator
        df.loc[mask, 'time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_report_data(report_id, df)
        
        # 更新报表的最后修改时间
        reports = load_reports()
        for report in reports:
            if report['id'] == report_id:
                report['last_modified'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        save_reports(reports)
        return True
    return False

def main():
    # 水印图片
    st.markdown("""
    <div class="watermark">
        <img src="data:image/png;base64,{}" alt="Logo">
    </div>
    """.format(base64.b64encode(open("imgs/logo1.png", "rb").read()).decode()), unsafe_allow_html=True)
    
    # 主标题
    st.markdown('<h1 class="main-header">📦 智能打包核对数字化系统</h1>', unsafe_allow_html=True)
    
    # 确保数据目录存在
    ensure_data_directory()
    
    # 侧边栏 - 账号管理
    if 'user' not in st.session_state:
        st.session_state.user = None

    st.sidebar.title("账号")
    if st.session_state.user:
        st.sidebar.success(f"已登录：{st.session_state.user['username']}")
        if st.sidebar.button("注销"):
            st.session_state.user = None
            st.rerun()
    else:
        auth_tabs = st.sidebar.tabs(["登录", "注册"])
        with auth_tabs[0]:
            login_username = st.text_input("用户名", key="login_username")
            login_password = st.text_input("密码", type="password", key="login_password")
            if st.button("登录", key="login_button"):
                if authenticate_user(login_username, login_password):
                    st.session_state.user = { 'username': login_username.strip() }
                    st.sidebar.success("登录成功")
                    st.rerun()
                else:
                    st.sidebar.error("用户名或密码不正确")
        with auth_tabs[1]:
            reg_username = st.text_input("新用户名", key="reg_username")
            reg_password = st.text_input("新密码", type="password", key="reg_password")
            reg_password2 = st.text_input("确认密码", type="password", key="reg_password2")
            if st.button("注册", key="register_button"):
                if reg_password != reg_password2:
                    st.sidebar.error("两次输入的密码不一致")
                else:
                    ok, msg = register_user(reg_username, reg_password)
                    if ok:
                        st.sidebar.success(msg)
                    else:
                        st.sidebar.error(msg)

    # 未登录则不展示功能菜单与主界面功能
    if not st.session_state.user:
        st.header("请先登录")
        st.info("登录后将显示报表管理与数据管理功能。请在左侧侧边栏完成登录或注册。")
        st.markdown("---")
        st.markdown("© 智能打包数字化系统 | 技术支持：RBCC-phrase3-Team5-蔡伟")
        return

    # 侧边栏 - 功能菜单（仅登录后可见）
    st.sidebar.title("功能菜单")
    menu = st.sidebar.selectbox(
        "选择功能",
        ["报表管理", "数据管理"]
    )
    
    if menu == "报表管理":
        st.header("📋 报表管理")
        
        # 创建新报表
        with st.expander("➕ 创建新报表", expanded=False):
            with st.container():
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    report_name = st.text_input("报表名称", placeholder="请输入报表名称")
                with col2:
                    if st.session_state.user:
                        st.text_input("创建人", value=st.session_state.user['username'], disabled=True, key="creator_view")
                        creator = st.session_state.user['username']
                    else:
                        creator = st.text_input("创建人", placeholder="请先登录或手动输入创建人姓名")
                
                description = st.text_area("报表描述", placeholder="请输入报表描述")
                
                if st.button("创建报表", type="primary"):
                    if not st.session_state.user:
                        st.markdown('<div class="error-message">⚠️ 请先登录再创建报表。</div>', unsafe_allow_html=True)
                    elif report_name and creator:
                        if create_report(report_name, description, creator):
                            st.markdown('<div class="success-message">✅ 报表创建成功！</div>', unsafe_allow_html=True)
                            st.balloons()
                            st.rerun()
                        else:
                            st.markdown('<div class="error-message">❌ 报表创建失败！</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="error-message">⚠️ 请填写完整信息！</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 显示报表列表
        st.subheader("📊 报表列表")
        reports = load_reports()
        
        if reports:
            for report in reports:
                with st.container():
                    st.markdown(f"""
                    <div class="report-card">
                        <div class="report-header">
                            <div class="report-title">{report['name']}</div>
                            <div class="report-actions">
                                <button onclick="editReport({report['id']})" class="btn btn-sm btn-outline-primary">编辑</button>
                                <button onclick="deleteReport({report['id']})" class="btn btn-sm btn-outline-danger">删除</button>
                            </div>
                        </div>
                        <p><strong>描述:</strong> {report['description']}</p>
                        <p><strong>创建人:</strong> {report['creator']}</p>
                        <p><strong>创建时间:</strong> {report['created_time']}</p>
                        <p><strong>最后修改:</strong> {report['last_modified']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 编辑报表信息
                    if st.button(f"编辑报表信息", key=f"edit_{report['id']}"):
                        st.session_state.editing_report = report['id']
                    
                    if st.session_state.get('editing_report') == report['id']:
                        with st.container():
                            st.markdown('<div class="form-container">', unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                new_name = st.text_input("报表名称", value=report['name'], key=f"name_{report['id']}")
                            with col2:
                                new_description = st.text_area("报表描述", value=report['description'], key=f"desc_{report['id']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("保存", key=f"save_{report['id']}"):
                                    if new_name:
                                        if update_report(report['id'], new_name, new_description):
                                            st.markdown('<div class="success-message">✅ 报表更新成功！</div>', unsafe_allow_html=True)
                                            st.rerun()
                                        else:
                                            st.markdown('<div class="error-message">❌ 报表更新失败！</div>', unsafe_allow_html=True)
                                    else:
                                        st.markdown('<div class="error-message">⚠️ 请填写报表名称！</div>', unsafe_allow_html=True)
                            with col2:
                                if st.button("取消", key=f"cancel_{report['id']}"):
                                    st.session_state.editing_report = None
                                    st.rerun()
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 删除报表确认
                    if st.button(f"删除报表", key=f"delete_{report['id']}"):
                        st.session_state.deleting_report = report['id']
                    
                    if st.session_state.get('deleting_report') == report['id']:
                        st.warning(f"您即将删除报表：{report['name']}")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("确认删除", key=f"confirm_delete_{report['id']}"):
                                if delete_report(report['id']):
                                    st.markdown('<div class="success-message">✅ 报表删除成功！</div>', unsafe_allow_html=True)
                                    st.rerun()
                                else:
                                    st.markdown('<div class="error-message">❌ 报表删除失败！</div>', unsafe_allow_html=True)
                        with col2:
                            if st.button("取消删除", key=f"cancel_delete_{report['id']}"):
                                st.session_state.deleting_report = None
                                st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("暂无报表，请先创建报表。")
    
    elif menu == "数据管理":
        st.header("📝 数据管理")
        
        # 选择报表
        reports = load_reports()
        if not reports:
            st.warning("请先创建报表，然后才能管理数据。")
            return
        
        selected_report = st.selectbox(
            "选择要管理的报表",
            reports,
            format_func=lambda x: f"{x['name']} (ID: {x['id']})"
        )
        
        if selected_report:
            st.subheader(f"📊 {selected_report['name']} - 数据管理")
            
            # 子菜单
            data_submenu = st.tabs(["添加数据", "查看数据", "编辑数据", "删除数据"])
            
            # 添加数据
            with data_submenu[0]:
                st.header("➕ 添加新数据")
                
                # 拍照识别零件
                st.subheader("📸 拍照识别零件")
                st.info("请拍照上传零件图片，系统将自动识别零件名称")
                
                # 定义零件类别选项（可以根据实际需要修改）
                part_options = [
                    "螺丝", "螺母", "垫片", "轴承", "齿轮", "弹簧", "销子", "键", "联轴器",
                    "皮带", "链条", "电机", "传感器", "控制器", "开关", "连接器", "线缆",
                    "管道", "阀门", "泵", "过滤器", "散热器", "风扇", "其他"
                ]
                
                # 拍照输入
                camera_photo = st.camera_input("拍照识别零件", key="camera_photo")
                
                if camera_photo is not None:
                    # 显示拍照结果
                    st.image(camera_photo, caption="已拍照", use_column_width=True)
                    
                    # 转换为base64并调用识别API
                    if st.button("🔍 开始识别", key="recognize_btn"):
                        with st.spinner("正在识别零件..."):
                            try:
                                # 将拍照图片转换为base64
                                photo_bytes = camera_photo.getvalue()
                                photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
                                
                                # 调用识别API
                                recognized_part = classify_part_from_b64(photo_base64, part_options)
                                
                                if recognized_part and not recognized_part.startswith("API调用失败"):
                                    st.success(f"识别成功！零件名称：{recognized_part}")
                                    # 自动填充到表单中
                                    st.session_state.recognized_part_name = recognized_part
                                else:
                                    st.error(f"识别失败：{recognized_part}")
                            except Exception as e:
                                st.error(f"识别过程出错：{str(e)}")
                
                st.markdown("---")
                st.subheader("✏️ 手动输入零件信息")
                
                with st.container():
                    st.markdown('<div class="form-container">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        # 如果识别成功，自动填充零件名称
                        default_part_name = st.session_state.get('recognized_part_name', '')
                        part_name = st.text_input("零件名称", 
                                                value=default_part_name,
                                                placeholder="请输入零件名称或拍照识别", 
                                                key="add_part_name")
                    with col2:
                        if st.session_state.user:
                            st.text_input("扫描人员", value=st.session_state.user['username'], disabled=True, key="add_operator_view")
                        else:
                            st.text_input("扫描人员", value="未登录", disabled=True, key="add_operator_view_guest")
                    
                    if st.button("添加数据", type="primary", key="add_data_btn"):
                        if not st.session_state.user:
                            st.markdown('<div class="error-message">⚠️ 请先登录再添加数据。</div>', unsafe_allow_html=True)
                        elif part_name:
                            if add_record_to_report(selected_report['id'], part_name, st.session_state.user['username']):
                                st.markdown('<div class="success-message">✅ 数据添加成功！</div>', unsafe_allow_html=True)
                                st.balloons()
                                # 清除识别的零件名称，为下次添加做准备
                                if 'recognized_part_name' in st.session_state:
                                    del st.session_state.recognized_part_name
                                st.rerun()
                            else:
                                st.markdown('<div class="error-message">❌ 数据添加失败！</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="error-message">⚠️ 请填写完整信息！</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            # 查看数据
            with data_submenu[1]:
                st.header("📊 数据报表")
                
                df = load_report_data(selected_report['id'])
                if not df.empty:
                    # 统计信息
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("总记录数", len(df))
                    with col2:
                        st.metric("零件种类", df['part_name'].nunique())
                    with col3:
                        st.metric("总数量", df['quantity'].sum())
                    with col4:
                        st.metric("操作人员数", df['operator'].nunique())
                    
                    # 数据表格
                    st.markdown('<div class="data-table">', unsafe_allow_html=True)
                    st.dataframe(df, use_container_width=True)
                    
                    # 导出功能
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 导出CSV",
                        data=csv,
                        file_name=f"{selected_report['name']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("该报表暂无数据，请先添加数据。")
            
            # 编辑数据
            with data_submenu[2]:
                st.header("✏️ 编辑数据")
                
                df = load_report_data(selected_report['id'])
                if not df.empty:
                    # 选择要编辑的记录
                    selected_id = st.selectbox("选择要编辑的记录ID", df['id'].tolist(), key="edit_select")
                    
                    if selected_id:
                        record = df[df['id'] == selected_id].iloc[0]
                        
                        with st.container():
                            st.markdown('<div class="form-container">', unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                new_part_name = st.text_input("零件名称", value=record['part_name'], key="edit_part_name")
                                new_quantity = st.number_input("数量", value=int(record['quantity']), min_value=1, key="edit_quantity")
                            with col2:
                                new_operator = st.text_input("扫描人员", value=record['operator'], key="edit_operator")
                            
                            if st.button("更新数据", type="primary", key="update_data_btn"):
                                if new_part_name and new_operator:
                                    if update_record_in_report(selected_report['id'], selected_id, new_part_name, new_quantity, new_operator):
                                        st.markdown('<div class="success-message">✅ 数据更新成功！</div>', unsafe_allow_html=True)
                                        st.rerun()
                                    else:
                                        st.markdown('<div class="error-message">❌ 数据更新失败！</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div class="error-message">⚠️ 请填写完整信息！</div>', unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("该报表暂无数据可编辑。")
            
            # 删除数据
            with data_submenu[3]:
                st.header("🗑️ 删除数据")
                
                df = load_report_data(selected_report['id'])
                if not df.empty:
                    # 选择要删除的记录
                    selected_id = st.selectbox("选择要删除的记录ID", df['id'].tolist(), key="delete_select")
                    
                    if selected_id:
                        record = df[df['id'] == selected_id].iloc[0]
                        
                        st.warning(f"您即将删除以下记录：")
                        st.write(f"ID: {record['id']}")
                        st.write(f"零件名称: {record['part_name']}")
                        st.write(f"数量: {record['quantity']}")
                        st.write(f"扫描人员: {record['operator']}")
                        st.write(f"时间: {record['time']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("确认删除", type="secondary", key="confirm_delete_record"):
                                if delete_record_from_report(selected_report['id'], selected_id):
                                    st.markdown('<div class="success-message">✅ 数据删除成功！</div>', unsafe_allow_html=True)
                                    st.rerun()
                                else:
                                    st.markdown('<div class="error-message">❌ 数据删除失败！</div>', unsafe_allow_html=True)
                        with col2:
                            if st.button("取消删除", key="cancel_delete_record"):
                                st.rerun()
                else:
                    st.info("该报表暂无数据可删除。")
    
    # 页脚
    st.markdown("---")
    st.markdown("© 智能打包数字化系统 | 技术支持：RBCC-phrase3-Team5-蔡伟")

if __name__ == "__main__":
    main()
