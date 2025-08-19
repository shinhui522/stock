@echo off
chcp 65001 > nul
title 股票技術分析系統

echo.
echo ========================================
echo    股票技術分析系統 v1.0
echo ========================================
echo.
echo 選擇啟動方式：
echo 1. 網頁界面 (推薦)
echo 2. 命令行互動模式
echo 3. 示範功能
echo 4. 安裝依賴套件
echo 5. 退出
echo.

set /p choice=請選擇 (1-5): 

if "%choice%"=="1" (
    echo 正在啟動網頁界面...
    streamlit run streamlit_app.py
) else if "%choice%"=="2" (
    echo 正在啟動命令行模式...
    python main.py -i
) else if "%choice%"=="3" (
    echo 正在運行示範...
    python demo.py
) else if "%choice%"=="4" (
    echo 正在安裝依賴套件...
    python install.py
) else if "%choice%"=="5" (
    exit
) else (
    echo 無效選擇，請重新執行
)

pause 