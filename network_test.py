import requests
import time

def test_yahoo_connection():
    """
    測試是否能連線到 Yahoo Finance 的各個 API 端點。
    """
    urls_to_test = {
        "Query1 (主要)": "https://query1.finance.yahoo.com/v7/finance/download/2330.TW",
        "Query2 (備用)": "https://query2.finance.yahoo.com/v7/finance/download/2330.TW",
        "Chart API": "https://query1.finance.yahoo.com/v8/finance/chart/2330.TW"
    }
    
    all_successful = True
    
    for name, url in urls_to_test.items():
        print(f"--- 正在測試端點: {name} ---")
        print(f"URL: {url}")
        try:
            # 使用較短的超時時間來快速檢測連線問題
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            
            if response.status_code == 200:
                print(f"[SUCCESS] 連線成功！狀態碼: {response.status_code}")
            else:
                print(f"[ERROR] 連線失敗。狀態碼: {response.status_code}")
                print(f"回應內容 (前100字元): {response.text[:100]}")
                all_successful = False
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 發生連線錯誤: {e}")
            all_successful = False
        
        print("-" * (len(name) + 20))
        time.sleep(1) # 避免請求過於頻繁

    return all_successful

if __name__ == "__main__":
    print("正在開始網路連線測試...")
    success = test_yahoo_connection()
    print("\n--- 測試總結 ---")
    if success:
        print("[SUCCESS] 所有對 Yahoo Finance 的連線測試均成功。")
        print("這表示您的網路應該可以正常存取 yfinance 所需的數據。")
    else:
        print("[ERROR] 至少有一個連線測試失敗。")
        print("這可能表示有防火牆、代理伺erv器、DNS 問題或網路不穩定。")
        print("請檢查您的網路設定，或嘗試在不同的網路環境下執行。")