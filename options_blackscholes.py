import yfinance as yf
import streamlit as st
from scipy.stats import norm
import seaborn as sn
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def d1(price, strike, rf, years, volatility):
    '''returns the d1 of the Black-Scholes formula'''
    return (np.log(price/strike)+years*(rf+np.pow(volatility, 2)/2))/(volatility*np.sqrt(years))

def d2(price, strike, rf, years, volatility):
    '''returns the d2 of the Black-Scholes formula'''
    return d1(price, strike, rf, years, volatility) - volatility*np.sqrt(years)

def call_value(price, strike, rf, years, volatility):
    '''returns the call premium cost using the Black-Scholes formula'''
    d1_val = d1(price, strike, rf, years, volatility)
    d2_val = d2(price, strike, rf, years, volatility)
    return price*norm.cdf(d1_val)-strike*np.exp(-rf*years)*norm.cdf(d2_val)

def put_value(price, strike, rf, years, volatility):
    '''returns the put premium cost using the Black-Scholes formula'''
    d1_val = d1(price, strike, rf, years, volatility)
    d2_val = d2(price, strike, rf, years, volatility)
    return strike*np.exp(-rf*years)*norm.cdf(-d2_val)-price*norm.cdf(-d1_val)

def heat_map(col, row, title):
    '''forms the asset price vs volatility heat map'''
    st.title(f"{title} Price Map")
    plt.figure(figsize=(10,10))
    sn.heatmap(data=data_call, annot=True, fmt=".2f", cmap="flare", xticklabels=col, yticklabels=row, square=True, cbar_kws={"shrink":0.8})
    plt.xlabel("Asset Price")
    plt.ylabel("volatility")
    st.pyplot(plt)
    plt.close(None)

def print_value(price, strike, rf, years, volatility):
    '''prints the call and put values to the screen'''
    with col1:
        st.subheader("The call value at these values is")
        st.title(f":green-background[{round(call_value(price, strike, rf, years, volatility), 2)}]")

    with col2:
        st.subheader("The put value at these values is")
        st.title(f":red-background[{round(put_value(price, strike, rf, years, volatility), 2)}]")

def print_value_tick(price, strike, rf, years, volatility):
    '''prints the call and put values to the screen'''
    with col1:
        st.subheader("The call value at these values is")
        st.title(f":green-background[{round(call_value(price, strike, rf, years, volatility)[0], 2)}]")

    with col2:
        st.subheader("The put value at these values is")
        st.title(f":red-background[{round(put_value(price, strike, rf, years, volatility)[0], 2)}]")

def delta(option_type, price, strike, rf, years, volatility):
    '''returns the delta of the option'''
    if option_type == "call":
        return norm.cdf(d1(price, strike, rf, years, volatility))
    elif option_type == "put":
        return norm.cdf(d1(price, strike, rf, years, volatility))-1

def rho(option_type, price, strike, rf, years, volatility):
    '''returns the rho of the option'''
    if option_type == "call":
        return (strike*years*np.exp(-rf*years)*norm.cdf(d2(price, strike, rf, years, volatility)))/100
    elif option_type == "put":
        return (-strike*years*np.exp(-rf*years)*norm.cdf(-d2(price, strike, rf, years, volatility)))/100

#setting up the page layout
st.set_page_config(layout="wide")
st.title("Black-Scholes Pricing Model")
col1, col2 = st.columns(2)

#creating needed variables and adding them to the screen
st.sidebar.title("Black-Scholes Model")

choice = st.sidebar.checkbox("Check if you want to enter a ticker")
if choice:
    ticker = st.sidebar.text_input("Type in a ticker", "temp")
        
    #grabbing api data for asset price, and to calculate volatility
    data = yf.download(ticker, period="1y", interval="1d")
    data['log_return'] = np.log(data['Close'] / data['Close'].shift(1))

    #creating the values
    rfir = 0.045
    cap = data["Close"].iloc[-1]
    print_cap = round(cap[0], 2)

    #printing out current stock value
    st.sidebar.write(f"Current {ticker.upper()} price: {print_cap}")

    #grabbing user inputted data
    sp = st.sidebar.number_input("Strike Price", value=100.00, step=0.01, min_value=0.0, max_value=9999.00, format="%.2f")
    ty = st.sidebar.number_input("Time to Maturity (Years)", value=1.00, step=0.01, min_value=0.0, max_value=9999.00, format="%.4f")
    
    #performing volatility calculation
    vol = data["log_return"].std() * np.sqrt(252)

    #printing out the call and put values
    print_value_tick(cap, sp, rfir, ty, vol)

else:
    #grabbing user inputted data
    ticker = "N/A"
    cap = st.sidebar.number_input("Current Asset Price", value=80.00, step=0.01, min_value=0.0, max_value=9999.00, format="%.2f")
    sp = st.sidebar.number_input("Strike Price", value=100.00, step=0.01, min_value=0.0, max_value=9999.00, format="%.2f")
    ty = st.sidebar.number_input("Time to Maturity", value=1.00, step=0.01, min_value=0.0, max_value=9999.00, format="%.4f")
    vol = st.sidebar.number_input("Volatility", value=0.20, step=0.01, min_value=0.0, max_value=9999.00, format="%.2f")
    rfir = st.sidebar.number_input("Risk-Free Interest rate", value=0.05, step=0.01, min_value=0.0, max_value=9999.00, format="%.2f")

    #printing out the call and put values
    print_value(cap, sp, rfir, ty, vol)

