# 股票技術分析系統 📈

一套專業的股票技術分析軟體，專門用於識別**緩坡爬升趨勢**、**黃藍線交叉點**和**利潤空間評估**。

## 🎯 核心功能

### 1. 緩坡爬升識別
- 檢測穩定的上升趨勢
- 過濾過於陡峭或不穩定的走勢
- 適合中長期投資策略

### 2. 黃藍線交叉分析
- **黃線**：5日移動平均線（短期趨勢）
- **藍線**：20日移動平均線（中期趨勢）
- 自動識別黃金交叉（買入信號）和死亡交叉（賣出信號）

### 3. 利潤空間計算
- 計算交叉點到後續高點的利潤空間
- 評估天花板與進場點的距離
- 提供歷史統計數據

### 4. 智能股票篩選
- 多指標綜合評分系統
- 批量分析和排名
- 自定義篩選條件

### 5. 永豐金證券 Shioaji API 整合 🏦
- **即時報價**：獲取股票最新價格資訊
- **逐筆交易資料**：使用 `api.ticks` 獲取即時交易明細
- **歷史數據**：K線圖和技術指標分析
- **股票搜尋**：快速找到目標股票合約
- **時間範圍查詢**：指定時間段的交易資料

## 🚀 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 使用方式

#### 1. 命令行模式
```bash
# 互動模式（推薦新手）
python main.py -i

# 分析單一股票
python main.py -s 2330.TW -p 6mo

# 股票篩選
python main.py --screen --min-score 70

# 啟動網頁界面
python main.py --web

# 永豐金證券 API 功能
python shioaji_extended.py    # 完整功能選單
python ticks_demo.py          # 逐筆交易示範
```

#### 2. 網頁界面模式（推薦）
```bash
streamlit run streamlit_app.py
```

#### 3. Python 程式碼模式
```python
from stock_analyzer import StockAnalyzer
from stock_screener import StockScreener

# 分析個股
analyzer = StockAnalyzer()
analyzer.fetch_data('2330.TW', period='6mo')
signals = analyzer.generate_trading_signals()
analyzer.print_analysis_report()

# 股票篩選
screener = StockScreener()
screener.load_stock_list()
results = screener.screen_stocks(min_score=60)
screener.print_screening_results()
```

## 📊 技術指標說明

### 移動平均線系統
- **MA5**：5日移動平均線（黃線）
- **MA20**：20日移動平均線（藍線）
- **MA60**：60日移動平均線（紫線）

### 支撐阻力系統
- **支撐線**：動態低點支撐
- **阻力線**：動態高點阻力

### 趨勢分析
- **趨勢斜率**：量化上升/下降趨勢強度
- **緩坡識別**：篩選穩定的爬升模式

## 🏆 評分系統

系統採用100分制評分，包含：

| 評分項目 | 權重 | 說明 |
|---------|------|------|
| 緩坡爬升趨勢 | 30% | 近期上升趨勢品質 |
| 黃金交叉信號 | 25% | 近期買入信號強度 |
| 利潤空間 | 25% | 歷史利潤空間平均 |
| 技術指標健康度 | 20% | 當前技術面狀況 |

## 📁 專案結構

```
stock/
├── stock_analyzer.py      # 核心分析模組
├── stock_screener.py      # 股票篩選器
├── streamlit_app.py       # 網頁界面
├── main.py               # 主程式入口
├── requirements.txt      # 依賴套件
└── README.md            # 說明文件
```

## 💡 使用範例

### 範例1：分析台積電
```python
analyzer = StockAnalyzer()
analyzer.fetch_data('2330.TW')
signals = analyzer.generate_trading_signals()

# 查看交叉點
print(f"發現 {len(signals['crossovers'])} 個交叉點")

# 查看上升趨勢
print(f"發現 {len(signals['uptrends'])} 個上升趨勢段")

# 生成圖表
fig = analyzer.create_interactive_chart()
fig.show()
```

### 範例2：篩選優質股票
```python
screener = StockScreener()
screener.load_stock_list([
    '2330.TW', '2454.TW', '2317.TW', 
    '2382.TW', '3711.TW'
])

results = screener.screen_stocks(min_score=70)
print(f"找到 {len(results)} 檔優質股票")
```

