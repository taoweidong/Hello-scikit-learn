@echo off
echo 开始构建 Hello-scikit-learn 项目...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 运行构建脚本
python build.py

echo.
echo 构建完成！按任意键退出...
pause >nul