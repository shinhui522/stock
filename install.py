#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票技術分析系統 - 安裝腳本
自動安裝所需依賴套件
"""

import subprocess
import sys
import os

def check_python_version():
    """檢查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 錯誤：需要 Python 3.8 或更高版本")
        print(f"當前版本：{version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本檢查通過：{version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """安裝依賴套件"""
    print("📦 正在安裝依賴套件...")
    
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ 找不到 {requirements_file} 文件")
        return False
    
    try:
        # 升級pip
        print("🔄 升級 pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True, capture_output=True)
        
        # 安裝依賴
        print("🔄 安裝依賴套件...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], 
                              check=True, capture_output=True, text=True)
        
        print("✅ 依賴套件安裝完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 安裝失敗：{e}")
        print(f"錯誤輸出：{e.stderr}")
        return False

def verify_installation():
    """驗證安裝"""
    print("🔍 驗證安裝...")
    
    required_modules = [
        'yfinance',
        'pandas',
        'numpy',
        'matplotlib',
        'plotly',
        'streamlit',
        'ta',
        'sklearn',
        'seaborn',
        'requests'
    ]
    
    failed_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n❌ 以下模組安裝失敗：{', '.join(failed_modules)}")
        return False
    
    print("\n✅ 所有模組驗證通過")
    return True

def create_desktop_shortcut():
    """創建桌面快捷方式（Windows）"""
    if sys.platform != "win32":
        return
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "股票技術分析系統.lnk")
        target = sys.executable
        wdir = os.getcwd()
        arguments = "streamlit_app.py"
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = "streamlit"
        shortcut.Arguments = f"run {arguments}"
        shortcut.WorkingDirectory = wdir
        shortcut.save()
        
        print("✅ 桌面快捷方式已創建")
        
    except ImportError:
        print("💡 提示：可以手動創建快捷方式來啟動系統")

def main():
    """主安裝函數"""
    print("🎯 股票技術分析系統 - 安裝程序")
    print("=" * 50)
    
    # 檢查Python版本
    if not check_python_version():
        return 1
    
    # 安裝依賴套件
    if not install_requirements():
        print("\n❌ 安裝失敗，請手動執行：pip install -r requirements.txt")
        return 1
    
    # 驗證安裝
    if not verify_installation():
        print("\n❌ 驗證失敗，請檢查安裝過程")
        return 1
    
    # 創建快捷方式
    create_desktop_shortcut()
    
    print("\n" + "=" * 50)
    print("🎉 安裝完成！")
    print("=" * 50)
    print("💡 使用方法：")
    print("1. 網頁界面：streamlit run streamlit_app.py")
    print("2. 命令行：python main.py -i")
    print("3. 示範功能：python demo.py")
    print("\n⚠️  首次使用可能需要下載股票數據，請確保網路連接正常")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 