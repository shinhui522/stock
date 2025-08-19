#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shioaji API Ticks 功能示範
展示如何使用 api.ticks 獲取即時逐筆交易資料
"""

from shioaji_extended import ShioajiExtended

def demo_ticks():
    """示範逐筆交易功能"""
    print("=== Shioaji API Ticks 功能示範 ===\n")
    
    # 建立客戶端
    client = ShioajiExtended()
    
    # 連接 API
    if not client.connect():
        print("❌ 無法連接到 Shioaji API")
        return
    
    # 測試股票代碼 (台積電)
    stock_code = "2330"
    
    print(f"📊 測試股票: {stock_code} (台積電)\n")
    
    try:
        # 1. 獲取最近10筆交易
        print("1️⃣ 獲取最近10筆逐筆交易資料:")
        print("-" * 50)
        ticks_recent = client.get_realtime_ticks(stock_code, last_cnt=10)
        
        if ticks_recent:
            print("✅ 成功獲取最近交易資料\n")
        else:
            print("❌ 無法獲取最近交易資料\n")
        
        # 2. 獲取指定時間範圍的交易 (早上9點到10點)
        print("2️⃣ 獲取指定時間範圍交易資料 (09:00-10:00):")
        print("-" * 50)
        ticks_range = client.get_ticks_by_time_range(
            stock_code, 
            time_start="09:00:00", 
            time_end="10:00:00"
        )
        
        if ticks_range:
            print("✅ 成功獲取時間範圍交易資料\n")
        else:
            print("❌ 無法獲取時間範圍交易資料\n")
        
        # 3. 獲取最近30筆交易 (更多資料)
        print("3️⃣ 獲取最近30筆逐筆交易資料:")
        print("-" * 50)
        ticks_more = client.get_realtime_ticks(stock_code, last_cnt=30)
        
        if ticks_more:
            print("✅ 成功獲取更多交易資料\n")
        else:
            print("❌ 無法獲取更多交易資料\n")
    
    except Exception as e:
        print(f"❌ 示範過程中發生錯誤: {e}")
    
    finally:
        # 斷開連接
        client.disconnect()
        print("✅ 示範完成")

def main():
    """主函數"""
    try:
        demo_ticks()
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷程式")
    except Exception as e:
        print(f"❌ 程式執行錯誤: {e}")

if __name__ == "__main__":
    main() 