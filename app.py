import streamlit as st
import pandas as pd
import json
EXCLUDED_USERS = {
    "CELL",
    "WEB",
    "Machine Vending"
}


def analyze_users(df, config):

    results = []

    user_rows = []

    for idx, row in df.iterrows():

        row_values = [
            str(x).strip()
            for x in row.values
            if pd.notna(x)
        ]

        if "User:" in row_values:

            try:
                user = str(row[8]).strip()

                user_rows.append(
                    (idx, user)
                )

            except:
                pass

    for pos, (start_row, user) in enumerate(user_rows):

        if user in EXCLUDED_USERS:
            continue

        if pos < len(user_rows) - 1:
            end_row = user_rows[pos + 1][0]
        else:
            end_row = len(df)

        block = df.iloc[start_row:end_row]

        omaggi_da_commentare = 0
        transaction_comments = 0

        for _, row in block.iterrows():

            values = [
                str(x).strip()
                for x in row.values
                if pd.notna(x)
            ]

            row_text = " ".join(values)

            # Transaction Comments
            if "Transaction Comments" in row_text:

                for value in values:

                    if value.isdigit():

                        transaction_comments = int(value)

                        break

            # Omaggi
            for value in values:

                if "Omaggio" not in value:
                    continue

                gift = " ".join(value.split())

                if config.get(gift) is True:

                    omaggi_da_commentare += 1

        diff = (
            transaction_comments
            - omaggi_da_commentare
        )

        if diff == 0:
            esito = "✅ OK"

        elif diff > 0:
            esito = f"⚠️ +{diff} commenti"

        else:
            esito = f"❌ Mancano {abs(diff)}"

        results.append({
            "User": user,
            "Omaggi da commentare":
                omaggi_da_commentare,
            "Transaction Comments":
                transaction_comments,
            "Esito": esito
        })

    return pd.DataFrame(results)
CONFIG_FILE = "omaggi_config.json"


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except Exception as e:
        st.error(f"Errore lettura JSON: {e}")
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
        st.divider()

        st.subheader("📊 Controllo Utenti")

        users_df = analyze_users(
            df,
            config
        )

        st.dataframe(
            users_df,
            use_container_width=True
        )
    except Exception as e:

        st.error(str(e))
