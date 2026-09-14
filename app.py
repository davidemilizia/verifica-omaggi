import streamlit as st
import pandas as pd

st.title("Debug XLS")

file = st.file_uploader(
    "Carica report",
    type=["xls"]
)

if file:

    try:

df = pd.read_excel(
    file,
    header=None
)
        st.success("File letto correttamente")

        st.write("Righe:", len(df))
        st.write("Colonne:", len(df.columns))

        st.dataframe(df.head(50))

    except Exception as e:

        st.error(str(e))
