@echo off
echo ====================================================
echo 🚀 Hello-scikit-learn 一键式打包工具 (Windows)
echo ====================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查参数
if "%1"=="" (
    echo 开始构建当前平台...
    python build.py
) else if "%1"=="cleanspec" (
    echo 清理spec文件...
    python build.py cleanspec
) else (
    echo 执行命令: %1
    python build.py %1
)

echo.
echo 操作完成！按任意键退出...
pause >nul