## 📈 支援的市場

- **台股**：代碼格式 `XXXX.TW` (例：2330.TW)
- **美股**：代碼格式 `XXXX` (例：AAPL, TSLA)
- **港股**：代碼格式 `XXXX.HK` (例：0700.HK)
- **其他**：Yahoo Finance 支援的所有市場

## ⚠️ 風險提示

1. **本系統僅供參考，不構成投資建議**
2. 技術分析有其局限性，請結合基本面分析
3. 投資有風險，請謹慎操作
4. 建議設置停損點，控制風險
5. 過去績效不代表未來表現

## 🔧 進階功能

### 自定義參數
```python
# 調整移動平均線週期
analyzer.data['Custom_MA'] = ta.trend.sma_indicator(
    analyzer.data['Close'], window=10
)

# 調整趨勢識別參數
uptrends = analyzer.identify_gentle_uptrend(
    min_slope=0.05,  # 最小斜率
    max_slope=1.5,   # 最大斜率
    min_days=15      # 最少持續天數
)
```

### 批量處理
```python
# 批量分析多檔股票
stocks = ['2330.TW', '2454.TW', '2317.TW']
results = []

for stock in stocks:
    analyzer = StockAnalyzer()
    if analyzer.fetch_data(stock):
        signals = analyzer.generate_trading_signals()
        results.append({
            'symbol': stock,
            'signals': signals
        })
```

## 🏦 永豐金證券 Shioaji API 使用說明

### 環境設定
1. 在專案根目錄創建 `.env` 檔案
2. 設定以下環境變數：
```env
API_KEY=你的API金鑰
SECRET_KEY=你的秘密金鑰
CA_CERT_PATH=憑證檔案路徑
CA_PASSWORD=憑證密碼
```

### 逐筆交易功能 ⚡
使用 `api.ticks` 獲取即時交易資料：

#### 1. 最近N筆交易
```python
# 獲取最近10筆交易
client.get_realtime_ticks("2330", last_cnt=10)
```

#### 2. 時間範圍查詢
```python
# 獲取9點到10點的交易資料
client.get_ticks_by_time_range("2330", "09:00:00", "10:00:00")
```

#### 3. 資料內容
- **時間**：精確到毫秒的交易時間
- **價格**：成交價格
- **成交量**：單筆成交量
- **買賣別**：買盤/賣盤/中性

### 功能選單
執行 `python shioaji_extended.py` 可使用完整功能：
1. 搜尋股票
2. 即時報價
3. 即時逐筆交易 (最近N筆)
4. 時間範圍逐筆交易
5. 歷史數據
6. 帳戶資訊
7. 調試合約結構

## 📞 技術支援

如有問題或建議，歡迎聯繫：

- 問題回報：請提供詳細的錯誤信息和重現步驟
- 功能建議：歡迎提出新功能需求
- 技術交流：討論技術分析策略和改進方案

## 📝 更新日誌

### v1.1.0 (2024-12-19)
- ✅ **新增 Shioaji API 逐筆交易功能**
- ✅ 使用 `api.ticks` 獲取即時交易資料
- ✅ 支援最近N筆交易查詢
- ✅ 支援時間範圍交易查詢
- ✅ 詳細的交易統計資訊
- ✅ 買賣盤識別功能

### v1.0.0 (2024-12-19)
- ✅ 基本技術分析功能
- ✅ 黃藍線交叉檢測
- ✅ 緩坡爬升識別
- ✅ 利潤空間計算
- ✅ 股票篩選器
- ✅ 網頁界面
- ✅ 互動式圖表

## 🤝 貢獻指南

歡迎貢獻代碼！請遵循以下步驟：

1. Fork 本專案
2. 創建功能分支 (`git checkout -b feature/新功能`)
3. 提交更改 (`git commit -am '添加新功能'`)
4. 推送分支 (`git push origin feature/新功能`)
5. 創建 Pull Request

## 📄 授權協議

本專案採用 MIT 授權協議 - 詳見 LICENSE 文件

---

**免責聲明**：本軟體僅供教育和研究目的使用。投資決策應基於您自己的研究和判斷，作者不對任何投資損失承擔責任。 