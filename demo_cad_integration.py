#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示CAD图片集成功能
展示如何在AI检索结果中自动匹配和显示CAD图片
"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.search_service import _enhance_part_with_cad_image

def demo_cad_image_integration():
    """演示CAD图片集成功能"""
    print("🎯 演示CAD图片集成功能")
    print("=" * 50)
    
    # 模拟AI检索结果
    mock_search_results = [
        {
            "part_number": "rectangular_plate_with_hole",
            "source_file": "rectangular_plate_with_hole.json",
            "part_name": "带孔矩形板",
            "description": "该零件是一个矩形板状结构，由四条直线围合而成，形成一个长714.29单位、宽1000单位的矩形轮廓。矩形中心位置存在一个圆形特征，圆心位于(214.29, 285.71)，半径178.57单位。",
            "score": 0.95,
            "relevance_reason": "高相似度匹配"
        },
        {
            "part_number": "concentric_circles",
            "source_file": "concentric_circles.json",
            "part_name": "同心圆零件",
            "description": "该CAD模型由两个同心圆构成，圆心位于(500.0, 500.0)。外圆Circle0半径为500.0，内圆Circle1半径为449.99999999999994。",
            "score": 0.88,
            "relevance_reason": "几何特征匹配"
        },
        {
            "part_number": "square_plate",
            "source_file": "square_plate.json",
            "part_name": "方形板",
            "description": "该零件是一个矩形板，由四条直线组成，形成封闭轮廓。其中两条水平线长度均为0.05单位，两条垂直线长度均为0.05单位，构成一个正方形几何结构。",
            "score": 0.82,
            "relevance_reason": "形状特征匹配"
        },
        {
            "part_number": "nonexistent_part",
            "source_file": "nonexistent.json",
            "part_name": "不存在的零件",
            "description": "这是一个用于测试的虚拟零件，实际不存在对应的CAD图片。",
            "score": 0.45,
            "relevance_reason": "低相似度匹配"
        }
    ]
    
    print(f"🔍 模拟AI检索到 {len(mock_search_results)} 个零件")
    print()
    
    # 处理每个检索结果，集成CAD图片
    enhanced_results = []
    for i, part in enumerate(mock_search_results, 1):
        print(f"📋 处理零件 {i}: {part['part_name']}")
        print(f"   零件编号: {part['part_number']}")
        print(f"   相似度: {part['score']:.2f}")
        print(f"   匹配原因: {part['relevance_reason']}")
        
        # 增强零件数据，添加CAD图片信息
        enhanced_part = _enhance_part_with_cad_image(part)
        enhanced_results.append(enhanced_part)
        
        if enhanced_part.get('has_cad_image'):
            print(f"   ✅ 找到对应CAD图片")
            print(f"   📁 图片路径: {enhanced_part.get('cad_image_path', 'N/A')}")
            print(f"   🖼️  图片大小: {len(enhanced_part.get('cad_image', ''))} 字符 (base64)")
        else:
            print(f"   ❌ 未找到对应CAD图片")
        
        print()
    
    # 统计结果
    print("📊 集成结果统计")
    print("-" * 30)
    total_parts = len(enhanced_results)
    parts_with_cad = len([p for p in enhanced_results if p.get('has_cad_image')])
    parts_without_cad = total_parts - parts_with_cad
    
    print(f"总零件数: {total_parts}")
    print(f"有CAD图片: {parts_with_cad} ({parts_with_cad/total_parts*100:.1f}%)")
    print(f"无CAD图片: {parts_without_cad} ({parts_without_cad/total_parts*100:.1f}%)")
    
    # 显示详细信息
    print("\n🔍 详细信息")
    print("-" * 30)
    for i, part in enumerate(enhanced_results, 1):
        print(f"\n{i}. {part['part_name']}")
        print(f"   零件编号: {part['part_number']}")
        print(f"   相似度: {part['score']:.2f}")
        
        if part.get('has_cad_image'):
            print(f"   🎨 CAD图片: ✅ 可用")
            print(f"   📁 路径: {part['cad_image_path']}")
            print(f"   📏 大小: {len(part['cad_image'])} 字符")
        else:
            print(f"   🎨 CAD图片: ❌ 不可用")
            print(f"   💡 建议: 检查零件编号和源文件是否匹配")
    
    print("\n✅ 演示完成!")
    return enhanced_results

def demo_ui_display_simulation():
    """模拟UI显示效果"""
    print("\n🖥️  模拟UI显示效果")
    print("=" * 50)
    
    # 获取增强后的结果
    enhanced_results = demo_cad_image_integration()
    
    print("\n📱 在Streamlit UI中的显示效果:")
    print("-" * 40)
    
    for i, part in enumerate(enhanced_results, 1):
        print(f"\n🏷️  零件 {i}: {part['part_name']}")
        print(f"   编号: {part['part_number']}")
        print(f"   相似度: {part['score']:.2f}")
        print(f"   描述: {part['description'][:50]}...")
        
        if part.get('has_cad_image'):
            print(f"   🎨 CAD设计图: [图片显示区域]")
            print(f"   📁 图片路径: {part['cad_image_path']}")
            print(f"   🔍 详细信息: [可展开查看]")
        else:
            print(f"   🎨 CAD设计图: [无图片]")
        
        print(f"   📄 零件图片: [如果有的话]")
        print(f"   ---")
    
    print("\n💡 功能特点:")
    print("   • 自动匹配CAD图片")
    print("   • 支持多种图片格式")
    print("   • 智能路径查找")
    print("   • 错误处理和回退")
    print("   • 调试信息显示")

if __name__ == "__main__":
    print("🚀 开始演示CAD图片集成功能...")
    
    try:
        # 演示基本功能
        demo_cad_image_integration()
        
        # 演示UI显示效果
        demo_ui_display_simulation()
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 演示完成!")
    print("\n💡 现在您可以在Streamlit应用中看到:")
    print("   1. AI检索结果自动匹配CAD图片")
    print("   2. 图片和文字信息同时显示")
    print("   3. 详细的调试信息")
    print("   4. 优雅的错误处理")
