import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from stock_analyzer import StockAnalyzer
from stock_screener import StockScreener
import time
from shioaji_extended import ShioajiExtended
from shioaji import TickSTKv1, Exchange
import threading

# 設置頁面配置
st.set_page_config(
    page_title="股票技術分析系統",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem 0;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
.warning-box {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    color: #856404;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# 主標題
st.markdown('<h1 class="main-header">📈 股票技術分析系統</h1>', unsafe_allow_html=True)

# 側邊欄
st.sidebar.title("🔧 功能選單")
app_mode = st.sidebar.selectbox(
    "選擇功能",
    ["個股分析", "當日即時分析", "股票篩選器", "批量比較", "關於系統"]
)

if app_mode == "個股分析":
    st.header("📊 個股技術分析")
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        symbol = st.text_input(
            "輸入股票代碼 (例: 2330.TW, AAPL)",
            value="2330.TW",
            help="台股請加上.TW後綴，美股直接輸入代碼"
        )
    
    with col2:
        period = st.selectbox(
            "分析期間",
            ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3,
            help="選擇數據分析的時間範圍"
        )

    with col3:
        interval = st.selectbox(
            "數據週期",
            ["1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"],
            index=0,
            help="選擇要獲取的原始數據K線週期"
        )

    with col4:
        resample_to = st.selectbox(
            "轉換為",
            ["(不轉換)", "1d", "1wk", "1mo"],
            index=1,
            help="將獲取的數據轉換為指定的K線週期"
        )
    
    if st.button("🔍 開始分析", type="primary"):
        if symbol:
            with st.spinner("正在獲取數據並進行分析..."):
                analyzer = StockAnalyzer()
                
                if analyzer.fetch_data(symbol, period=period, interval=interval):
                    # 如果使用者選擇了轉換週期，則執行重採樣
                    if resample_to != "(不轉換)":
                        analyzer.resample_data(resample_to)

                    # 執行分析 (這一步會計算所有指標)
                    analyzer.analyze()
                    
                    # 生成交易信號
                    signals = analyzer.generate_trading_signals()
                    
                    # 顯示基本信息
                    current_price = analyzer.data['Close'][-1]
                    price_change = analyzer.data['Close'][-1] - analyzer.data['Close'][-2]
                    price_change_pct = (price_change / analyzer.data['Close'][-2]) * 100
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "當前價格",
                            f"${current_price:.2f}",
                            f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
                        )
                    
                    with col2:
                        st.metric(
                            "交叉點數量",
                            len(signals['crossovers']),
                            "個交叉點"
                        )
                    
                    with col3:
                        st.metric(
                            "上升趨勢",
                            len(signals['uptrends']),
                            "個趨勢段"
                        )
                    
                    with col4:
                        if signals['profit_analysis']:
                            avg_profit = sum(p['profit_potential'] for p in signals['profit_analysis']) / len(signals['profit_analysis'])
                            st.metric(
                                "平均利潤空間",
                                f"{avg_profit:.1f}%",
                                "歷史平均"
                            )
                        else:
                            st.metric("平均利潤空間", "N/A", "無數據")
                    
                    # 顯示圖表
                    st.subheader("📈 技術分析圖表")
                    fig = analyzer.create_interactive_chart()
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # 顯示詳細分析
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("🔄 黃藍線交叉分析")
                        if signals['crossovers']:
                            crossover_df = pd.DataFrame(signals['crossovers'])
                            crossover_df['date'] = crossover_df['date'].dt.strftime('%Y-%m-%d')
                            crossover_df = crossover_df.rename(columns={
                                'date': '日期',
                                'price': '價格',
                                'type': '類型',
                                'signal': '信號'
                            })
                            st.dataframe(crossover_df, use_container_width=True)
                        else:
                            st.info("未發現明顯的交叉點")
                    
                    with col2:
                        st.subheader("📈 緩坡爬升趨勢")
                        if signals['uptrends']:
                            uptrend_data = []
                            for trend in signals['uptrends']:
                                gain = ((trend['end_price'] - trend['start_price']) / trend['start_price']) * 100
                                uptrend_data.append({
                                    '開始日期': trend['start_date'].strftime('%Y-%m-%d'),
                                    '結束日期': trend['end_date'].strftime('%Y-%m-%d'),
                                    '持續天數': trend['duration_days'],
                                    '漲幅(%)': f"{gain:.2f}%"
                                })
                            uptrend_df = pd.DataFrame(uptrend_data)
                            st.dataframe(uptrend_df, use_container_width=True)
                        else:
                            st.info("未發現明顯的緩坡爬升趨勢")
                    
                    # 利潤空間分析
                    if signals['profit_analysis']:
                        st.subheader("💰 利潤空間分析")
                        profit_data = []
                        for profit in signals['profit_analysis']:
                            profit_data.append({
                                '交叉日期': profit['crossover_date'].strftime('%Y-%m-%d'),
                                '交叉價格': f"{profit['crossover_price']:.2f}",
                                '天花板價格': f"{profit['ceiling_price']:.2f}",
                                '利潤空間(%)': f"{profit['profit_potential']:.2f}%",
                                '到達天數': profit['distance_days']
                            })
                        profit_df = pd.DataFrame(profit_data)
                        st.dataframe(profit_df, use_container_width=True)
                    
                    # 交易建議
                    st.subheader("💡 交易建議")
                    recent_crossovers = [c for c in signals['crossovers'] 
                                       if (analyzer.data.index[-1] - c['date']).days <= 10]
                    
                    if recent_crossovers:
                        latest_signal = recent_crossovers[-1]
                        if latest_signal['signal'] == 'BUY':
                            st.markdown(
                                f'<div class="success-box">🟢 <strong>買入信號</strong><br>'
                                f'最近在 {latest_signal["date"].strftime("%Y-%m-%d")} 出現黃金交叉，'
                                f'建議關注後續走勢。</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f'<div class="warning-box">🔴 <strong>賣出信號</strong><br>'
                                f'最近在 {latest_signal["date"].strftime("%Y-%m-%d")} 出現死亡交叉，'
                                f'建議謹慎操作。</div>',
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("目前沒有明確的交易信號，建議繼續觀察。")
                    
                else:
                    st.error(f"無法獲取 {symbol} 的數據，請檢查股票代碼是否正確。")
        else:
            st.warning("請輸入股票代碼")

elif app_mode == "當日即時分析":
    st.header("📈 當日個股即時分析")

    # --- 狀態初始化 ---
    if 'shioaji_client' not in st.session_state:
        st.session_state.shioaji_client = None
    if 'tick_data' not in st.session_state:
        st.session_state.tick_data = []
    if 'subscribed_stock' not in st.session_state:
        st.session_state.subscribed_stock = None
    if 'lock' not in st.session_state:
        st.session_state.lock = threading.Lock()

    # --- 連接 API ---
    if st.session_state.shioaji_client is None:
        with st.spinner("正在連接 Shioaji API..."):
            client = ShioajiExtended()
            if client.connect():
                st.session_state.shioaji_client = client
                client.api.usage()
                st.success("Shioaji API 連接成功！")
                st.rerun()
            else:
                st.error("Shioaji API 連接失敗，請檢查 .env 設定檔。")
                st.stop()
    
    api = st.session_state.shioaji_client.api

    # --- 定義 Callback 函數 ---
    def quote_callback(exchange: Exchange, tick: TickSTKv1):
        with st.session_state.lock:
            # 確保 tick_data 是最新的
            if len(st.session_state.tick_data) > 500: # 最多保留最近500筆
                st.session_state.tick_data.pop(0)
            
            st.session_state.tick_data.append({
                '時間': pd.to_datetime(tick.ts, unit='ns').strftime('%H:%M:%S.%f')[:-3],
                '價格': tick.close,
                '成交量': tick.volume,
                '買賣別': '買盤' if tick.tick_type == 1 else '賣盤' if tick.tick_type == -1 else '中性'
            })

    #api.set_on_tick_stk_v1(quote_callback)
    api.quote.set_on_tick_stk_v1_callback(quote_callback)

    # --- UI 介面 ---
    stock_code = st.text_input("輸入股票代碼 (例: 2330)", value=st.session_state.get("subscribed_stock", "2330"))

    col1, col2 = st.columns(2)
    is_subscribed = st.session_state.subscribed_stock is not None

    with col1:
        if st.button("🚀 開始訂閱", disabled=is_subscribed, type="primary"):
            if stock_code:
                with st.spinner(f"正在訂閱 {stock_code}..."):
                    with st.session_state.lock:
                        st.session_state.tick_data.clear()
                    
                    st.session_state.subscribed_stock = stock_code
                    contract = api.Contracts.Stocks[stock_code]
                    api.quote.subscribe(contract, quote_type='tick', version='v1')
                    st.rerun()

    with col2:
        if st.button("🛑 停止訂閱", disabled=not is_subscribed):
            if st.session_state.subscribed_stock:
                with st.spinner(f"正在取消訂閱 {st.session_state.subscribed_stock}..."):
                    contract = api.Contracts.Stocks[st.session_state.subscribed_stock]
                    api.quote.unsubscribe(contract, quote_type='tick')
                    st.session_state.subscribed_stock = None
                    st.rerun()

    # --- 顯示即時數據與自動刷新 ---
    if st.session_state.subscribed_stock:
        st.success(f"已訂閱 {st.session_state.subscribed_stock} 的即時 Tick 資訊。每秒自動更新...")
        
        placeholder = st.empty()

        with st.session_state.lock:
            df = pd.DataFrame(st.session_state.tick_data)

        if not df.empty:
            # 顯示指標
            latest_price = df['價格'].iloc[-1]
            high_price = df['價格'].max()
            low_price = df['價格'].min()
            total_volume = df['成交量'].sum()

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("最新價格", f"{latest_price:.2f}")
            c2.metric("今日最高", f"{high_price:.2f}")
            c3.metric("今日最低", f"{low_price:.2f}")
            c4.metric("總成交量", f"{total_volume:,}")

            # 顯示圖表和表格
            with placeholder.container():
                st.subheader("價格走勢")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['時間'], y=df['價格'], mode='lines', name='價格'))
                fig.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("最新逐筆交易 (最近20筆)")
                st.dataframe(df.tail(20).iloc[::-1], use_container_width=True) # 反轉順序，最新在最上面
        else:
            st.info("正在等待接收第一筆資料...")

        time.sleep(1)
        st.rerun()

