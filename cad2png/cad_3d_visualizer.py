#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D CAD模型可视化工具
支持从JSON文件创建3D CAD模型并导出为图片
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as patches
from pathlib import Path
import argparse

class CAD3DVisualizer:
    def __init__(self):
        self.fig = None
        self.ax = None
        
    def create_3d_plot(self):
        """创建3D绘图环境"""
        self.fig = plt.figure(figsize=(15, 12))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('X轴')
        self.ax.set_ylabel('Y轴')
        self.ax.set_zlabel('Z轴')
        self.ax.set_title('3D CAD模型可视化', fontsize=16, fontweight='bold')
        
    def draw_2d_profile(self, primitives, z_height=0, color='blue'):
        """在指定Z高度绘制2D轮廓"""
        for primitive in primitives:
            if primitive['type'] == 'Circle':
                # 绘制圆形
                theta = np.linspace(0, 2*np.pi, 100)
                x = primitive['xc'] + primitive['r'] * np.cos(theta)
                y = primitive['yc'] + primitive['r'] * np.sin(theta)
                z = np.full_like(theta, z_height)
                self.ax.plot(x, y, z, color=color, linewidth=2)
                
            elif primitive['type'] == 'Line':
                # 绘制直线
                x = [primitive['xstart'], primitive['xend']]
                y = [primitive['ystart'], primitive['yend']]
                z = [z_height, z_height]
                self.ax.plot(x, y, z, color=color, linewidth=2)
                
    def create_extruded_model(self, json_data, extrude_height=100):
        """创建拉伸的3D模型"""
        self.create_3d_plot()
        
        # 获取基本图形
        primitives = json_data.get('primitives', [])
        
        # 绘制底部轮廓
        self.draw_2d_profile(primitives, z_height=0, color='blue')
        
        # 绘制顶部轮廓
        self.draw_2d_profile(primitives, z_height=extrude_height, color='red')
        
        # 绘制连接线（创建3D效果）
        for primitive in primitives:
            if primitive['type'] == 'Circle':
                # 绘制圆柱体的连接线
                theta = np.linspace(0, 2*np.pi, 8)
                for t in theta:
                    x = primitive['xc'] + primitive['r'] * np.cos(t)
                    y = primitive['yc'] + primitive['r'] * np.sin(t)
                    self.ax.plot([x, x], [y, y], [0, extrude_height], 
                               color='gray', alpha=0.5, linewidth=1)
                               
            elif primitive['type'] == 'Line':
                # 绘制直线的连接线
                x_start, y_start = primitive['xstart'], primitive['ystart']
                x_end, y_end = primitive['xend'], primitive['yend']
                
                # 绘制四个角点的连接线
                for x, y in [(x_start, y_start), (x_end, y_end)]:
                    self.ax.plot([x, x], [y, y], [0, extrude_height], 
                               color='gray', alpha=0.5, linewidth=1)
        
        # 设置坐标轴范围
        all_x = []
        all_y = []
        for primitive in primitives:
            if primitive['type'] == 'Circle':
                all_x.extend([primitive['xc'] - primitive['r'], primitive['xc'] + primitive['r']])
                all_y.extend([primitive['yc'] - primitive['r'], primitive['yc'] + primitive['r']])
            elif primitive['type'] == 'Line':
                all_x.extend([primitive['xstart'], primitive['xend']])
                all_y.extend([primitive['ystart'], primitive['yend']])
        
        if all_x and all_y:
            x_range = max(all_x) - min(all_x)
            y_range = max(all_y) - min(all_y)
            margin = max(x_range, y_range) * 0.1
            
            self.ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
            self.ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
            self.ax.set_zlim(0, extrude_height + margin)
        
        return self.fig, self.ax
    
    def create_wireframe_model(self, json_data, extrude_height=100):
        """创建线框3D模型"""
        self.create_3d_plot()
        
        primitives = json_data.get('primitives', [])
        
        # 绘制底部和顶部轮廓
        self.draw_2d_profile(primitives, z_height=0, color='blue')
        self.draw_2d_profile(primitives, z_height=extrude_height, color='red')
        
        # 绘制连接线
        for primitive in primitives:
            if primitive['type'] == 'Circle':
                # 绘制圆周上的连接点
                num_points = 8
                theta = np.linspace(0, 2*np.pi, num_points)
                for t in theta:
                    x = primitive['xc'] + primitive['r'] * np.cos(t)
                    y = primitive['yc'] + primitive['r'] * np.sin(t)
                    self.ax.plot([x, x], [y, y], [0, extrude_height], 
                               color='gray', alpha=0.7, linewidth=1)
                               
            elif primitive['type'] == 'Line':
                # 绘制端点连接线
                x_start, y_start = primitive['xstart'], primitive['ystart']
                x_end, y_end = primitive['xend'], primitive['yend']
                
                for x, y in [(x_start, y_start), (x_end, y_end)]:
                    self.ax.plot([x, x], [y, y], [0, extrude_height], 
                               color='gray', alpha=0.7, linewidth=1)
        
        # 设置坐标轴
        self._set_axis_limits(primitives, extrude_height)
        
        return self.fig, self.ax
    
    def _set_axis_limits(self, primitives, extrude_height):
        """设置坐标轴范围"""
        all_x = []
        all_y = []
        for primitive in primitives:
            if primitive['type'] == 'Circle':
                all_x.extend([primitive['xc'] - primitive['r'], primitive['xc'] + primitive['r']])
                all_y.extend([primitive['yc'] - primitive['r'], primitive['yc'] + primitive['r']])
            elif primitive['type'] == 'Line':
                all_x.extend([primitive['xstart'], primitive['xend']])
                all_y.extend([primitive['ystart'], primitive['yend']])
        
        if all_x and all_y:
            x_range = max(all_x) - min(all_x)
            y_range = max(all_y) - min(all_y)
            margin = max(x_range, y_range) * 0.1
            
            self.ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
            self.ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
            self.ax.set_zlim(0, extrude_height + margin)
    
    def add_metadata_info(self, json_data):
        """添加模型信息"""
        metadata = json_data.get('metadata', {})
        if metadata:
            info_text = f"基本图形数量: {metadata.get('primitive_count', {})}\n"
            info_text += f"约束数量: {metadata.get('constraint_count', 0)}\n"
            info_text += f"尺寸数量: {metadata.get('dimension_count', 0)}"
            
            # 在3D图中添加文本信息
            self.ax.text2D(0.02, 0.98, info_text, transform=self.ax.transAxes,
                           verticalalignment='top', 
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def save_model(self, output_path, dpi=300):
        """保存模型图片"""
        if self.fig:
            plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
            print(f"3D模型图片已保存到: {output_path}")
    
    def show_model(self):
        """显示模型"""
        if self.fig:
            plt.show()

def process_cad_3d_files(input_dir, output_dir, extrude_height=100, style='extruded'):
    """批量处理CAD文件并生成3D可视化"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 查找所有JSON文件
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        print(f"在 {input_dir} 中没有找到JSON文件")
        return
    
    print(f"找到 {len(json_files)} 个JSON文件")
    
    for json_file in json_files:
        try:
            print(f"处理文件: {json_file.name}")
            
            # 读取JSON数据
            with open(json_file, 'r', encoding='utf-8') as f:
                cad_data = json.load(f)
            
            # 创建3D可视化器
            visualizer = CAD3DVisualizer()
            
            # 根据样式创建不同的3D模型
            if style == 'extruded':
                visualizer.create_extruded_model(cad_data, extrude_height)
            elif style == 'wireframe':
                visualizer.create_wireframe_model(cad_data, extrude_height)
            
            # 添加元数据信息
            visualizer.add_metadata_info(cad_data)
            
            # 生成输出文件名
            output_file = output_path / f"{json_file.stem}_3d.png"
            
            # 保存图片
            visualizer.save_model(str(output_file))
            
            # 关闭图形以释放内存
            plt.close(visualizer.fig)
            
        except Exception as e:
            print(f"处理文件 {json_file.name} 时出错: {e}")
            continue
    
    print(f"3D模型处理完成！图片保存在: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='3D CAD模型可视化工具')
    parser.add_argument('--input', '-i', type=str, default='cad/cadl',
                        help='输入目录路径 (默认: cad/cadl)')
    parser.add_argument('--output', '-o', type=str, default='cad/3d_images',
                        help='输出目录路径 (默认: cad/3d_images)')
    parser.add_argument('--height', '-z', type=float, default=100,
                        help='拉伸高度 (默认: 100)')
    parser.add_argument('--style', '-s', type=str, default='extruded',
                        choices=['extruded', 'wireframe'],
                        help='3D模型样式 (默认: extruded)')
    parser.add_argument('--single', type=str,
                        help='处理单个文件 (可选)')
    
    args = parser.parse_args()
    
    if args.single:
        # 处理单个文件
        if not os.path.exists(args.single):
            print(f"文件不存在: {args.single}")
            return
        
        try:
            with open(args.single, 'r', encoding='utf-8') as f:
                cad_data = json.load(f)
            
            visualizer = CAD3DVisualizer()
            
            if args.style == 'extruded':
                visualizer.create_extruded_model(cad_data, args.height)
            else:
                visualizer.create_wireframe_model(cad_data, args.height)
            
            visualizer.add_metadata_info(cad_data)
            
            output_file = f"{os.path.splitext(args.single)[0]}_3d.png"
            visualizer.save_model(output_file)
            
            print(f"单个文件处理完成: {output_file}")
            
        except Exception as e:
            print(f"处理文件时出错: {e}")
    else:
        # 批量处理
        process_cad_3d_files(args.input, args.output, args.height, args.style)

if __name__ == "__main__":
    main()
