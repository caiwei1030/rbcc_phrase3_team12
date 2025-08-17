#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量CAD转换工具
将CAD JSON文件批量转换为2D和3D图片
"""

import os
import json
import subprocess
import time
from pathlib import Path
import argparse

def run_conversion_script(script_path, args):
    """运行转换脚本"""
    try:
        cmd = ['python', script_path] + args
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"✅ {script_path} 执行成功")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {script_path} 执行失败")
            if result.stderr:
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 执行 {script_path} 时出错: {e}")
        return False
    
    return True

def create_output_directories():
    """创建输出目录"""
    dirs = ['cad/images', 'cad/3d_images', 'cad/combined']
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 创建目录: {dir_path}")

def generate_2d_images(input_dir='cad/cadl', output_dir='cad/images'):
    """生成2D图片"""
    print("\n🖼️  开始生成2D图片...")
    
    args = [
        '--input', input_dir,
        '--output', output_dir,
        '--format', 'png'
    ]
    
    success = run_conversion_script('cad_to_image.py', args)
    
    if success:
        print(f"✅ 2D图片生成完成，保存在: {output_dir}")
    else:
        print("❌ 2D图片生成失败")
    
    return success

def generate_3d_images(input_dir='cad/cadl', output_dir='cad/3d_images', style='extruded'):
    """生成3D图片"""
    print(f"\n🎯 开始生成3D图片 (样式: {style})...")
    
    args = [
        '--input', input_dir,
        '--output', output_dir,
        '--style', style,
        '--height', '100'
    ]
    
    success = run_conversion_script('cad_3d_visualizer.py', args)
    
    if success:
        print(f"✅ 3D图片生成完成，保存在: {output_dir}")
    else:
        print("❌ 3D图片生成失败")
    
    return success

def create_combined_view(input_dir='cad/cadl', output_dir='cad/combined'):
    """创建组合视图（2D+3D并排显示）"""
    print("\n🔄 开始创建组合视图...")
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        from pathlib import Path
        
        # 获取所有JSON文件
        json_files = list(Path(input_dir).glob("*.json"))
        
        if not json_files:
            print("❌ 没有找到JSON文件")
            return False
        
        print(f"📁 找到 {len(json_files)} 个文件，开始创建组合视图...")
        
        for json_file in json_files:
            try:
                # 检查对应的图片文件是否存在
                img_2d = Path('cad/images') / f"{json_file.stem}.png"
                img_3d = Path('cad/3d_images') / f"{json_file.stem}_3d.png"
                
                if not img_2d.exists() or not img_3d.exists():
                    print(f"⚠️  跳过 {json_file.name} - 缺少对应的图片文件")
                    continue
                
                # 创建组合图片
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
                
                # 加载2D图片
                img_2d_data = mpimg.imread(str(img_2d))
                ax1.imshow(img_2d_data)
                ax1.set_title(f'2D视图 - {json_file.stem}', fontsize=14, fontweight='bold')
                ax1.axis('off')
                
                # 加载3D图片
                img_3d_data = mpimg.imread(str(img_3d))
                ax2.imshow(img_3d_data)
                ax2.set_title(f'3D视图 - {json_file.stem}', fontsize=14, fontweight='bold')
                ax2.axis('off')
                
                # 保存组合图片
                output_file = Path(output_dir) / f"{json_file.stem}_combined.png"
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"✅ 创建组合视图: {output_file.name}")
                
            except Exception as e:
                print(f"❌ 处理 {json_file.name} 时出错: {e}")
                continue
        
        print(f"✅ 组合视图创建完成，保存在: {output_dir}")
        return True
        
    except ImportError:
        print("❌ 缺少必要的库，无法创建组合视图")
        return False
    except Exception as e:
        print(f"❌ 创建组合视图时出错: {e}")
        return False

def generate_summary_report(input_dir='cad/cadl'):
    """生成转换报告"""
    print("\n📊 生成转换报告...")
    
    try:
        # 统计文件数量
        json_files = list(Path(input_dir).glob("*.json"))
        img_2d_files = list(Path('cad/images').glob("*.png"))
        img_3d_files = list(Path('cad/3d_images').glob("*.png"))
        combined_files = list(Path('cad/combined').glob("*.png"))
        
        # 生成报告
        report = f"""
# CAD文件转换报告

## 文件统计
- 原始JSON文件: {len(json_files)} 个
- 生成的2D图片: {len(img_2d_files)} 个
- 生成的3D图片: {len(img_3d_files)} 个
- 组合视图: {len(combined_files)} 个

## 转换状态
- 2D转换成功率: {len(img_2d_files)/len(json_files)*100:.1f}%
- 3D转换成功率: {len(img_3d_files)/len(json_files)*100:.1f}%
- 组合视图成功率: {len(combined_files)/len(json_files)*100:.1f}%

## 文件列表
"""
        
        # 添加文件列表
        for json_file in json_files:
            report += f"- {json_file.name}\n"
        
        # 保存报告
        report_file = Path('cad/conversion_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ 转换报告已保存到: {report_file}")
        
        # 打印摘要
        print(f"\n📈 转换摘要:")
        print(f"   JSON文件: {len(json_files)} 个")
        print(f"   2D图片: {len(img_2d_files)} 个")
        print(f"   3D图片: {len(img_3d_files)} 个")
        print(f"   组合视图: {len(combined_files)} 个")
        
    except Exception as e:
        print(f"❌ 生成报告时出错: {e}")

def main():
    parser = argparse.ArgumentParser(description='批量CAD转换工具')
    parser.add_argument('--input', '-i', type=str, default='cad/cadl',
                        help='输入目录路径 (默认: cad/cadl)')
    parser.add_argument('--skip-2d', action='store_true',
                        help='跳过2D图片生成')
    parser.add_argument('--skip-3d', action='store_true',
                        help='跳过3D图片生成')
    parser.add_argument('--skip-combined', action='store_true',
                        help='跳过组合视图生成')
    parser.add_argument('--style', '-s', type=str, default='extruded',
                        choices=['extruded', 'wireframe'],
                        help='3D模型样式 (默认: extruded)')
    
    args = parser.parse_args()
    
    print("🚀 开始批量CAD转换...")
    print(f"📁 输入目录: {args.input}")
    print(f"🎯 3D样式: {args.style}")
    
    # 创建输出目录
    create_output_directories()
    
    start_time = time.time()
    
    # 生成2D图片
    if not args.skip_2d:
        success_2d = generate_2d_images(args.input)
    else:
        print("⏭️  跳过2D图片生成")
        success_2d = True
    
    # 生成3D图片
    if not args.skip_3d:
        success_3d = generate_3d_images(args.input, style=args.style)
    else:
        print("⏭️  跳过3D图片生成")
        success_3d = True
    
    # 创建组合视图
    if not args.skip_combined and success_2d and success_3d:
        success_combined = create_combined_view(args.input)
    else:
        print("⏭️  跳过组合视图生成")
        success_combined = True
    
    # 生成报告
    if success_2d or success_3d:
        generate_summary_report(args.input)
    
    # 计算总时间
    total_time = time.time() - start_time
    
    print(f"\n🎉 批量转换完成！")
    print(f"⏱️  总耗时: {total_time:.2f} 秒")
    
    if success_2d and success_3d and success_combined:
        print("✅ 所有转换任务都成功完成")
    else:
        print("⚠️  部分转换任务失败，请检查错误信息")

if __name__ == "__main__":
    main()