#grabbing user inputted/generated data for the heatmap parameters
st.sidebar.write("--------------------------")
st.sidebar.subheader("Heatmap Parameters")
min_vol = st.sidebar.slider("Min volatility", 0.01, 1.00, vol*0.5)
max_vol = st.sidebar.slider("Max Volatility", 0.01, 1.00, vol*1.5)
min_price = st.sidebar.number_input("Min Price", value=cap.iloc[0] * 0.8 if isinstance(cap, pd.Series) else cap * 0.8, step=0.01, min_value=0.0, max_value=9999.00, format="%.2f")
max_price = st.sidebar.number_input("Max Price", value=cap.iloc[0] * 1.2 if isinstance(cap, pd.Series) else cap * 1.2, step=0.01, min_value=0.0, max_value=9999.00, format="%.2f")

#the heatmaps are being setup here
st.title("Options Heatmap")
st.subheader("An interactive options heatmap to represent the different values you can get at different spot values and volatility")

col1, col2 = st.columns(2)

#creating the values to multiply for the heatmap
rows = [(min_vol + i*(max_vol-min_vol)/9) for i in range(0, 10)] #volatility (y-axis)
columns = [(min_price + i*(max_price-min_price)/9) for i in range(0, 10)] #spot price (x-axis)

#printing out the x-axis and y-axis values for the heatmap
rows_print = [round((min_vol + i*(max_vol-min_vol)/9), 2) for i in range(0, 10)]
columns_print = [round((min_price + i*(max_price-min_price)/9), 2) for i in range(0, 10)]

#creating the 2d matrix's for the heat maps
data_call = []
data_put = []
for i in range(len(rows)):
    data_call_row = []
    data_put_row = []
    for j in range(len(columns)):
        call_val = call_value(columns[j], sp, rfir, ty, rows[i])
        put_val = put_value(columns[j], sp, rfir, ty, rows[i])
        data_call_row.append(call_val)
        data_put_row.append(put_val)
    data_call.append(data_call_row)
    data_put.append(data_put_row)

#outputting the heatmaps to the screen
with col1:  
    heat_map(columns_print, rows_print, "Call")\

with col2:
    heat_map(columns_print, rows_print, "Put")

#outputting the values for the greeks
st.title("Here are greek values for the call/put")
col1, col2 = st.columns(2)

if choice:
    with col1:
        st.subheader("the delta of the call")
        st.header(f":green-background[{round(delta("call", cap, sp, rfir, ty, vol)[0], 3)}]")
        st.subheader("the rho of the call")
        st.header(f":green-background[{round(rho("call", cap, sp, rfir, ty, vol)[0], 3)}]")

    with col2:
        st.subheader("the delta of the put")
        st.header(f":red-background[{round(delta("put", cap, sp, rfir, ty, vol)[0], 3)}]")
        st.subheader("the rho of the put")
        st.header(f":red-background[{round(rho("put", cap, sp, rfir, ty, vol)[0], 3)}]")
else:
    with col1:
        st.subheader("the delta of the call")
        st.header(f":green-background[{round(delta("call", cap, sp, rfir, ty, vol), 3)}]")
        st.subheader("the rho of the call")
        st.header(f":green-background[{round(rho("call", cap, sp, rfir, ty, vol), 3)}]")

    with col2:
        st.subheader("the delta of the put")
        st.header(f":red-background[{round(delta("put", cap, sp, rfir, ty, vol), 3)}]")
        st.subheader("the rho of the put")
        st.header(f":red-background[{round(rho("put", cap, sp, rfir, ty, vol), 3)}]")

#creating the information to be downloaded
if choice:
    content = f'''Ticker: {ticker.upper()}
    Asset Price: {cap}
    Strike Price: {sp}
    Time to Maturity (years:days): {ty}:{ty*365}
    Risk-Free Interest Rate: {rfir}
    Volatility: {vol}
    Call Premium: {round(call_value(cap, sp, rfir, ty, vol)[0], 4)}
    Put Premium: {round(put_value(cap, sp, rfir, ty, vol)[0], 4)}
    Call Delta: {round(delta("call", cap, sp, rfir, ty, vol)[0], 3)}
    Put Delta: {round(delta("put", cap, sp, rfir, ty, vol)[0], 3)}
    Call Rho: {round(rho("call", cap, sp, rfir, ty, vol)[0], 3)}
    Put Rho: {round(rho("put", cap, sp, rfir, ty, vol)[0], 3)}
    '''
    st.sidebar.write("--------------------------")
    st.sidebar.download_button("Download information", content, "results.txt")
else:
    content = f'''Ticker: {ticker.upper()}
    Asset Price: {cap}
    Strike Price: {sp}
    Time to Maturity (years:days): {ty}:{ty*365}
    Risk-Free Interest Rate: {rfir}
    Volatility: {vol}
    Call Premium: {round(call_value(cap, sp, rfir, ty, vol), 4)}
    Put Premium: {round(put_value(cap, sp, rfir, ty, vol), 4)}
    Call Delta: {round(delta("call", cap, sp, rfir, ty, vol), 3)}
    Put Delta: {round(delta("put", cap, sp, rfir, ty, vol), 3)}
    Call Rho: {round(rho("call", cap, sp, rfir, ty, vol), 3)}
    Put Rho: {round(rho("put", cap, sp, rfir, ty, vol), 3)}
    '''
    st.sidebar.write("--------------------------")
    st.sidebar.download_button("Download information", content, "results.txt")
