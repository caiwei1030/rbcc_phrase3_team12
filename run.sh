#!/bin/bash

# 智能打包数字化系统启动脚本

echo "🚀 启动Non-standard Part Approval AI Retrieval System..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到pip3，请先安装pip"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖包..."
pip3 install -r requirements.txt

# 检查环境变量配置
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  警告: 未找到 .streamlit/secrets.toml 配置文件"
    echo "请创建配置文件并设置 SILICONFLOW_API_KEY"
    echo "参考 .streamlit/secrets.toml.template 文件"
fi

# 启动应用
echo "🌐 启动Streamlit应用..."
streamlit run app.py
