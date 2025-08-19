#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 yfinance 連接並嘗試不同的解決方案
"""

import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def test_internet_connection():
    """測試網路連接"""
    print("🔍 測試網路連接...")
    try:
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            print("✅ 網路連接正常")
            return True
        else:
            print("❌ 網路連接異常")
            return False
    except Exception as e:
        print(f"❌ 網路連接失敗: {e}")
        return False

def test_yahoo_finance():
    """測試 Yahoo Finance 網站"""
    print("🔍 測試 Yahoo Finance 網站...")
    try:
        response = requests.get("https://finance.yahoo.com", timeout=10)
        if response.status_code == 200:
            print("✅ Yahoo Finance 網站可訪問")
            return True
        else:
            print("❌ Yahoo Finance 網站不可訪問")
            return False
    except Exception as e:
        print(f"❌ Yahoo Finance 網站訪問失敗: {e}")
        return False

def test_yfinance_with_session():
    """使用自定義 session 測試 yfinance"""
    print("🔍 使用自定義 session 測試 yfinance...")
    
    # 創建自定義 session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    try:
        ticker = yf.Ticker("AAPL", session=session)
        data = ticker.history(period="5d")
        
        if not data.empty:
            print(f"✅ 成功獲取數據: {len(data)} 筆記錄")
            print("最新數據:")
            print(data.tail(2))
            return True
        else:
            print("❌ 獲取到空數據")
            return False
            
    except Exception as e:
        print(f"❌ yfinance 測試失敗: {e}")
        return False

def test_different_symbols():
    """測試不同的股票代碼"""
    print("🔍 測試不同的股票代碼...")
    
    symbols = [
        ("AAPL", "Apple"),
        ("MSFT", "Microsoft"),
        ("GOOGL", "Google"),
        ("TSLA", "Tesla"),
        ("2330.TW", "台積電"),
        ("7703.TW", "銳澤")
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    success_count = 0
    
    for symbol, name in symbols:
        try:
            print(f"測試 {symbol} ({name})...")
            ticker = yf.Ticker(symbol, session=session)
            data = ticker.history(period="5d")
            
            if not data.empty:
                print(f"  ✅ 成功: {len(data)} 筆數據，最新價格: {data['Close'][-1]:.2f}")
                success_count += 1
            else:
                print(f"  ❌ 空數據")
                
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
        
        time.sleep(1)  # 避免請求過於頻繁
    
    print(f"\n成功率: {success_count}/{len(symbols)} ({success_count/len(symbols)*100:.1f}%)")
    return success_count > 0

def try_alternative_approach():
    """嘗試替代方法"""
    print("🔍 嘗試替代方法...")
    
    # 方法1: 使用不同的 period 參數
    print("方法1: 使用不同的 period 參數")
    periods = ["1d", "5d", "1mo", "3mo"]
    
    for period in periods:
        try:
            ticker = yf.Ticker("AAPL")
            data = ticker.history(period=period)
            if not data.empty:
                print(f"  ✅ {period} 成功: {len(data)} 筆數據")
                return True
            else:
                print(f"  ❌ {period} 空數據")
        except Exception as e:
            print(f"  ❌ {period} 錯誤: {e}")
    
    # 方法2: 使用日期範圍
    print("方法2: 使用日期範圍")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        ticker = yf.Ticker("AAPL")
        data = ticker.history(start=start_date, end=end_date)
        
        if not data.empty:
            print(f"  ✅ 日期範圍成功: {len(data)} 筆數據")
            return True
        else:
            print(f"  ❌ 日期範圍空數據")
    except Exception as e:
        print(f"  ❌ 日期範圍錯誤: {e}")
    
    return False

def main():
    """主測試函數"""
    print("=" * 60)
    print("🔧 yfinance 連接診斷工具")
    print("=" * 60)
    
    # 測試步驟
    tests = [
        ("網路連接", test_internet_connection),
        ("Yahoo Finance 網站", test_yahoo_finance),
        ("yfinance with session", test_yfinance_with_session),
        ("不同股票代碼", test_different_symbols),
        ("替代方法", try_alternative_approach)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20}")
        print(f"測試: {test_name}")
        print('='*20)
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
            results[test_name] = False
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
    
    # 建議
    print("\n💡 建議:")
    if not results.get("網路連接", False):
        print("• 檢查網路連接")
    elif not results.get("Yahoo Finance 網站", False):
        print("• Yahoo Finance 網站可能暫時不可用")
        print("• 嘗試使用 VPN 或等待一段時間")
    elif not any(results.values()):
        print("• 所有測試都失敗，可能需要:")
        print("  - 檢查防火牆設置")
        print("  - 更新 yfinance 版本: pip install --upgrade yfinance")
        print("  - 使用代理服務器")
        print("  - 暫時使用示範數據")
    else:
        print("• 部分測試通過，yfinance 可能間歇性可用")
        print("• 建議在程式中加入重試機制")

if __name__ == "__main__":
    main() 