import streamlit as st
import pandas as pd
import json

CONFIG_FILE = "omaggi_config.json"


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            config,
            f,
            indent=4,
            ensure_ascii=False
        )


st.set_page_config(
    page_title="Verifica Omaggi",
    layout="wide"
)

st.title("🎟️ Verifica Omaggi")

# -------------------------------------------------
# CONFIGURAZIONE OMAGGI
# -------------------------------------------------

config = load_config()

st.subheader("⚙️ Configurazione Omaggi")

if config:

    new_config = {}

    for gift in sorted(config.keys()):

        new_config[gift] = st.checkbox(
            gift,
            value=bool(config[gift]),
            key=f"cfg_{gift}"
        )

    if st.button("💾 Salva Configurazione"):

        save_config(new_config)

        st.success(
            "Configurazione salvata"
        )

else:

    st.info(
        "Nessun omaggio configurato."
    )

st.divider()

# -------------------------------------------------
# UPLOAD REPORT
# -------------------------------------------------

uploaded_file = st.file_uploader(
    "Carica report Vista (.xls)",
    type=["xls"]
)

if uploaded_file:

    try:

        df = pd.read_excel(
            uploaded_file,
            header=None
        )

        st.success(
            f"Report letto correttamente ({len(df)} righe)"
        )

        omaggi_trovati = set()

        for _, row in df.iterrows():

             for value in row.values:
    
                if pd.isna(value):
                    continue

                text = str(value).strip()

                if "Omaggio" in text:

                    text = " ".join(text.split())

                    omaggi_trovati.add(text)
    
        st.subheader("🎁 Omaggi trovati")

        if not omaggi_trovati:

            st.warning(
                "Nessun omaggio trovato"
            )

        else:

            for gift in sorted(omaggi_trovati):

                st.write("•", gift)

        # -----------------------------------------
        # NUOVE TIPOLOGIE
        # -----------------------------------------

        config_norm = {
            k.strip(): v
            for k, v in config.items()
        }

        nuovi_omaggi = [
            gift
            for gift in omaggi_trovati
            if gift.strip() not in config_norm
        ]

        if nuovi_omaggi:

            st.subheader(
                "🆕 Nuove tipologie omaggio"
            )

            for gift in sorted(nuovi_omaggi):

                scelta = st.radio(
                    gift,
                    [
                        "Richiede commento",
                        "Non richiede commento"
                    ],
                    key=f"new_{gift}"
                )

                config[gift] = (
                    scelta == "Richiede commento"
                )

            if st.button(
                "➕ Salva Nuove Tipologie"
            ):

                save_config(config)

                st.success(
                    "Nuove tipologie salvate"
                )

    except Exception as e:

        st.error(str(e))