elif app_mode == "股票篩選器":
    st.header("🔍 智能股票篩選器")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("篩選條件")
        min_score = st.slider("最低評分", 0, 100, 60, help="設定股票評分的最低門檻")
        
    with col2:
        st.subheader("股票池")
        use_custom_list = st.checkbox("使用自定義股票清單")
        
        if use_custom_list:
            custom_stocks = st.text_area(
                "輸入股票代碼 (每行一個)",
                value="2330.TW\n2454.TW\n2317.TW",
                help="每行輸入一個股票代碼"
            )
            stock_list = [s.strip() for s in custom_stocks.split('\n') if s.strip()]
        else:
            stock_list = None
    
    if st.button("🚀 開始篩選", type="primary"):
        with st.spinner("正在篩選股票，請稍候..."):
            screener = StockScreener()
            screener.load_stock_list(stock_list)
            
            # 顯示進度
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = screener.screen_stocks(min_score=min_score)
            
            progress_bar.progress(100)
            status_text.text(f"篩選完成！找到 {len(results)} 檔符合條件的股票")
            
            if results:
                st.success(f"🎉 成功找到 {len(results)} 檔優質股票！")
                
                # 顯示結果表格
                result_data = []
                for i, result in enumerate(results, 1):
                    result_data.append({
                        '排名': i,
                        '股票代碼': result['symbol'],
                        '當前價格': f"{result['current_price']:.2f}",
                        '評分': f"{result['score']:.1f}",
                        '交叉點': len(result['signals']['crossovers']),
                        '上升趨勢': len(result['signals']['uptrends'])
                    })
                
                result_df = pd.DataFrame(result_data)
                st.dataframe(result_df, use_container_width=True)
                
                # 顯示比較圖表
                if len(results) > 0:
                    st.subheader("📊 前5名股票走勢比較")
                    comparison_chart = screener.create_comparison_chart(top_n=min(5, len(results)))
                    if comparison_chart:
                        st.plotly_chart(comparison_chart, use_container_width=True)
                
                # 詳細分析選項
                st.subheader("🔍 詳細分析")
                selected_rank = st.selectbox(
                    "選擇要查看詳細分析的股票排名",
                    range(1, min(11, len(results) + 1))
                )
                
                if st.button("查看詳細分析"):
                    selected_result = results[selected_rank - 1]
                    analyzer = selected_result['analyzer']
                    
                    st.write(f"### {selected_result['symbol']} 詳細分析")
                    
                    # 創建詳細圖表
                    detail_chart = analyzer.create_interactive_chart()
                    if detail_chart:
                        st.plotly_chart(detail_chart, use_container_width=True)
            else:
                st.warning("沒有找到符合條件的股票，請調整篩選條件後重試。")

