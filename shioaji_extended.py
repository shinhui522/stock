#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
永豐金證券 Shioaji API 擴展功能示範
包含股票查詢、即時報價、歷史數據等功能
"""

import os
from dotenv import load_dotenv
import shioaji as sj
import pandas as pd
from datetime import datetime, timedelta

# 載入環境變數
load_dotenv()

class ShioajiExtended:
    """Shioaji API 擴展功能客戶端"""
    
    def __init__(self):
        self.api = None
        self.is_connected = False
        self.contracts = {}
    
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

            print("🔍 使用量: ", self.api.usage())
            
            # 處理憑證路徑
            cert_path = os.environ.get("CA_CERT_PATH")
            if cert_path:
                cert_path = os.path.abspath(cert_path)
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
            
            # 載入合約資訊
            self.load_contracts()
            return True
            
        except Exception as e:
            print(f"❌ Shioaji API 連接失敗: {e}")
            return False
    
    def load_contracts(self):
        """載入股票合約資訊"""
        try:
            print("📋 正在載入合約資訊...")
            # 取得台股合約
            self.api.fetch_contracts(contract_download=True)
            print("✅ 合約資訊載入完成")
        except Exception as e:
            print(f"⚠️ 載入合約資訊失敗: {e}")
    
    def get_quote(self, stock_code):
        """獲取即時報價"""
        if not self.is_connected:
            print("❌ 請先連接 API")
            return None
        
        try:
            print(f"💰 獲取 {stock_code} 即時報價...")
            
            # 找到股票合約
            contract = self._find_contract(stock_code)
            
            if not contract:
                print(f"❌ 找不到股票代碼: {stock_code}")
                return None
            
            # 顯示合約基本資訊
            contract_name = getattr(contract, 'name', stock_code)
            contract_code = getattr(contract, 'code', stock_code)
            print(f"📋 合約資訊: {contract_name} ({contract_code})")
            print(f"   交易所: {getattr(contract, 'exchange', 'N/A')}")
            print(f"   參考價: ${getattr(contract, 'reference', 'N/A')}")
            print(f"   漲停價: ${getattr(contract, 'limit_up', 'N/A')}")
            print(f"   跌停價: ${getattr(contract, 'limit_down', 'N/A')}")
            
            # 獲取即時報價 (使用 snapshots 方法)
            try:
                snapshots = self.api.snapshots([contract])
                if snapshots and len(snapshots) > 0:
                    quote_data = snapshots[0]
                    print(f"\n📈 即時報價:")
                    print(f"   現價: ${getattr(quote_data, 'close', 'N/A')}")
                    print(f"   開盤: ${getattr(quote_data, 'open', 'N/A')}")
                    print(f"   最高: ${getattr(quote_data, 'high', 'N/A')}")
                    print(f"   最低: ${getattr(quote_data, 'low', 'N/A')}")
                    print(f"   成交量: {getattr(quote_data, 'volume', 'N/A')}")
                    print(f"   漲跌: {getattr(quote_data, 'change_price', 'N/A')}")
                    print(f"   漲跌幅: {getattr(quote_data, 'change_rate', 'N/A')}%")
                    
                    return quote_data
                else:
                    print("❌ 無法獲取即時報價資料")
                    return None
                    
            except Exception as quote_error:
                print(f"⚠️ 即時報價獲取失敗: {quote_error}")
                print("💡 可能原因: 非交易時間或該股票暫停交易")
                return contract
            
        except Exception as e:
            print(f"❌ 獲取報價失敗: {e}")
            print(f"   錯誤詳情: {str(e)}")
            return None
    
    def get_realtime_ticks(self, stock_code, last_cnt=10):
        """獲取即時逐筆交易資料 (使用 api.ticks)"""
        if not self.is_connected:
            print("❌ 請先連接 API")
            return None
        
        try:
            print(f"⚡ 獲取 {stock_code} 即時逐筆交易資料...")
            
            # 找到股票合約
            contract = self._find_contract(stock_code)
            
            if not contract:
                print(f"❌ 找不到股票代碼: {stock_code}")
                return None
            
            # 獲取今日日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 獲取即時逐筆資料
            ticks = self.api.ticks(
                contract=contract,
                date=today,
                query_type=sj.constant.TicksQueryType.AllDay,
                last_cnt=last_cnt  # 獲取最近N筆交易
            )
            
            if ticks and hasattr(ticks, 'ts'):
                contract_name = getattr(contract, 'name', stock_code)
                contract_code = getattr(contract, 'code', stock_code)
                
                print(f"⚡ {contract_name} ({contract_code}) - 最近 {last_cnt} 筆交易")
                print("=" * 60)
                
                # 轉換為 DataFrame 以便顯示
                df = pd.DataFrame({
                    '時間': ticks.ts,
                    '價格': ticks.close,
                    '成交量': ticks.volume,
                    '買賣別': ['買盤' if x == 1 else '賣盤' if x == -1 else '中性' for x in ticks.tick_type]
                })
                
                # 將時間戳轉換為可讀格式
                df['時間'] = pd.to_datetime(df['時間'], unit='ns').dt.strftime('%H:%M:%S.%f').str[:-3]
                
                print(df.to_string(index=False))
                
                # 顯示統計資訊
                if len(df) > 0:
                    print("\n📊 統計資訊:")
                    print(f"   最新價格: ${df['價格'].iloc[-1]}")
                    print(f"   最高價格: ${df['價格'].max()}")
                    print(f"   最低價格: ${df['價格'].min()}")
                    print(f"   總成交量: {df['成交量'].sum():,}")
                    print(f"   平均價格: ${df['價格'].mean():.2f}")
                
                return ticks
            else:
                print("❌ 無法獲取逐筆交易資料")
                return None
                
        except Exception as e:
            print(f"❌ 獲取逐筆交易資料失敗: {e}")
            print(f"   錯誤詳情: {str(e)}")
            return None
    
    def get_ticks_by_time_range(self, stock_code, time_start="09:00:00", time_end="13:30:00"):
        """獲取指定時間範圍的逐筆交易資料"""
        if not self.is_connected:
            print("❌ 請先連接 API")
            return None
        
        try:
            print(f"🕐 獲取 {stock_code} 時間範圍 {time_start} ~ {time_end} 的逐筆交易資料...")
            
            # 找到股票合約
            contract = self._find_contract(stock_code)
            
            if not contract:
                print(f"❌ 找不到股票代碼: {stock_code}")
                return None
            
            # 獲取今日日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 獲取指定時間範圍的逐筆資料
            ticks = self.api.ticks(
                contract=contract,
                date=today,
                query_type=sj.constant.TicksQueryType.Range,
                time_start=time_start,
                time_end=time_end
            )
            
            if ticks and hasattr(ticks, 'ts') and len(ticks.ts) > 0:
                contract_name = getattr(contract, 'name', stock_code)
                contract_code = getattr(contract, 'code', stock_code)
                
                print(f"🕐 {contract_name} ({contract_code}) - {time_start} ~ {time_end}")
                print("=" * 70)
                
                # 轉換為 DataFrame
                df = pd.DataFrame({
                    '時間': ticks.ts,
                    '價格': ticks.close,
                    '成交量': ticks.volume,
                    '買賣別': ['買盤' if x == 1 else '賣盤' if x == -1 else '中性' for x in ticks.tick_type]
                })
                
                # 將時間戳轉換為可讀格式
                df['時間'] = pd.to_datetime(df['時間'], unit='ns').dt.strftime('%H:%M:%S.%f').str[:-3]
                
                # 只顯示前20筆和後20筆
                if len(df) > 40:
                    print("📊 前20筆交易:")
                    print(df.head(20).to_string(index=False))
                    print(f"\n... (省略 {len(df)-40} 筆交易) ...\n")
                    print("📊 後20筆交易:")
                    print(df.tail(20).to_string(index=False))
                else:
                    print(df.to_string(index=False))
                
                # 顯示統計資訊
                print(f"\n📊 統計資訊 (共 {len(df)} 筆交易):")
                print(f"   開盤價格: ${df['價格'].iloc[0]}")
                print(f"   收盤價格: ${df['價格'].iloc[-1]}")
                print(f"   最高價格: ${df['價格'].max()}")
                print(f"   最低價格: ${df['價格'].min()}")
                print(f"   總成交量: {df['成交量'].sum():,}")
                print(f"   平均價格: ${df['價格'].mean():.2f}")
                
                return ticks
            else:
                print("❌ 指定時間範圍內無交易資料")
                return None
                
        except Exception as e:
            print(f"❌ 獲取時間範圍交易資料失敗: {e}")
            print(f"   錯誤詳情: {str(e)}")
            return None
    
    def get_historical_data(self, stock_code, days=30):
        """獲取歷史數據"""
        if not self.is_connected:
            print("❌ 請先連接 API")
            return None
        
        try:
            print(f"📊 獲取 {stock_code} 近 {days} 天歷史數據...")
            
            # 找到股票合約
            contract = self._find_contract(stock_code)
            
            if not contract:
                print(f"❌ 找不到股票代碼: {stock_code}")
                return None
            
            # 計算日期範圍
            end_date = datetime.now()
            # -1 是因為 kbars 的 start 和 end 是包含的，確保獲取正確的天數
            start_date = end_date - timedelta(days=days-1)
            
            # 獲取歷史數據
            kbars = self.api.kbars(
                contract=contract,
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d')
            )
            
            if kbars:
                df = pd.DataFrame({**kbars})
                print(f"✅ 獲取到 {len(df)} 筆數據")
                print("\n📈 最近5天數據:")
                print(df.tail().to_string(index=False))
                return df
            else:
                print("❌ 無法獲取歷史數據")
                return None
                
        except Exception as e:
            print(f"❌ 獲取歷史數據失敗: {e}")
            print(f"   錯誤詳情: {str(e)}")
            return None
    
    def get_account_info(self):
        """獲取帳戶資訊"""
        if not self.is_connected:
            print("❌ 請先連接 API")
            return None
        
        try:
            print("👤 獲取帳戶資訊...")
            
            # 獲取帳戶餘額
            account_balance = self.api.account_balance()
            
            if account_balance:
                print("💰 帳戶資訊:")
                print(f"   可用資金: ${account_balance.get('available_balance', 'N/A')}")
                print(f"   帳戶淨值: ${account_balance.get('net_value', 'N/A')}")
            
            return account_balance
            
        except Exception as e:
            print(f"❌ 獲取帳戶資訊失敗: {e}")
            return None
    
    def debug_contracts(self):
        """調試合約結構"""
        if not self.is_connected:
            print("❌ 請先連接 API")
            return
        
        try:
            print("🔍 調試合約結構...")
            
            if hasattr(self.api, 'Contracts'):
                contracts = self.api.Contracts
                print(f"📋 Contracts 類型: {type(contracts)}")
                
                if hasattr(contracts, 'Stocks'):
                    stocks = contracts.Stocks
                    print(f"📊 Stocks 類型: {type(stocks)}")
                    print(f"📊 Stocks 屬性: {dir(stocks)[:10]}...")  # 只顯示前10個
                    
                    # 嘗試獲取一些範例
                    if hasattr(stocks, '__iter__'):
                        try:
                            sample = list(stocks)[:3] if hasattr(stocks, '__len__') else []
                            print(f"📊 範例數量: {len(sample) if sample else '無法獲取'}")
                            for i, item in enumerate(sample):
                                print(f"   {i+1}. {type(item)} - {getattr(item, 'code', 'N/A')}")
                        except Exception as e:
                            print(f"   ⚠️ 無法迭代: {e}")
                    
                    # 嘗試直接訪問台積電
                    for code in ['2330', 'TSE_2330', '2330.TW']:
                        try:
                            contract = getattr(stocks, code, None)
                            if contract:
                                print(f"✅ 找到 {code}: {type(contract)}")
                                break
                        except:
                            continue
                    else:
                        print("❌ 無法找到台積電(2330)合約")
                
            else:
                print("❌ 找不到 Contracts")
                
        except Exception as e:
            print(f"❌ 調試失敗: {e}")
    
    def _find_contract(self, stock_code):
        """尋找股票合約"""
        try:
            if not hasattr(self.api.Contracts, 'Stocks'):
                print("❌ 合約資訊未載入")
                return None
            
            stocks = self.api.Contracts.Stocks
            
            # 方法1: 如果是字典結構
            if isinstance(stocks, dict):
                # 直接用股票代碼查找
                if stock_code in stocks:
                    return stocks[stock_code]
                
                # 遍歷查找
                for key, contract in stocks.items():
                    if hasattr(contract, 'code') and contract.code == stock_code:
                        return contract
                    if key == stock_code:
                        return contract
            
            # 方法2: 如果有 __getitem__ 方法
            elif hasattr(stocks, '__getitem__'):
                try:
                    return stocks[stock_code]
                except (KeyError, TypeError):
                    pass
            
            # 方法3: 如果是可迭代的
            elif hasattr(stocks, '__iter__'):
                for contract in stocks:
                    if hasattr(contract, 'code') and contract.code == stock_code:
                        return contract
            
            print(f"💡 提示：嘗試使用 api.Contracts.Stocks.{stock_code}")
            return getattr(stocks, stock_code, None)
            
        except Exception as e:
            print(f"⚠️ 查找合約時發生錯誤: {e}")
            return None
    
    def _alternative_search(self, keyword):
        """替代搜尋方法"""
        try:
            print("🔄 嘗試直接訪問合約...")
            
            # 嘗試直接訪問
            if hasattr(self.api.Contracts, 'Stocks'):
                stocks = self.api.Contracts.Stocks
                
                # 如果關鍵字看起來像股票代碼
                if keyword.isdigit() and len(keyword) == 4:
                    contract = getattr(stocks, keyword, None)
                    if contract:
                        return [{
                            'code': keyword,
                            'name': getattr(contract, 'name', keyword),
                            'exchange': 'TSE',
                            'contract': contract
                        }]
            
            return []
            
        except Exception as e:
            print(f"⚠️ 替代搜尋失敗: {e}")
            return []
    
    def disconnect(self):
        """斷開連接"""
        if self.api and self.is_connected:
            try:
                self.api.logout()
                self.is_connected = False
                print("✅ 已斷開 Shioaji API 連接")
            except Exception as e:
                print(f"❌ 斷開連接時發生錯誤: {e}")

def interactive_menu():
    """互動式選單"""
    client = ShioajiExtended()
    
    if not client.connect():
        return
    
    while True:
        print("\n" + "="*50)
        print("🏦 永豐金證券 Shioaji API 功能選單")
        print("="*50)
        print("1. 搜尋股票")
        print("2. 即時報價")
        print("3. 即時逐筆交易 (最近N筆)")
        print("4. 時間範圍逐筆交易")
        print("5. 歷史數據")
        print("6. 帳戶資訊")
        print("7. 調試合約結構")
        print("8. 退出")
        
        choice = input("\n請選擇功能 (1-8): ").strip()
        
        if choice == '2':
            stock_code = input("請輸入股票代碼 (例: 2330): ").strip()
            if stock_code:
                client.get_quote(stock_code)
        
        elif choice == '3':
            stock_code = input("請輸入股票代碼 (例: 2330): ").strip()
            if stock_code:
                cnt = input("請輸入要查看的交易筆數 (預設10筆): ").strip()
                cnt = int(cnt) if cnt.isdigit() else 10
                client.get_realtime_ticks(stock_code, cnt)
        
        elif choice == '4':
            stock_code = input("請輸入股票代碼 (例: 2330): ").strip()
            if stock_code:
                time_start = input("請輸入開始時間 (格式: HH:MM:SS, 預設09:00:00): ").strip()
                time_start = time_start if time_start else "09:00:00"
                time_end = input("請輸入結束時間 (格式: HH:MM:SS, 預設13:30:00): ").strip()
                time_end = time_end if time_end else "13:30:00"
                client.get_ticks_by_time_range(stock_code, time_start, time_end)
        
        elif choice == '5':
            stock_code = input("請輸入股票代碼 (例: 2330): ").strip()
            if stock_code:
                days = input("請輸入天數 (預設30天): ").strip()
                days = int(days) if days.isdigit() else 30
                client.get_historical_data(stock_code, days)
        
        elif choice == '6':
            client.get_account_info()
        
        elif choice == '7':
            client.debug_contracts()
        
        elif choice == '8':
            print("👋 謝謝使用！")
            break
        
        else:
            print("❌ 無效選擇，請重新輸入")
    
    client.disconnect()

def main():
    """主函數"""
    print("=== 永豐金證券 Shioaji API 擴展功能示範 ===")
    
    # 檢查環境變數
    required_vars = ["API_KEY", "SECRET_KEY", "CA_CERT_PATH", "CA_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ 缺少環境變數: {', '.join(missing_vars)}")
        print("請在 .env 檔案中設定這些變數")
        return 1
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n⚠️ 用戶中斷程式")
    
    return 0

if __name__ == "__main__":
    exit(main()) 