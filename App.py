import streamlit as st

st.set_page_config(
    page_title="Clover Sales App",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("Clover Box-Adjusted Sales Summary")
st.info("Upload a CSV file below. This app is optimized for mobile devices. If you do not see the upload button, please refresh your browser.")

import pandas as pd

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    st.success("File uploaded successfully!")
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
else:
    st.warning("No file uploaded yet.")
