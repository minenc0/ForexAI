import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="Forex Correlation AI Agent",
    page_icon="📈",
    layout="wide"
)

# ==========================================
# DATA HARGA
# ==========================================

prices = {
    "EURUSD": 1.15912,
    "AUDUSD": 0.64800,
    "EURCAD": 1.58500,
    "GBPUSD": 1.34300,
    "NZDUSD": 0.60200,
    "GBPCAD": 1.83600,
    "USDCHF": 0.78500,
    "USDCAD": 1.38200
}

# ==========================================
# KORELASI
# ==========================================

correlation = {

    "EURUSD": {
        "positive": ["GBPUSD", "AUDUSD", "NZDUSD"],
        "negative": ["USDCHF", "USDCAD"]
    },

    "GBPUSD": {
        "positive": ["EURUSD", "AUDUSD", "NZDUSD"],
        "negative": ["USDCHF", "USDCAD"]
    },

    "AUDUSD": {
        "positive": ["EURUSD", "GBPUSD", "NZDUSD"],
        "negative": ["USDCHF", "USDCAD"]
    },

    "NZDUSD": {
        "positive": ["EURUSD", "GBPUSD", "AUDUSD"],
        "negative": ["USDCHF", "USDCAD"]
    },

    "USDCHF": {
        "positive": ["USDCAD"],
        "negative": ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"]
    },

    "USDCAD": {
        "positive": ["USDCHF"],
        "negative": ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"]
    },

    "EURCAD": {
        "positive": ["GBPCAD"],
        "negative": []
    },

    "GBPCAD": {
        "positive": ["EURCAD"],
        "negative": []
    }
}

# ==========================================
# FUNGSI
# ==========================================

def calc_buy(price, sl_percent, tp_percent):

    sl = price * (1 - sl_percent / 100)
    tp = price * (1 + tp_percent / 100)

    return round(sl, 5), round(tp, 5)

def calc_sell(price, sl_percent, tp_percent):

    sl = price * (1 + sl_percent / 100)
    tp = price * (1 - tp_percent / 100)

    return round(sl, 5), round(tp, 5)

def generate(pair, entry, sl_percent, tp_percent):

    prices[pair] = entry

    buy_result = []
    sell_result = []

    # Pair Acuan

    sl,tp = calc_buy(entry, sl_percent, tp_percent)

    buy_result.append([
        pair,
        "BUY",
        entry,
        sl,
        tp
    ])

    sl,tp = calc_sell(entry, sl_percent, tp_percent)

    sell_result.append([
        pair,
        "SELL",
        entry,
        sl,
        tp
    ])

    # Positif

    for p in correlation[pair]["positive"]:

        price = prices[p]

        sl,tp = calc_buy(price, sl_percent, tp_percent)

        buy_result.append([
            p,
            "BUY",
            price,
            sl,
            tp
        ])

        sl,tp = calc_sell(price, sl_percent, tp_percent)

        sell_result.append([
            p,
            "SELL",
            price,
            sl,
            tp
        ])

    # Negatif

    for p in correlation[pair]["negative"]:

        price = prices[p]

        sl,tp = calc_sell(price, sl_percent, tp_percent)

        buy_result.append([
            p,
            "SELL",
            price,
            sl,
            tp
        ])

        sl,tp = calc_buy(price, sl_percent, tp_percent)

        sell_result.append([
            p,
            "BUY",
            price,
            sl,
            tp
        ])

    buy_df = pd.DataFrame(
        buy_result,
        columns=["PAIR","DIRECTION","ENTRY","SL","TP"]
    )

    sell_df = pd.DataFrame(
        sell_result,
        columns=["PAIR","DIRECTION","ENTRY","SL","TP"]
    )

    return buy_df, sell_df

# ==========================================
# UI
# ==========================================

st.title("📈 Forex Correlation AI Agent")

col1,col2,col3,col4 = st.columns(4)

with col1:

    pair = st.selectbox(
        "Pair Acuan",
        list(prices.keys())
    )

with col2:

    entry = st.number_input(
        "Harga Entry",
        value=float(prices[pair]),
        format="%.5f"
    )

with col3:

    sl_percent = st.number_input(
        "SL %",
        value=0.17,
        step=0.01,
        format="%.2f"
    )

with col4:

    tp_percent = st.number_input(
        "TP %",
        value=0.34,
        step=0.01,
        format="%.2f"
    )

rr = tp_percent / sl_percent

st.info(f"Risk Reward = 1 : {rr:.2f}")

if st.button("🚀 GENERATE REPORT", use_container_width=True):

    buy_df, sell_df = generate(
        pair,
        entry,
        sl_percent,
        tp_percent
    )

    st.success("Report berhasil dibuat")

    tab1,tab2 = st.tabs([
        "BUY SCENARIO",
        "SELL SCENARIO"
    ])

    with tab1:
        st.dataframe(
            buy_df,
            use_container_width=True
        )

    with tab2:
        st.dataframe(
            sell_df,
            use_container_width=True
        )

    os.makedirs(
        "reports",
        exist_ok=True
    )

    filename = (
        "reports/"
        f"Forex_AI_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

    with pd.ExcelWriter(filename) as writer:

        buy_df.to_excel(
            writer,
            sheet_name="BUY",
            index=False
        )

        sell_df.to_excel(
            writer,
            sheet_name="SELL",
            index=False
        )

    with open(filename, "rb") as f:

        st.download_button(
            "📥 Download Excel",
            data=f,
            file_name=os.path.basename(filename),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