elif app_mode == "批量比較":
    st.header("📊 股票批量比較")
    
    stocks_input = st.text_area(
        "輸入要比較的股票代碼 (每行一個)",
        value="2330.TW\n2454.TW\n2317.TW\n0050.TW",
        height=150
    )
    
    period = st.selectbox("比較期間", ["1d", "1mo", "3mo", "6mo", "1y"], index=2)
    
    if st.button("開始比較分析"):
        stock_list = [s.strip() for s in stocks_input.split('\n') if s.strip()]
        
        if stock_list:
            comparison_data = []
            charts_data = {}
            
            progress_bar = st.progress(0)
            
            for i, symbol in enumerate(stock_list):
                progress_bar.progress((i + 1) / len(stock_list))
                
                analyzer = StockAnalyzer()
                if analyzer.fetch_data(symbol, period=period):
                    signals = analyzer.generate_trading_signals()
                    current_price = analyzer.data['Close'][-1]
                    price_change_pct = ((current_price - analyzer.data['Close'][0]) / analyzer.data['Close'][0]) * 100
                    
                    comparison_data.append({
                        '股票代碼': symbol,
                        '當前價格': current_price,
                        '期間漲跌(%)': price_change_pct,
                        '交叉點數': len(signals['crossovers']),
                        '上升趨勢數': len(signals['uptrends']),
                        '平均利潤空間(%)': np.mean([p['profit_potential'] for p in signals['profit_analysis']]) if signals['profit_analysis'] else 0
                    })
                    
                    charts_data[symbol] = analyzer.data
            
            progress_bar.progress(100)
            
            if comparison_data:
                # 顯示比較表格
                comparison_df = pd.DataFrame(comparison_data)
                st.subheader("📈 比較結果")
                st.dataframe(comparison_df, use_container_width=True)
                
                # 創建比較圖表
                fig = go.Figure()
                
                for symbol, data in charts_data.items():
                    # 標準化價格（以第一天為基準）
                    normalized_price = (data['Close'] / data['Close'].iloc[0]) * 100
                    
                    # 格式化日期為只顯示日期部分
                    formatted_dates = [date.strftime('%Y-%m-%d') for date in data.index]
                    
                    fig.add_trace(go.Scatter(
                        x=formatted_dates,
                        y=normalized_price,
                        mode='lines',
                        name=symbol,
                        line=dict(width=2)
                    ))
                
                fig.update_layout(
                    title="股票價格走勢比較（標準化）",
                    xaxis_title="日期",
                    yaxis_title="相對價格變化 (%)",
                    height=600,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 績效排名
                st.subheader("🏆 績效排名")
                performance_ranking = comparison_df.sort_values('期間漲跌(%)', ascending=False)
                
                for i, (_, row) in enumerate(performance_ranking.iterrows(), 1):
                    col1, col2, col3 = st.columns([1, 2, 2])
                    
                    with col1:
                        if i == 1:
                            st.markdown("🥇")
                        elif i == 2:
                            st.markdown("🥈")
                        elif i == 3:
                            st.markdown("🥉")
                        else:
                            st.markdown(f"#{i}")
                    
                    with col2:
                        st.markdown(f"**{row['股票代碼']}**")
                    
                    with col3:
                        color = "green" if row['期間漲跌(%)'] > 0 else "red"
                        st.markdown(f"<span style='color: {color}'>{row['期間漲跌(%)']:+.2f}%</span>", 
                                  unsafe_allow_html=True)

elif app_mode == "關於系統":
    st.header("ℹ️ 關於股票技術分析系統")
    
    st.markdown("""
    ### 🎯 系統特色
    
    這套股票技術分析系統專門設計來識別以下交易機會：
    
    1. **緩坡爬升趨勢** 📈
       - 識別穩定的上升趨勢
       - 過濾掉過於陡峭或不穩定的走勢
       - 適合中長期投資策略
    
    2. **黃藍線交叉點** ⚡
       - 黃線：5日指數移動平均線 (EMA5)（短期趨勢）
       - 藍線：20日指數移動平均線 (EMA20)（中期趨勢）
       - 黃金交叉：買入信號
       - 死亡交叉：賣出信號
    
    3. **利潤空間評估** 💰
       - 計算從交叉點到後續高點的利潤空間
       - 評估風險回報比
       - 提供歷史統計數據
    
    ### 🔧 技術指標說明
    
    - **EMA5/EMA20/EMA60**：指數移動平均線系統
    - **支撐線/阻力線**：動態支撐阻力位
    - **趨勢斜率**：量化趨勢強度
    - **交叉點檢測**：自動識別交易信號
    
    ### 📊 評分系統
    
    系統會根據以下因素給股票評分（0-100分）：
    
    - **緩坡爬升趨勢**（30分）：近期上升趨勢的品質
    - **黃金交叉**（25分）：是否有近期的買入信號
    - **利潤空間**（25分）：歷史利潤空間的平均值
    - **技術指標**（20分）：當前技術面的健康度
    
    ### ⚠️ 風險提示
    
    - 本系統僅供參考，不構成投資建議
    - 技術分析有其局限性，請結合基本面分析
    - 投資有風險，請謹慎操作
    - 建議設置停損點，控制風險
    
    ### 💡 使用建議
    
    1. **個股分析**：深入分析單一股票的技術面
    2. **股票篩選**：從大量股票中找出符合條件的標的
    3. **批量比較**：比較多檔股票的相對表現
    
    ---
    
    **版本**：v1.0  
    **更新日期**：2024年  
    **技術支持**：基於 Python、Streamlit、Plotly 開發
    """)

# 側邊欄附加信息
st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 技術支持")
st.sidebar.info(
    "如有問題或建議，請聯繫開發團隊。\n\n"
    "本系統持續更新中，感謝您的使用！"
)

st.sidebar.markdown("### 📈 市場提醒")
st.sidebar.warning(
    "投資有風險，入市需謹慎。\n\n"
    "技術分析僅供參考，請結合基本面分析做出投資決策。"
) 