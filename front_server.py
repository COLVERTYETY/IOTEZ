import streamlit as st
import pandas as pd
import numpy as np
import time

@st.cache
class myview():
    def __init__(self, title):
        self.title = title
        self.data = pd.DataFrame()
        self.data["x"] = []
        self.data["y"] = []
        #  fill with some data
        for i in range(100):
            self.data = self.data.append({"x":i, "y":np.random.randint(0,100)}, ignore_index=True)

pages = [myview("df1"),myview("df2")]

#  setup navigation
st.sidebar.title("Navigation")
#  subsection for pages
con = st.sidebar.container()
con.subheader("Pages")
# unfolding pages
page = con.selectbox("view:", [p.title for p in pages])

st.sidebar.subheader("configutation")

config = st.sidebar.radio("config:", ["config1","config2"])

#  setup raw data
for p in pages:
    if p.title == page:
        st.subheader("raw data")
        st.dataframe(p.data)
        st.line_chart(p.data)

