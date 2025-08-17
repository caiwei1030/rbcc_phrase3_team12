#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CAD图片匹配功能
"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.search_service import _get_cad_image_path, _load_cad_image_as_base64, _enhance_part_with_cad_image

def test_cad_image_matching():
    """测试CAD图片匹配功能"""
    print("🔍 测试CAD图片匹配功能...")
    
    # 测试数据
    test_parts = [
        {
            "part_number": "rectangular_plate_with_hole",
            "source_file": "rectangular_plate_with_hole.json",
            "description": "测试零件1"
        },
        {
            "part_number": "concentric_circles",
            "source_file": "concentric_circles.json", 
            "description": "测试零件2"
        },
        {
            "part_number": "square_plate",
            "source_file": "square_plate.json",
            "description": "测试零件3"
        },
        {
            "part_number": "nonexistent_part",
            "source_file": "nonexistent.json",
            "description": "不存在的零件"
        }
    ]
    
    print("\n📁 检查CAD图片目录...")
    cad_images_dir = "cad/cad/images"
    if os.path.exists(cad_images_dir):
        print(f"✅ CAD图片目录存在: {cad_images_dir}")
        image_files = [f for f in os.listdir(cad_images_dir) if f.endswith('.png')]
        print(f"📸 找到 {len(image_files)} 个PNG图片文件")
        if image_files:
            print(f"   示例文件: {image_files[:5]}")
    else:
        print(f"❌ CAD图片目录不存在: {cad_images_dir}")
        return
    
    print("\n🔍 测试图片路径查找...")
    for part in test_parts:
        part_id = part["part_number"]
        source_file = part["source_file"]
        
        print(f"\n--- 测试零件: {part_id} ---")
        print(f"   源文件: {source_file}")
        
        # 测试图片路径查找
        image_path = _get_cad_image_path(part_id, source_file)
        if image_path:
            print(f"   ✅ 找到图片: {image_path}")
            
            # 测试图片加载
            try:
                img_base64 = _load_cad_image_as_base64(image_path)
                if img_base64:
                    print(f"   ✅ 图片加载成功，base64长度: {len(img_base64)}")
                else:
                    print(f"   ❌ 图片加载失败")
            except Exception as e:
                print(f"   ❌ 图片加载异常: {e}")
        else:
            print(f"   ❌ 未找到对应图片")
    
    print("\n🔧 测试零件数据增强...")
    for part in test_parts:
        print(f"\n--- 增强零件: {part['part_number']} ---")
        
        # 复制测试数据
        test_part = part.copy()
        
        # 增强零件数据
        enhanced_part = _enhance_part_with_cad_image(test_part)
        
        print(f"   是否有CAD图片: {enhanced_part.get('has_cad_image', False)}")
        if enhanced_part.get('has_cad_image'):
            print(f"   CAD图片路径: {enhanced_part.get('cad_image_path', 'N/A')}")
            print(f"   图片base64长度: {len(enhanced_part.get('cad_image', ''))}")
        else:
            print(f"   未找到CAD图片")
    
    print("\n✅ 测试完成!")

def test_specific_part():
    """测试特定零件的图片匹配"""
    print("\n🎯 测试特定零件图片匹配...")
    
    # 测试一个已知存在的零件
    test_part = {
        "part_number": "rectangular_plate_with_hole",
        "source_file": "rectangular_plate_with_hole.json",
        "description": "带孔的矩形板"
    }
    
    print(f"测试零件: {test_part['part_number']}")
    
    # 查找图片路径
    image_path = _get_cad_image_path(test_part['part_number'], test_part['source_file'])
    print(f"图片路径: {image_path}")
    
    if image_path and os.path.exists(image_path):
        print(f"✅ 图片文件存在")
        
        # 获取文件大小
        file_size = os.path.getsize(image_path)
        print(f"文件大小: {file_size} 字节")
        
        # 尝试加载图片
        img_base64 = _load_cad_image_as_base64(image_path)
        if img_base64:
            print(f"✅ 图片加载成功")
            print(f"Base64长度: {len(img_base64)}")
        else:
            print(f"❌ 图片加载失败")
    else:
        print(f"❌ 图片文件不存在")

if __name__ == "__main__":
    print("🚀 开始测试CAD图片匹配功能...")
    
    try:
        test_cad_image_matching()
        test_specific_part()
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🏁 所有测试完成!")
