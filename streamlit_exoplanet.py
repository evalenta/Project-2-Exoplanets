import streamlit as st
# streamlit run streamlit_exoplanet.py
st.title("Exoplanet")

option = st.selectbox(
    "Select an exoplanet:",
    ("HD 189733B", "Kepler 17B", "Kepler 20F"),
)

st.write("You selected:", option)

