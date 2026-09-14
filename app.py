import streamlit as st
import pandas as pd
import json
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


def save_config(data):

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def find_user_rows(df):

    rows = []

    for idx in df.index:

        row = df.loc[idx]

        for col in df.columns:

            value = str(row[col])

            if value.strip() == "User:":

                user = str(row[8]).strip()

                rows.append(
                    {
                        "row": idx,
                        "user": user
                    }
                )

                break

    return rows


def extract_transaction_comments(block):

    comments = 0

    for _, row in block.iterrows():

        row_text = " ".join(
            [
                str(x)
                for x in row.values
                if pd.notna(x)
            ]
        )

        if "Transaction Comments" in row_text:

            values = [
                x
                for x in row.values
                if pd.notna(x)
            ]

            for value in values:

                value = str(value).strip()

                if value.isdigit():

                    comments = int(value)

                    return comments

    return comments


def extract_gifts(block):

    gifts = defaultdict(int)

    for _, row in block.iterrows():

        value = row[4]

        if pd.isna(value):
            continue

        value = str(value).strip()

        if "Omaggio" not in value:
            continue

        qty = 1

        for cell in row.values:

            if (
                isinstance(cell, (int, float))
                and cell > 0
            ):
                qty = int(cell)

        gifts[value] += qty

    return gifts


def analyze_report(df):

    config = load_config()

    user_rows = find_user_rows(df)

    results = []

    new_gifts = set()

    for i, user_info in enumerate(user_rows):

        user = user_info["user"]

        if user in EXCLUDED_USERS:
            continue

        start = user_info["row"]

        if i < len(user_rows) - 1:
            end = user_rows[i + 1]["row"]
        else:
            end = len(df)

        block = df.iloc[start:end]

        gifts = extract_gifts(block)

        comments = extract_transaction_comments(
            block
        )

        total_gifts = sum(gifts.values())

        gifts_to_comment = 0

        for gift, qty in gifts.items():

            if gift not in config:

                config[gift] = None
                new_gifts.add(gift)

            if config[gift] is True:

                gifts_to_comment += qty

        delta = comments - gifts_to_comment

        if delta == 0:
            status = "✅ OK"

        elif delta > 0:
            status = (
                f"⚠️ {delta} commenti in più"
            )

        else:
            status = (
                f"❌ Mancano {abs(delta)}"
            )

        results.append(
            {
                "User": user,
                "Omaggi Totali": total_gifts,
                "Omaggi da Commentare":
                    gifts_to_comment,
                "Transaction Comments":
                    comments,
                "Esito": status
            }
        )

    save_config(config)

    return results, new_gifts, config


st.set_page_config(
    page_title="Verifica Omaggi",
    layout="wide"
)

st.title("🎟️ Verifica Omaggi")

uploaded_file = st.file_uploader(
    "Carica report Vista",
    type=["xls"]
)

if uploaded_file:

    df = pd.read_excel(
        uploaded_file,
        header=None
    )

    results, new_gifts, config = analyze_report(
        df
    )

    st.subheader("📊 Risultati")

    results_df = pd.DataFrame(results)

    st.dataframe(
        results_df,
        use_container_width=True
    )

    if len(new_gifts) > 0:

        st.subheader(
            "⚠️ Nuove tipologie omaggio"
        )

        for gift in sorted(new_gifts):

            value = st.radio(
                f"{gift}",
                ["SI", "NO"],
                horizontal=True,
                key=gift
            )

            if value == "SI":
                config[gift] = True
            else:
                config[gift] = False

        if st.button(
            "💾 Salva Nuove Regole"
        ):

            save_config(config)

            st.success(
                "Regole salvate"
            )
