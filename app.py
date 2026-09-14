import streamlit as st

st.title("Debug Report")

file = st.file_uploader(
    "Carica file",
    type=["xls"]
)

if file:

    content = file.read()

    text = content.decode(
        "utf-8",
        errors="ignore"
    )

    st.write("Dimensione file:", len(text))

    st.subheader("Prime 5000 lettere")

    st.text(text[:5000])
