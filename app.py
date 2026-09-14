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
  
