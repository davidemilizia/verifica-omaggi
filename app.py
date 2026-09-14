import streamlit as st
import pandas as pd

st.title("Verifica Omaggi - Analisi")

file = st.file_uploader(
    "Carica report",
    type=["xls"]
)

if file:

    df = pd.read_excel(
        file,
        header=None
    )

    utenti = df[
        df.astype(str).apply(
            lambda col: col.str.contains(
                "User:",
                na=False
            )
        ).any(axis=1)
    ]

    st.subheader("Righe User")

    st.dataframe(
        utenti,
        use_container_width=True
    )
