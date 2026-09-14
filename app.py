import streamlit as st

st.set_page_config(
    page_title="Verifica Omaggi",
    layout="wide"
)

st.title("🎟️ Verifica Omaggi")

file = st.file_uploader(
    "Carica il report Cashier Session Reconciliation",
    type=["xls"]
)

if file:
    st.success("Report caricato correttamente")
    st.write("Nome file:", file.name)
