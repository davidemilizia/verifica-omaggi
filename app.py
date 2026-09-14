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
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
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

            value = str(row[col]).strip()

            if value == "User:":

                user = str(row[8]).strip()

                rows.append({
                    "row": idx,
                    "user": user
                })

                break

    return rows


def extract_transaction_comments(block):

    comments = 0

    for _, row in block.iterrows():

        values = [
            str(x)
            for x in row.values
            if pd.notna(x)
        ]

        row_text = " ".join(values)

if "Transaction Comments" in row_text:

