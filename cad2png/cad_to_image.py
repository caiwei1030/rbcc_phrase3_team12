#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAD JSON文件转图片工具
将CAD文件中的JSON文件转换为PNG图片格式
"""

import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, Polygon, FancyBboxPatch
import numpy as np
from pathlib import Path
import argparse

class CADVisualizer:
    def __init__(self, canvas_size=(1000, 1000)):
        self.canvas_size = canvas_size
        self.fig, self.ax = plt.subplots(figsize=(12, 12))
        self.ax.set_xlim(0, canvas_size[0])
        self.ax.set_ylim(0, canvas_size[1])
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('CADmodel visualization', fontsize=16, fontweight='bold')
        
    def draw_primitive(self, primitive):
        """绘制基本几何图形"""
        if primitive['type'] == 'Circle':
            circle = Circle((primitive['xc'], primitive['yc']), 
                          primitive['r'], 
                          fill=False, 
                          edgecolor='blue', 
                          linewidth=2)
            self.ax.add_patch(circle)
            
            # 添加圆心标记
            self.ax.plot(primitive['xc'], primitive['yc'], 'ro', markersize=4)
            
        elif primitive['type'] == 'Line':
            x_start, y_start = primitive['xstart'], primitive['ystart']
            x_end, y_end = primitive['xend'], primitive['yend']
            
            self.ax.plot([x_start, x_end], [y_start, y_end], 
                        'b-', linewidth=2, solid_capstyle='round')
            
            # 添加端点标记
            self.ax.plot([x_start, x_end], [y_start, y_end], 'ro', markersize=4)
            
        elif primitive['type'] == 'Arc':
            # 简化为线段处理
            if 'xstart' in primitive and 'ystart' in primitive:
                x_start, y_start = primitive['xstart'], primitive['ystart']
                x_end, y_end = primitive['xend'], primitive['yend']
                self.ax.plot([x_start, x_end], [y_start, y_end], 
                            'g-', linewidth=2, linestyle='--')
                
        elif primitive['type'] == 'Point':
            self.ax.plot(primitive['x'], primitive['y'], 'ko', markersize=6)
    
    def draw_constraints(self, constraints):
        """绘制约束关系（用不同颜色表示）"""
        constraint_colors = {
            'Coincident': 'red',
            'Horizontal': 'orange',
            'Vertical': 'purple',
            'Parallel': 'brown',
            'Perpendicular': 'magenta'
        }
        
        for constraint in constraints:
            if constraint['type'] in constraint_colors:
                color = constraint_colors[constraint['type']]
                # 这里可以添加约束的可视化表示
                pass
    
    def draw_dimensions(self, dimensions):
        """绘制尺寸标注"""
        for dim in dimensions:
            if dim['type'] == 'Radius':
                # 半径标注
                pass
            elif dim['type'] == 'Linear':
                # 线性标注
                pass
    
    def visualize_cad(self, json_data, output_path=None):
        """可视化CAD模型"""
        # 清空画布
        self.ax.clear()
        self.ax.set_xlim(0, self.canvas_size[0])
        self.ax.set_ylim(0, self.canvas_size[1])
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        
        # 设置标题
        title = f"CADmodel - {json_data.get('metadata', {}).get('notes', 'no description')}"
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        
        # 绘制基本图形
        for primitive in json_data.get('primitives', []):
            self.draw_primitive(primitive)
        
        # 绘制约束（可选）
        if json_data.get('constraints'):
            self.draw_constraints(json_data['constraints'])
        
        # 绘制尺寸（可选）
        if json_data.get('dimensions'):
            self.draw_dimensions(json_data['dimensions'])
        
        # 添加统计信息
        metadata = json_data.get('metadata', {})
        if metadata:
            stats_text = f"basic shapes: {metadata.get('primitive_count', {})}\n"
            stats_text += f"constraints: {metadata.get('constraint_count', 0)}\n"
            stats_text += f"dimensions: {metadata.get('dimension_count', 0)}"
            
            self.ax.text(0.02, 0.98, stats_text, transform=self.ax.transAxes,
                        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # 保存图片
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"image saved to: {output_path}")
        
        return self.fig, self.ax

def process_cad_files(input_dir, output_dir, file_format='png', fix_paths=False):
    """批量处理CAD文件"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 如果启用路径修复，确保输出目录结构正确
    if fix_paths:
        # 确保输出路径是 cad/cad/images/ 格式
        if not str(output_path).endswith('cad/images'):
            if str(output_path).endswith('images'):
                output_path = Path(str(output_path).replace('images', 'cad/images'))
            else:
                output_path = Path(str(output_path)) / 'cad' / 'images'
        print(f"🔧 批量处理使用修复后的输出路径: {output_path}")
    
    # 创建输出目录（包括所有必要的父目录）
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 查找所有JSON文件
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        print(f"no JSON files found in {input_dir}")
        return
    
    print(f"found {len(json_files)} JSON files")
    
    # 创建可视化器
    visualizer = CADVisualizer()
    
    for json_file in json_files:
        try:
            print(f"processing file: {json_file.name}")
            
            # 读取JSON数据
            with open(json_file, 'r', encoding='utf-8') as f:
                cad_data = json.load(f)
            
            # 生成输出文件名
            output_file = output_path / f"{json_file.stem}.{file_format}"
            
            # 可视化并保存
            visualizer.visualize_cad(cad_data, str(output_file))
            
        except Exception as e:
            print(f"error processing file {json_file.name}: {e}")
            continue
    
    print(f"processing completed! images saved to: {output_dir}")
    if fix_paths:
        print(f"📁 实际保存位置: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Transform CAD JSON files to images')
    parser.add_argument('--input', '-i', type=str, default='../cad/cadl',
                        help='input directory path (default: ../cad/cadl)')
    parser.add_argument('--output', '-o', type=str, default='../cad/images',
                        help='output directory path (default: ../cad/images)')
    parser.add_argument('--format', '-f', type=str, default='png',
                        choices=['png', 'jpg', 'pdf', 'svg'],
                        help='output image format (default: png)')
    parser.add_argument('--single', '-s', type=str,
                        help='process single file (optional)')
    parser.add_argument('--fix-paths', action='store_true',
                        help='automatically fix output paths to match AI retrieval system expectations')
    parser.add_argument('--auto-detect', action='store_true',
                        help='automatically detect and set correct paths based on current working directory')
    
    args = parser.parse_args()
    
    # 自动检测当前工作目录并设置正确路径
    if args.auto_detect:
        current_dir = Path.cwd()
        print(f"🔍 当前工作目录: {current_dir}")
        
        # 检测是否在项目根目录
        if (current_dir / 'cad').exists():
            print("✅ 检测到项目根目录结构")
            args.input = 'cad/cadl'
            args.output = 'cad/cad/images'
            print(f"🔧 自动设置输入路径: {args.input}")
            print(f"🔧 自动设置输出路径: {args.output}")
        elif (current_dir / 'cad_to_image.py').exists():
            print("✅ 检测到在cad目录中")
            args.input = 'cadl'
            args.output = 'cad/images'
            print(f"🔧 自动设置输入路径: {args.input}")
            print(f"🔧 自动设置输出路径: {args.output}")
        else:
            print("⚠️  无法自动检测目录结构，使用默认路径")
    
    # 自动修复路径以匹配AI检索系统期望
    if args.fix_paths:
        # 确保输出路径是 cad/cad/images/ 格式
        if not args.output.endswith('cad/images'):
            if args.output.endswith('images'):
                args.output = args.output.replace('images', 'cad/images')
            else:
                args.output = os.path.join(args.output, 'cad', 'images')
        print(f"🔧 自动修复输出路径: {args.output}")
    
    if args.single:
        # 处理单个文件
        if not os.path.exists(args.single):
            print(f"file not found: {args.single}")
            return
        
        try:
            with open(args.single, 'r', encoding='utf-8') as f:
                cad_data = json.load(f)
            
            # 确保输出路径正确
            if args.fix_paths:
                # 创建正确的输出目录结构
                output_dir = os.path.dirname(args.output)
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(args.output, f"{os.path.splitext(os.path.basename(args.single))[0]}.{args.format}")
            else:
                output_file = f"{os.path.splitext(args.single)[0]}.{args.format}"
            
            visualizer = CADVisualizer()
            visualizer.visualize_cad(cad_data, output_file)
            
            print(f"single file processing completed: {output_file}")
            
        except Exception as e:
            print(f"error processing file: {e}")
    else:
        # 批量处理
        process_cad_files(args.input, args.output, args.format, args.fix_paths)

if __name__ == "__main__":
    main()
