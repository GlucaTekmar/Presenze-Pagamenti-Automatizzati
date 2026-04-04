import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

st.set_page_config(layout="wide")

st.title("Sistema Presenze - STEP 1")

# =========================
# UPLOAD MASTER
# =========================

st.header("Caricamento Master")

master_file = st.file_uploader("Carica Master Edicola", type=["xlsx"])

if master_file:
    master_df = pd.read_excel(master_file)
    st.success("Master caricato")
    st.dataframe(master_df)

# =========================
# SELEZIONE MESE
# =========================

st.header("Selezione mese")

col1, col2 = st.columns(2)

with col1:
    anno = st.selectbox("Anno", [2025, 2026, 2027])

with col2:
    mese = st.selectbox("Mese", list(range(1, 13)))

# =========================
# GENERAZIONE FOGLIO
# =========================

if master_file:
    st.header("Genera foglio presenze")

    dipendente = st.selectbox("Seleziona dipendente", master_df["Nome"].unique())

    if st.button("Genera Foglio Presenze"):

        giorni_mese = calendar.monthrange(anno, mese)[1]

        giorni = list(range(1, giorni_mese + 1))

        df_presenze = pd.DataFrame({
            "Giorno": giorni,
            "Edicola Ore": [0]*giorni_mese,
            "Mondadori Ore": [0]*giorni_mese,
            "Giunti Ore": [0]*giorni_mese
        })

        st.session_state["foglio"] = df_presenze
        st.session_state["dipendente"] = dipendente

# =========================
# VISUALIZZAZIONE
# =========================

if "foglio" in st.session_state:

    st.header(f"Foglio Presenze - {st.session_state['dipendente']}")

    st.dataframe(st.session_state["foglio"], use_container_width=True)

# =========================
# STEP 2 - LETTURA MASTER REALI
# =========================

st.header("STEP 2 - Caricamento Master Completi")

col1, col2, col3 = st.columns(3)

with col1:
    file_edicola = st.file_uploader("Master Edicola", type=["xlsx"], key="edicola")

with col2:
    file_libri = st.file_uploader("Master Libri", type=["xlsx"], key="libri")

with col3:
    file_spot = st.file_uploader("Master Sostituti Spot", type=["xlsx"], key="spot")

# =========================
# FUNZIONE PULIZIA COLONNE
# =========================

def clean_columns(df):
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace("\n", "")
    return df

# =========================
# LETTURA FILE
# =========================

if file_edicola:
    df_edicola = pd.read_excel(file_edicola)
    df_edicola = clean_columns(df_edicola)
    st.subheader("Master Edicola")
    st.write("Colonne:", list(df_edicola.columns))
    st.dataframe(df_edicola, use_container_width=True)

if file_libri:
    df_libri = pd.read_excel(file_libri)
    df_libri = clean_columns(df_libri)
    st.subheader("Master Libri")
    st.write("Colonne:", list(df_libri.columns))
    st.dataframe(df_libri, use_container_width=True)

if file_spot:
    df_spot = pd.read_excel(file_spot)
    df_spot = clean_columns(df_spot)
    st.subheader("Master Sostituti Spot")
    st.write("Colonne:", list(df_spot.columns))
    st.dataframe(df_spot, use_container_width=True)

# =========================
# CONTROLLO BASE
# =========================

if file_edicola and file_libri:
    st.success("Master caricati correttamente")
