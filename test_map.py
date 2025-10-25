import streamlit as st
import pandas as pd

st.set_page_config(page_title="Map Test", layout="wide")

# ✅ Sample coordinates (Mumbai)
df = pd.DataFrame({
    "lat": [19.0760],
    "lon": [72.8777]
})

st.title("🗺️ Simple Map Test")
st.write("DEBUG DATAFRAME:", df)

st.map(df)
