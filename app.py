import streamlit as st
import pandas as pd

st.title("Analisi struttura report")

file = st.file_uploader(
    "Carica report",
    type=["xls"]
)

if file:

    df = pd.read_excel(
        file,
        header=None
    )

    st.success("File letto correttamente")

    ricerca = st.text_input(
        "Cerca testo",
        value="Omaggio"
    )

    if ricerca:

        mask = df.astype(str).apply(
            lambda col: col.str.contains(
                ricerca,
                case=False,
                na=False
            )
        )

        risultati = df[mask.any(axis=1)]

        st.write(
            f"Righe trovate: {len(risultati)}"
        )

        st.dataframe(
            risultati,
            use_container_width=True
        )
