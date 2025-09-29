#!/bin/bash

echo "===================================================="
echo "🚀 Hello-scikit-learn 一键式打包工具 (Linux/macOS)"
echo "===================================================="
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3，请先安装pip"
    exit 1
fi

# 检查参数
if [ $# -eq 0 ]; then
    echo "开始构建当前平台..."
    python3 build.py
elif [ "$1" = "cleanspec" ]; then
    echo "清理spec文件..."
    python3 build.py cleanspec
else
    echo "执行命令: $1"
    python3 build.py "$1"
fi

echo
echo "操作完成！"