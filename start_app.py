#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动脚本 - 展示CAD图片集成功能
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖是否满足"""
    print("🔍 检查系统依赖...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("❌ 需要Python 3.7或更高版本")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查必要目录
    required_dirs = [
        "cad/cad/images",
        "services",
        "dataset"
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ 目录存在: {dir_path}")
        else:
            print(f"❌ 目录不存在: {dir_path}")
            return False
    
    # 检查必要文件
    required_files = [
        "app.py",
        "services/search_service.py",
        "ui.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ 文件存在: {file_path}")
        else:
            print(f"❌ 文件不存在: {file_path}")
            return False
    
    print("✅ 所有依赖检查通过!")
    return True

def run_tests():
    """运行测试脚本"""
    print("\n🧪 运行功能测试...")
    
    try:
        # 运行CAD图片匹配测试
        print("📸 测试CAD图片匹配功能...")
        result = subprocess.run([sys.executable, "test_cad_image_matching.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CAD图片匹配测试通过!")
            # 显示部分测试输出
            lines = result.stdout.split('\n')
            for line in lines[:10]:  # 显示前10行
                if line.strip():
                    print(f"   {line}")
            if len(lines) > 10:
                print("   ...")
        else:
            print("❌ CAD图片匹配测试失败!")
            print(f"错误信息: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ 测试超时")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def show_demo():
    """运行演示脚本"""
    print("\n🎭 运行功能演示...")
    
    try:
        result = subprocess.run([sys.executable, "demo_cad_integration.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ 功能演示完成!")
            # 显示关键统计信息
            lines = result.stdout.split('\n')
            for line in lines:
                if "总零件数:" in line or "有CAD图片:" in line or "无CAD图片:" in line:
                    print(f"   {line}")
        else:
            print("❌ 功能演示失败!")
            print(f"错误信息: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ 演示超时")
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")

def start_streamlit():
    """启动Streamlit应用"""
    print("\n🚀 启动Streamlit应用...")
    
    print("💡 应用启动后，您可以:")
    print("   1. 在浏览器中访问显示的地址")
    print("   2. 使用AI查询功能测试CAD图片集成")
    print("   3. 查看自动匹配的CAD设计图")
    print("   4. 体验完整的零件搜索和显示功能")
    
    print("\n⚠️  注意: 按Ctrl+C停止应用")
    
    try:
        # 启动Streamlit应用
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], 
                      timeout=None)  # 无超时限制
    except KeyboardInterrupt:
        print("\n🛑 应用已停止")
    except Exception as e:
        print(f"❌ 启动应用时发生错误: {e}")

def main():
    """主函数"""
    print("🎯 CAD图片集成功能启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请解决上述问题后重试")
        return
    
    # 运行测试
    run_tests()
    
    # 运行演示
    show_demo()
    
    # 询问是否启动应用
    print("\n🤔 是否启动Streamlit应用? (y/n): ", end="")
    try:
        choice = input().strip().lower()
        if choice in ['y', 'yes', '是', '']:
            start_streamlit()
        else:
            print("👋 再见!")
    except KeyboardInterrupt:
        print("\n👋 再见!")

if __name__ == "__main__":
    main()
