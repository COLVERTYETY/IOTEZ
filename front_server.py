import streamlit as st
import requests
import pandas as pd
import json
from settings import *

API_BASE_URL = "http://"+SERVER_IP + ":"+str(PORT_HTTP)   # Update this to the correct API endpoint

def fetch_data(endpoint):
    response = requests.get(f"{API_BASE_URL}{endpoint}")
    return json.loads(response.text)

st.title("FastAPI Data Browser")

st.sidebar.title("Menu")
menu_option = st.sidebar.selectbox("Choose an option", ["Browse Data", "Connections", "Requests"])

if menu_option == "Browse Data":
    st.header("Browse Data")
    temp = fetch_data("/groups")
    #  remove { and } from the string
    t = temp[1:-1].split(",")
    group = st.selectbox("Select Group", t)
    if group:
        tk = fetch_data(f"/keys/{group}")
        #  remove { and } from the string
        tkk = tk[1:-1].split(",")
        key = st.selectbox("Select Key", tkk)
        if key:
            n = st.number_input("Number of data points", min_value=1, max_value=100, value=10)
            data = fetch_data(f"/{group}/{key}/{n}")
            # data  = json.loads(data)
            data = pd.read_json(data, orient="records")
            # only keep "ip" "value" and "time" columns
            data = data[["ip", "value", "time"]]
            data["time"] = pd.to_datetime(data["time"], unit="s")
            #  display line chart, grouped by ip
            st.line_chart(data["value"])
elif menu_option == "Connections":
    st.header("Connections")
    connections = fetch_data("/sockets")
    st.write(connections)
elif menu_option == "Requests":
    st.header("Requests")
    ips = fetch_data("/requests")
    st.write(ips)