import streamlit as st
import pandas as pd
import json
import re
from collections import defaultdict

CONFIG_FILE = "omaggi_config.json"

EXCLUDED_USERS = {
    "CELL",
    "WEB",
    "Machine Vending"
}


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def clean_html(text):

    text = re.sub(r"<[^>]+>", "\n", text)

    rows = []

    for row in text.splitlines():

        row = row.strip()

        if row:
            rows.append(row)

    return rows


def split_user_blocks(rows):

    indexes = []

    for i, row in enumerate(rows):

        if row == "User:":
            indexes.append(i)

    blocks = []

    for pos, start in enumerate(indexes):

        end = (
            indexes[pos + 1]
            if pos < len(indexes) - 1
            else len(rows)
        )

        blocks.append(rows[start:end])

    return blocks


def get_user_name(block):

    try:
        idx = block.index("User:")
        return block[idx + 1].strip()
    except:
        return "UNKNOWN"


def get_transaction_comments(block):

    for i, row in enumerate(block):

        if row == "Transaction Comments:":

            if i + 1 < len(block):

                try:
                    return int(block[i + 1])
                except:
                    return 0

    return 0


def get_gifts(block):

    gifts = defaultdict(int)

    for i, row in enumerate(block):

        if not row.startswith("Omaggio"):
            continue

        qty = 1

        for j in range(i + 1, min(i + 10, len(block))):

            if re.fullmatch(r"\d+", block[j]):

                qty = int(block[j])
                break

        gifts[row] += qty

    return gifts


def analyze(rows):

    config = load_config()

    user_blocks = split_user_blocks(rows)

    results = []
    new_gifts = set()

    for block in user_blocks:

        user = get_user_name(block)

        if user in EXCLUDED_USERS:
            continue

        gifts = get_gifts(block)

        comments = get_transaction_comments(block)

        total_gifts = sum(gifts.values())

        gifts_requiring_comment = 0

        for gift, qty in gifts.items():

            if gift not in config:
                new_gifts.add(gift)

            if config.get(gift) is True:
                gifts_requiring_comment += qty

        diff = comments - gifts_requiring_comment

        if diff == 0:
            status = "✅ OK"
        elif diff > 0:
            status = f"⚠️ +{diff} commenti"
        else:
            status = f"❌ Mancano {abs(diff)}"

        results.append({
            "User": user,
            "Omaggi Totali": total_gifts,
            "Omaggi da Commentare": gifts_requiring_comment,
            "Transaction Comments": comments,
            "Esito": status
        })

    return results, sorted(new_gifts)


# -------------------------
# STREAMLIT UI
# -------------------------

st.set_page_config(
    page_title="Verifica Omaggi",
    layout="wide"
)

st.title("🎟️ Verifica Omaggi")

uploaded_file = st.file_uploader(
    "Carica il report Cashier Session Reconciliation",
    type=["xls"]
)

if uploaded_file:

    try:

        content = uploaded_file.read()

        text = content.decode(
            "utf-8",
            errors="ignore"
        )

        rows = clean_html(text)

        results, new_gifts = analyze(rows)

        st.success("Analisi completata")

        df = pd.DataFrame(results)

        st.subheader("Risultati")

        st.dataframe(
            df,
            use_container_width=True
        )

        if new_gifts:

            st.subheader(
                "⚠️ Nuove tipologie omaggio"
            )

            for gift in new_gifts:
                st.write(gift)

        else:
            st.success(
                "Nessuna nuova tipologia trovata"
            )

    except Exception as e:

        st.error(str(e))
