#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能打包数字化系统 - 功能演示脚本
演示报表管理和数据管理的各项功能
"""

import os
import json
import pandas as pd
import datetime

def create_demo_data():
    """创建演示数据"""
    print("🚀 创建演示数据...")
    
    # 确保目录存在
    os.makedirs("dataset/reports", exist_ok=True)
    
    # 创建示例报表
    demo_reports = [
        {
            "id": 1,
            "name": "生产线A零件管理",
            "description": "管理生产线A的零件库存和扫描记录",
            "creator": "张三",
            "created_time": "2024-01-15 09:00:00",
            "last_modified": "2024-01-15 09:00:00"
        },
        {
            "id": 2,
            "name": "生产线B零件管理",
            "description": "管理生产线B的零件库存和扫描记录",
            "creator": "李四",
            "created_time": "2024-01-15 10:00:00",
            "last_modified": "2024-01-15 10:00:00"
        },
        {
            "id": 3,
            "name": "仓库库存管理",
            "description": "管理仓库的零件库存和出入库记录",
            "creator": "王五",
            "created_time": "2024-01-15 11:00:00",
            "last_modified": "2024-01-15 11:00:00"
        }
    ]
    
    # 保存报表元数据
    with open("dataset/reports.json", "w", encoding="utf-8") as f:
        json.dump(demo_reports, f, ensure_ascii=False, indent=2)
    
    print("✅ 报表元数据创建完成")
    
    # 为每个报表创建示例数据
    for report in demo_reports:
        report_id = report["id"]
        
        # 创建示例零件数据
        demo_data = [
            {
                "id": 1,
                "part_name": f"零件A-{report_id}",
                "quantity": 1,
                "operator": "操作员1",
                "time": "2024-01-15 09:30:00"
            },
            {
                "id": 2,
                "part_name": f"零件B-{report_id}",
                "quantity": 1,
                "operator": "操作员2",
                "time": "2024-01-15 10:30:00"
            },
            {
                "id": 3,
                "part_name": f"零件C-{report_id}",
                "quantity": 1,
                "operator": "操作员3",
                "time": "2024-01-15 11:30:00"
            }
        ]
        
        # 保存到CSV文件
        df = pd.DataFrame(demo_data)
        csv_file = f"dataset/reports/{report_id}.csv"
        df.to_csv(csv_file, index=False)
        
        print(f"✅ 报表 {report['name']} 的示例数据创建完成")
    
    print("\n🎉 所有演示数据创建完成！")
    print("现在可以运行 'streamlit run app.py' 来查看系统功能")

def show_system_info():
    """显示系统信息"""
    print("=" * 60)
    print("📦 智能打包数字化系统 - 功能演示")
    print("=" * 60)
    print()
    print("🔧 系统架构:")
    print("  • 报表管理: 创建、查看、编辑、删除报表")
    print("  • 数据管理: 对每个报表进行增删改查操作")
    print("  • 数据存储: JSON (报表元数据) + CSV (报表数据)")
    print()
    print("📊 主要功能:")
    print("  1. 报表管理")
    print("     - 创建新报表 (名称、描述、创建人)")
    print("     - 查看报表列表和详细信息")
    print("     - 编辑报表属性")
    print("     - 删除报表及其所有数据")
    print()
    print("  2. 数据管理")
    print("     - 向指定报表添加零件记录")
    print("     - 查看报表数据 (统计信息 + 数据表)")
    print("     - 编辑记录信息")
    print("     - 删除指定记录")
    print("     - 导出CSV文件")
    print()
    print("💡 使用流程:")
    print("  1. 先创建报表 (报表管理)")
    print("  2. 再管理数据 (数据管理)")
    print("  3. 选择报表进行操作")
    print()
    print("🚀 启动命令: streamlit run app.py")
    print("🌐 访问地址: http://localhost:8501")
    print("=" * 60)

if __name__ == "__main__":
    show_system_info()
    
    # 询问是否创建演示数据
    response = input("\n是否创建演示数据？(y/n): ").lower().strip()
    if response in ['y', 'yes', '是']:
        create_demo_data()
    else:
        print("跳过演示数据创建")
    
    print("\n感谢使用智能打包数字化系统！")
