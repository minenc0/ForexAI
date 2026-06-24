import streamlit as st
import pandas as pd

st.set_page_config(page_title="Forex Correlation AI Agent", layout="wide")

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

correlation = {
    "EURUSD":{"positive":["GBPUSD","AUDUSD","NZDUSD"],"negative":["USDCHF","USDCAD"]},
    "GBPUSD":{"positive":["EURUSD","AUDUSD","NZDUSD"],"negative":["USDCHF","USDCAD"]},
    "AUDUSD":{"positive":["EURUSD","GBPUSD","NZDUSD"],"negative":["USDCHF","USDCAD"]},
    "NZDUSD":{"positive":["EURUSD","GBPUSD","AUDUSD"],"negative":["USDCHF","USDCAD"]},
    "USDCHF":{"positive":["USDCAD"],"negative":["EURUSD","GBPUSD","AUDUSD","NZDUSD"]},
    "USDCAD":{"positive":["USDCHF"],"negative":["EURUSD","GBPUSD","AUDUSD","NZDUSD"]},
    "EURCAD":{"positive":["GBPCAD"],"negative":[]},
    "GBPCAD":{"positive":["EURCAD"],"negative":[]}
}

def calc_buy(price, slp, tpp):
    return round(price*(1-slp/100),5), round(price*(1+tpp/100),5)

def calc_sell(price, slp, tpp):
    return round(price*(1+slp/100),5), round(price*(1-tpp/100),5)

st.title("Forex Correlation AI Agent")

uploaded = st.file_uploader("Upload CSV harga (opsional)", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df, use_container_width=True)

c1,c2,c3,c4 = st.columns(4)
with c1:
    pair = st.selectbox("Pair Acuan", list(prices.keys()))
with c2:
    entry = st.number_input("Harga Entry", value=float(prices[pair]), format="%.5f")
with c3:
    sl = st.number_input("SL %", value=0.17, step=0.01)
with c4:
    tp = st.number_input("TP %", value=0.34, step=0.01)

if st.button("Generate"):
    hasil = []

    s,tpv = calc_buy(entry, sl, tp)
    hasil.append([pair,"BUY",entry,s,tpv])

    for p in correlation[pair]["positive"]:
        s,tpv = calc_buy(prices[p], sl, tp)
        hasil.append([p,"BUY",prices[p],s,tpv])

    for p in correlation[pair]["negative"]:
        s,tpv = calc_sell(prices[p], sl, tp)
        hasil.append([p,"SELL",prices[p],s,tpv])

    st.dataframe(pd.DataFrame(hasil,
        columns=["PAIR","DIRECTION","ENTRY","SL","TP"]),
        use_container_width=True)
