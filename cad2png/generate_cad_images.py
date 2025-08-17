#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速生成CAD图片脚本
一键生成所有CAD图片并验证路径正确性
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    current_dir = Path.cwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查是否在正确的目录
    if (current_dir / 'cad_to_image.py').exists():
        print("✅ 在cad目录中")
        base_dir = current_dir.parent
        input_dir = 'cadl'
        output_dir = 'cad/images'
    elif (current_dir / 'cad').exists():
        print("✅ 在项目根目录中")
        base_dir = current_dir
        input_dir = 'cad/cadl'
        output_dir = 'cad/cad/images'
    else:
        print("❌ 无法确定目录结构")
        return False, None, None, None
    
    print(f"项目根目录: {base_dir}")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    # 检查输入目录是否存在
    if not Path(input_dir).exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return False, None, None, None
    
    print("✅ 环境检查通过")
    return True, base_dir, input_dir, output_dir

def generate_cad_images(input_dir, output_dir):
    """生成CAD图片"""
    print(f"\n🎨 开始生成CAD图片...")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    
    # 检查输入目录中的JSON文件数量
    json_files = list(Path(input_dir).glob("*.json"))
    if not json_files:
        print("❌ 输入目录中没有找到JSON文件")
        return False
    
    print(f"📁 找到 {len(json_files)} 个JSON文件")
    
    # 运行CAD转图片工具
    try:
        cmd = [
            sys.executable, 'cad_to_image.py',
            '--input', input_dir,
            '--output', output_dir,
            '--fix-paths'
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("⏳ 正在生成图片，请稍候...")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ CAD图片生成完成!")
            print("输出信息:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    print(f"  {line}")
            return True
        else:
            print("❌ CAD图片生成失败")
            print(f"错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ 命令执行超时")
        return False
    except Exception as e:
        print(f"❌ 执行过程中发生错误: {e}")
        return False

def verify_output(output_dir):
    """验证输出结果"""
    print(f"\n🔍 验证输出结果...")
    print(f"输出目录: {output_dir}")
    
    # 检查输出目录是否存在
    if not Path(output_dir).exists():
        print(f"❌ 输出目录不存在: {output_dir}")
        return False
    
    # 统计生成的图片文件
    png_files = list(Path(output_dir).glob("*.png"))
    jpg_files = list(Path(output_dir).glob("*.jpg"))
    pdf_files = list(Path(output_dir).glob("*.pdf"))
    svg_files = list(Path(output_dir).glob("*.svg"))
    
    total_images = len(png_files) + len(jpg_files) + len(pdf_files) + len(svg_files)
    
    print(f"📊 生成的图片统计:")
    print(f"  PNG文件: {len(png_files)}")
    print(f"  JPG文件: {len(jpg_files)}")
    print(f"  PDF文件: {len(pdf_files)}")
    print(f"  SVG文件: {len(svg_files)}")
    print(f"  总计: {total_images}")
    
    if total_images == 0:
        print("❌ 没有生成任何图片文件")
        return False
    
    # 显示部分图片文件
    print(f"\n📸 部分生成的图片:")
    for i, img_file in enumerate(png_files[:5]):
        print(f"  {i+1}. {img_file.name}")
    if len(png_files) > 5:
        print(f"  ... 还有 {len(png_files) - 5} 个文件")
    
    print("✅ 输出验证通过")
    return True

def test_ai_integration():
    """测试AI集成功能"""
    print(f"\n🤖 测试AI集成功能...")
    
    # 检查AI检索系统是否能找到图片
    try:
        # 导入AI检索模块进行测试
        sys.path.append(str(Path.cwd().parent))
        
        from services.search_service import _get_cad_image_path
        
        # 测试几个示例零件
        test_cases = [
            ("rectangular_plate_with_hole", "rectangular_plate_with_hole.json"),
            ("concentric_circles", "concentric_circles.json"),
            ("square_plate", "square_plate.json")
        ]
        
        print("🔍 测试AI检索系统图片查找...")
        for part_id, source_file in test_cases:
            image_path = _get_cad_image_path(part_id, source_file)
            if image_path and Path(image_path).exists():
                print(f"  ✅ {part_id}: 找到图片 {image_path}")
            else:
                print(f"  ❌ {part_id}: 未找到图片")
        
        print("✅ AI集成测试完成")
        return True
        
    except ImportError as e:
        print(f"⚠️  无法导入AI检索模块: {e}")
        print("   请确保在正确的目录中运行此脚本")
        return False
    except Exception as e:
        print(f"❌ AI集成测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 CAD图片快速生成工具")
    print("=" * 60)
    
    # 检查环境
    env_ok, base_dir, input_dir, output_dir = check_environment()
    if not env_ok:
        print("\n❌ 环境检查失败，请检查目录结构")
        return
    
    # 生成CAD图片
    if not generate_cad_images(input_dir, output_dir):
        print("\n❌ CAD图片生成失败")
        return
    
    # 验证输出
    if not verify_output(output_dir):
        print("\n❌ 输出验证失败")
        return
    
    # 测试AI集成
    test_ai_integration()
    
    # 输出成功信息
    print(f"\n{'='*60}")
    print("🎉 CAD图片生成完成！")
    print(f"📁 图片保存在: {output_dir}")
    print(f"🔍 总数: {len(list(Path(output_dir).glob('*.png')))} 个PNG文件")
    
    print(f"\n💡 现在您可以:")
    print(f"   1. 在Streamlit应用中使用AI查询功能")
    print(f"   2. 查看自动匹配的CAD设计图")
    print(f"   3. 体验完整的零件搜索和显示功能")
    
    print(f"\n🧪 建议运行测试脚本验证功能:")
    print(f"   python test_cad_image_matching.py")
    print(f"   python demo_cad_integration.py")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
