#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
永豐金證券 Shioaji API 整合示範
"""

import os
from dotenv import load_dotenv
import shioaji as sj

# 載入環境變數
load_dotenv()

class ShioajiClient:
    """Shioaji API 客戶端"""
    
    def __init__(self):
        self.api = None
        self.is_connected = False
    
    def connect(self):
        """連接到 Shioaji API"""
        try:
            # 初始化 API（模擬模式）
            self.api = sj.Shioaji(simulation=True)
            
            # 登入
            self.api.login(
                api_key=os.environ.get("API_KEY"),
                secret_key=os.environ.get("SECRET_KEY"),
                fetch_contract=False
            )
            
            # 處理憑證路徑（支援相對路徑）
            cert_path = os.environ.get("CA_CERT_PATH")
            if cert_path:
                # 將相對路徑轉換為絕對路徑
                cert_path = os.path.abspath(cert_path)
                print(f"📁 憑證檔案路徑: {cert_path}")
                
                # 檢查檔案是否存在
                if not os.path.exists(cert_path):
                    print(f"❌ 找不到憑證檔案: {cert_path}")
                    return False
            
            # 啟用憑證
            self.api.activate_ca(
                ca_path=cert_path,
                ca_passwd=os.environ.get("CA_PASSWORD"),
            )
            
            self.is_connected = True
            print("✅ Shioaji API 連接成功！")
            return True
            
        except Exception as e:
            print(f"❌ Shioaji API 連接失敗: {e}")
            return False
    
    def get_stock_data(self, symbol):
        """獲取股票資料"""
        if not self.is_connected:
            print("❌ 請先連接 API")
            return None
            
        try:
            # 這裡可以添加獲取股票資料的邏輯
            print(f"📊 正在獲取 {symbol} 的資料...")
            # 實際的資料獲取邏輯需要根據 Shioaji API 文件實作
            return None
            
        except Exception as e:
            print(f"❌ 獲取股票資料失敗: {e}")
            return None
    
    def disconnect(self):
        """斷開連接"""
        if self.api and self.is_connected:
            try:
                self.api.logout()
                self.is_connected = False
                print("✅ 已斷開 Shioaji API 連接")
            except Exception as e:
                print(f"❌ 斷開連接時發生錯誤: {e}")

def main():
    """主函數"""
    print("=== 永豐金證券 Shioaji API 示範 ===")
    
    # 檢查環境變數
    required_vars = ["API_KEY", "SECRET_KEY", "CA_CERT_PATH", "CA_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ 缺少環境變數: {', '.join(missing_vars)}")
        print("請在 .env 檔案中設定這些變數")
        return 1
    
    # 創建客戶端並連接
    client = ShioajiClient()
    
    if client.connect():
        try:
            # 這裡可以添加您的業務邏輯
            print("🎯 API 已就緒，可以開始進行股票操作")
            
            # 示範：獲取股票資料
            # client.get_stock_data("2330")
            
        except KeyboardInterrupt:
            print("\n⚠️ 用戶中斷程式")
        finally:
            client.disconnect()
    
    return 0

if __name__ == "__main__":
    exit(main()) 