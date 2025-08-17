import json
import os
import datetime
from config import REPORTS_FILE, PARTS_FILE

# --- Reports ---
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


# --- Parts ---
def load_parts_data():
    """加载零件数据库"""
    if os.path.exists(PARTS_FILE):
        try:
            with open(PARTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_parts_data(parts):
    """保存零件数据库"""
    os.makedirs(os.path.dirname(PARTS_FILE), exist_ok=True)
    with open(PARTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(parts, f, ensure_ascii=False, indent=2)

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
            if image_data:
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
            if (query in part['part_number'].lower() or
                    query in part['part_name'].lower() or
                    query in part['description'].lower()):
                results.append(part)
        elif search_type == "part_number":
            if query in part['part_number'].lower():
                results.append(part)
        elif search_type == "description":
            if query in part['description'].lower():
                results.append(part)

    return results
