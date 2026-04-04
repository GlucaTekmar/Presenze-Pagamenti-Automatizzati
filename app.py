import calendar
from datetime import date
from io import BytesIO

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Presenze e Pagamenti Automatizzati", layout="wide")

LOGO_URL = "https://drive.google.com/uc?export=view&id=1hRhNV-CTjKPh8F-d831lc8vznSi-rKYB"
COLOR_ROSSO = "#C62828"
GIORNI_SETTIMANA = ["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"]
MESI = {
    1: "Gennaio",
    2: "Febbraio",
    3: "Marzo",
    4: "Aprile",
    5: "Maggio",
    6: "Giugno",
    7: "Luglio",
    8: "Agosto",
    9: "Settembre",
    10: "Ottobre",
    11: "Novembre",
    12: "Dicembre",
}

COLONNE_MASTER_EDICOLA = [
    "LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM",
    "COMPENSO_MENSILE", "NETTO_ORA", "ID_GDMS", "AGENZIA", "PDV",
    "MHS_TITOLARE", "TEL_MHS", "MAIL_MHS", "COD_FISCALE",
]

COLONNE_MASTER_LIBRI = [
    "ID_GDMS", "PDV", "MHS_TITOLARE", "TEL_MHS", "MAIL_MHS",
    "COD_FISCALE", "AGENZIA", "TIPO_LIBRI", "ELEMENTI_BANCO",
    "LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM", "NETTO_ORA",
]

COLONNE_MASTER_SPOT = [
    "MHS_SOSTITUTO_SPOT", "CODICE_FISCALE", "TEL", "MAIL", "NETTO_ORA",
]

COLONNE_TABELLA = [
    "GIORNO_NUM",
    "DATA",
    "GIORNO_SETTIMANA",
    "EDICOLA_ORE",
    "EDICOLA_€",
    "EDICOLA_TIPO_ASSENZA",
    "EDICOLA_PDV",
    "MONDADORI_ORE",
    "MONDADORI_€",
    "MONDADORI_TIPO_ASSENZA",
    "MONDADORI_PDV",
    "GIUNTI_ORE",
    "GIUNTI_€",
    "GIUNTI_TIPO_ASSENZA",
    "GIUNTI_PDV",
    "FESTIVO",
]

TIPI_ASSENZA = ["", "Ferie", "Malattia", "Permesso", "Assenza", "Altro"]


# =========================
# STILE
# =========================

def render_header():
    logo_html = ""
    if LOGO_URL.strip():
        logo_html = f'<img src="{LOGO_URL}" style="max-height:70px; margin-bottom:10px;">'

    st.markdown(
        f"""
        <style>
            .block-container {{padding-top: 1.2rem; padding-bottom: 2rem;}}
            .titolo-admin {{font-size: 1.8rem; font-weight: 700; color: {COLOR_ROSSO}; margin: 0;}}
            .sottotitolo-admin {{font-size: 1.1rem; font-weight: 600; color: #111111; margin-top: 0.2rem;}}
            .box-intestazione {{border: 1px solid #D0D0D0; border-radius: 10px; padding: 14px; background: #FFFFFF;}}
            .box-totale {{border: 2px solid #D0D0D0; border-radius: 10px; padding: 10px 14px; background: #FAFAFA;}}
            .sezione-step {{border-top: 2px solid #E6E6E6; padding-top: 0.6rem; margin-top: 0.8rem;}}
        </style>
        <div>
            {logo_html}
            <p class="titolo-admin">DASHBOARD ADMIN</p>
            <p class="sottotitolo-admin">presenze e pagamenti automatizzati</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# UTILITY
# =========================

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().replace("\n", " ") for col in df.columns]
    return df


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_upper(value) -> str:
    return normalize_text(value).upper()


def safe_float(value) -> float:
    if pd.isna(value) or str(value).strip() == "":
        return 0.0
    text = str(value).strip().replace("€", "").replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    missing = [col for col in required_columns if col not in df.columns]
    return missing


def normalize_master_edicola(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)
    df = df.copy()
    for col in ["MHS_TITOLARE", "COD_FISCALE", "AGENZIA", "PDV", "ID_GDMS", "TEL_MHS", "MAIL_MHS"]:
        df[col] = df[col].apply(normalize_text)
    for col in GIORNI_SETTIMANA + ["COMPENSO_MENSILE", "NETTO_ORA"]:
        df[col] = df[col].apply(safe_float)
    return df


def normalize_master_libri(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)
    df = df.copy()
    for col in ["MHS_TITOLARE", "COD_FISCALE", "AGENZIA", "PDV", "ID_GDMS", "TEL_MHS", "MAIL_MHS", "TIPO_LIBRI", "ELEMENTI_BANCO"]:
        df[col] = df[col].apply(normalize_text)
    for col in GIORNI_SETTIMANA + ["NETTO_ORA"]:
        df[col] = df[col].apply(safe_float)
    df["TIPO_LIBRI"] = df["TIPO_LIBRI"].str.upper()
    return df


def normalize_master_spot(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)
    df = df.copy()
    for col in ["MHS_SOSTITUTO_SPOT", "CODICE_FISCALE", "TEL", "MAIL"]:
        df[col] = df[col].apply(normalize_text)
    df["NETTO_ORA"] = df["NETTO_ORA"].apply(safe_float)
    return df


def build_anagrafica_pairs(df_edicola: pd.DataFrame, df_libri: pd.DataFrame) -> pd.DataFrame:
    frames = []

    if not df_edicola.empty:
        ed = df_edicola[["MHS_TITOLARE", "COD_FISCALE", "AGENZIA", "TEL_MHS", "MAIL_MHS", "NETTO_ORA", "COMPENSO_MENSILE"]].copy()
        ed["FONTE"] = "EDICOLA"
        frames.append(ed)

    if not df_libri.empty:
        lb = df_libri[["MHS_TITOLARE", "COD_FISCALE", "AGENZIA", "TEL_MHS", "MAIL_MHS", "NETTO_ORA"]].copy()
        lb["COMPENSO_MENSILE"] = 0.0
        lb["FONTE"] = "LIBRI"
        frames.append(lb)

    if not frames:
        return pd.DataFrame()

    anagrafica = pd.concat(frames, ignore_index=True)
    anagrafica["CHIAVE"] = anagrafica.apply(lambda row: f"{normalize_upper(row['COD_FISCALE'])}__{normalize_upper(row['AGENZIA'])}", axis=1)

    rows = []
    for _, group in anagrafica.groupby("CHIAVE", dropna=False):
        first = group.iloc[0]
        netto_ora_values = [v for v in group["NETTO_ORA"].tolist() if safe_float(v) > 0]
        compenso_values = [v for v in group["COMPENSO_MENSILE"].tolist() if safe_float(v) > 0]
        rows.append(
            {
                "CHIAVE": first["CHIAVE"],
                "MHS_TITOLARE": normalize_text(first["MHS_TITOLARE"]),
                "COD_FISCALE": normalize_text(first["COD_FISCALE"]),
                "AGENZIA": normalize_text(first["AGENZIA"]),
                "TEL_MHS": normalize_text(first["TEL_MHS"]),
                "MAIL_MHS": normalize_text(first["MAIL_MHS"]),
                "NETTO_ORA": netto_ora_values[0] if netto_ora_values else 0.0,
                "COMPENSO_MENSILE": compenso_values[0] if compenso_values else 0.0,
            }
        )

    result = pd.DataFrame(rows)
    result = result.sort_values(["AGENZIA", "MHS_TITOLARE", "COD_FISCALE"]).reset_index(drop=True)
    return result


def get_day_label(day_date: date) -> str:
    return GIORNI_SETTIMANA[day_date.weekday()]


def get_festivo_multiplier(agenzia: str) -> float:
    agenzia_up = normalize_upper(agenzia)
    if agenzia_up == "TEKMAR":
        return 1.30
    if agenzia_up == "UP":
        return 1.20
    return 1.00


def extract_default_pdv_and_hours(sub_df: pd.DataFrame, giorno_label: str) -> tuple[float, str]:
    if sub_df.empty:
        return 0.0, ""
    ore = round(sub_df[giorno_label].apply(safe_float).sum(), 2)
    pdv_list = [normalize_text(v) for v in sub_df["PDV"].tolist() if normalize_text(v)]
    pdv_unique = sorted(set(pdv_list))
    return ore, " | ".join(pdv_unique)


def calculate_row_amount(ore: float, netto_ora: float, festivo: bool, agenzia: str) -> float:
    base = round(safe_float(ore) * safe_float(netto_ora), 2)
    if festivo:
        return round(base * get_festivo_multiplier(agenzia), 2)
    return base


def build_presence_dataframe(
    df_edicola: pd.DataFrame,
    df_libri: pd.DataFrame,
    cod_fiscale: str,
    agenzia: str,
    netto_ora: float,
    anno: int,
    mese: int,
) -> pd.DataFrame:
    giorni_mese = calendar.monthrange(anno, mese)[1]
    cod_fiscale_up = normalize_upper(cod_fiscale)
    agenzia_up = normalize_upper(agenzia)

    sub_edicola = df_edicola[
        (df_edicola["COD_FISCALE"].apply(normalize_upper) == cod_fiscale_up)
        & (df_edicola["AGENZIA"].apply(normalize_upper) == agenzia_up)
    ].copy()

    sub_libri = df_libri[
        (df_libri["COD_FISCALE"].apply(normalize_upper) == cod_fiscale_up)
        & (df_libri["AGENZIA"].apply(normalize_upper) == agenzia_up)
    ].copy()

    sub_mondadori = sub_libri[sub_libri["TIPO_LIBRI"].apply(normalize_upper) == "MONDADORI"].copy()
    sub_giunti = sub_libri[sub_libri["TIPO_LIBRI"].apply(normalize_upper) == "GIUNTI"].copy()

    rows = []
    for giorno_num in range(1, giorni_mese + 1):
        current_date = date(anno, mese, giorno_num)
        giorno_label = get_day_label(current_date)

        edicola_ore, edicola_pdv = extract_default_pdv_and_hours(sub_edicola, giorno_label)
        mondadori_ore, mondadori_pdv = extract_default_pdv_and_hours(sub_mondadori, giorno_label)
        giunti_ore, giunti_pdv = extract_default_pdv_and_hours(sub_giunti, giorno_label)

        festivo_default = current_date.weekday() == 6

        rows.append(
            {
                "GIORNO_NUM": giorno_num,
                "DATA": current_date.strftime("%d/%m/%Y"),
                "GIORNO_SETTIMANA": giorno_label,
                "EDICOLA_ORE": edicola_ore,
                "EDICOLA_€": calculate_row_amount(edicola_ore, netto_ora, festivo_default, agenzia),
                "EDICOLA_TIPO_ASSENZA": "",
                "EDICOLA_PDV": edicola_pdv,
                "MONDADORI_ORE": mondadori_ore,
                "MONDADORI_€": calculate_row_amount(mondadori_ore, netto_ora, festivo_default, agenzia),
                "MONDADORI_TIPO_ASSENZA": "",
                "MONDADORI_PDV": mondadori_pdv,
                "GIUNTI_ORE": giunti_ore,
                "GIUNTI_€": calculate_row_amount(giunti_ore, netto_ora, festivo_default, agenzia),
                "GIUNTI_TIPO_ASSENZA": "",
                "GIUNTI_PDV": giunti_pdv,
                "FESTIVO": festivo_default,
            }
        )

    return pd.DataFrame(rows, columns=COLONNE_TABELLA)


def refresh_amounts(df: pd.DataFrame, netto_ora: float, agenzia: str) -> pd.DataFrame:
    updated = df.copy()
    for idx in updated.index:
        festivo = bool(updated.at[idx, "FESTIVO"])
        updated.at[idx, "EDICOLA_€"] = calculate_row_amount(updated.at[idx, "EDICOLA_ORE"], netto_ora, festivo, agenzia)
        updated.at[idx, "MONDADORI_€"] = calculate_row_amount(updated.at[idx, "MONDADORI_ORE"], netto_ora, festivo, agenzia)
        updated.at[idx, "GIUNTI_€"] = calculate_row_amount(updated.at[idx, "GIUNTI_ORE"], netto_ora, festivo, agenzia)
    return updated


def calculate_sheet_stats(df: pd.DataFrame) -> dict:
    edicola_ore = df["EDICOLA_ORE"].apply(safe_float).sum()
    mondadori_ore = df["MONDADORI_ORE"].apply(safe_float).sum()
    giunti_ore = df["GIUNTI_ORE"].apply(safe_float).sum()
    tot_ore = round(edicola_ore + mondadori_ore + giunti_ore, 2)

    tot_euro = round(
        df["EDICOLA_€"].apply(safe_float).sum()
        + df["MONDADORI_€"].apply(safe_float).sum()
        + df["GIUNTI_€"].apply(safe_float).sum(),
        2,
    )

    giorni_lavorati = int(
        ((df["EDICOLA_ORE"].apply(safe_float) + df["MONDADORI_ORE"].apply(safe_float) + df["GIUNTI_ORE"].apply(safe_float)) > 0).sum()
    )

    giorni_modificati = int(
        (
            df["EDICOLA_TIPO_ASSENZA"].astype(str).str.strip().ne("")
            | df["MONDADORI_TIPO_ASSENZA"].astype(str).str.strip().ne("")
            | df["GIUNTI_TIPO_ASSENZA"].astype(str).str.strip().ne("")
        ).sum()
    )

    return {
        "GIORNI_LAVORATI": giorni_lavorati,
        "GIORNI_MODIFICATI": giorni_modificati,
        "TOT_ORE_LAVORATIVE_MESE": tot_ore,
        "TOT_ORE_AZZERATE": 0.0,
        "TOT_€_DA_SCALARE": 0.0,
        "TOT_ATTIVITA_€": tot_euro,
    }


def init_sheet_record(pair_row: pd.Series, df_edicola: pd.DataFrame, df_libri: pd.DataFrame, anno: int, mese: int) -> dict:
    tabella = build_presence_dataframe(
        df_edicola=df_edicola,
        df_libri=df_libri,
        cod_fiscale=pair_row["COD_FISCALE"],
        agenzia=pair_row["AGENZIA"],
        netto_ora=pair_row["NETTO_ORA"],
        anno=anno,
        mese=mese,
    )
    stats = calculate_sheet_stats(tabella)
    return {
        "societa": pair_row["AGENZIA"],
        "nome": pair_row["MHS_TITOLARE"],
        "cf": pair_row["COD_FISCALE"],
        "telefono": pair_row["TEL_MHS"],
        "email": pair_row["MAIL_MHS"],
        "mese": mese,
        "anno": anno,
        "tipo_contratto": "",
        "netto_mese": round(safe_float(pair_row["COMPENSO_MENSILE"]), 2),
        "netto_ora": round(safe_float(pair_row["NETTO_ORA"]), 2),
        "giorni_lavorati": stats["GIORNI_LAVORATI"],
        "giorni_modificati": stats["GIORNI_MODIFICATI"],
        "tot_ore_lavorative_mese": stats["TOT_ORE_LAVORATIVE_MESE"],
        "tot_ore_azzerate": stats["TOT_ORE_AZZERATE"],
        "tot_euro_da_scalare": stats["TOT_€_DA_SCALARE"],
        "lucchetto_foglio": False,
        "lucchetto_mese": False,
        "arretrati": 0.0,
        "extra": 0.0,
        "domeniche": 0.0,
        "rimborso": 0.0,
        "note_generali": "",
        "rimborso_allegati": [],
        "tabella": tabella,
        "tot_attivita": stats["TOT_ATTIVITA_€"],
        "tot_netto_mese": stats["TOT_ATTIVITA_€"],
    }


def update_sheet_totals(record: dict):
    record["tabella"] = refresh_amounts(record["tabella"], record["netto_ora"], record["societa"])
    stats = calculate_sheet_stats(record["tabella"])
    record["giorni_lavorati"] = stats["GIORNI_LAVORATI"]
    record["giorni_modificati"] = stats["GIORNI_MODIFICATI"]
    record["tot_ore_lavorative_mese"] = stats["TOT_ORE_LAVORATIVE_MESE"]
    record["tot_ore_azzerate"] = stats["TOT_ORE_AZZERATE"]
    record["tot_euro_da_scalare"] = stats["TOT_€_DA_SCALARE"]
    record["tot_attivita"] = stats["TOT_ATTIVITA_€"]
    record["tot_netto_mese"] = round(
        stats["TOT_ATTIVITA_€"]
        + safe_float(record["arretrati"])
        + safe_float(record["extra"])
        + safe_float(record["domeniche"])
        + safe_float(record["rimborso"]),
        2,
    )


def ensure_session_keys():
    if "fogli_generati" not in st.session_state:
        st.session_state["fogli_generati"] = {}
    if "chiave_foglio_attivo" not in st.session_state:
        st.session_state["chiave_foglio_attivo"] = None


def serialize_sheet_for_export(record: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    intestazione = pd.DataFrame(
        [
            ["Società", record["societa"]],
            ["Nome", record["nome"]],
            ["CF", record["cf"]],
            ["Mese", f"{MESI[record['mese']]} {record['anno']}"],
            ["Tipo contratto", record["tipo_contratto"]],
            ["NETTO MESE", record["netto_mese"]],
            ["Netto orario", record["netto_ora"]],
            ["Giorni lavorati", record["giorni_lavorati"]],
            ["Giorni modificati", record["giorni_modificati"]],
            ["Tot ore lavorative mese", record["tot_ore_lavorative_mese"]],
            ["Tot ore azzerate", record["tot_ore_azzerate"]],
            ["Tot € da scalare", record["tot_euro_da_scalare"]],
            ["Lucchetto foglio", "SI" if record["lucchetto_foglio"] else "NO"],
            ["Lucchetto mese", "SI" if record["lucchetto_mese"] else "NO"],
        ],
        columns=["Campo", "Valore"],
    )

    blocco_finale = pd.DataFrame(
        [
            ["Arretrati", record["arretrati"]],
            ["Extra", record["extra"]],
            ["Domeniche", record["domeniche"]],
            ["Rimborso", record["rimborso"]],
            ["Tot attività", record["tot_attivita"]],
            ["TOT NETTO MESE", record["tot_netto_mese"]],
            ["Note generali", record["note_generali"]],
        ],
        columns=["Campo", "Valore"],
    )

    return intestazione, record["tabella"], blocco_finale


def export_single_sheet(record: dict) -> bytes:
    output = BytesIO()
    intestazione, tabella, blocco_finale = serialize_sheet_for_export(record)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        intestazione.to_excel(writer, sheet_name="Foglio Presenze", index=False, startrow=0)
        tabella.to_excel(writer, sheet_name="Foglio Presenze", index=False, startrow=len(intestazione) + 2)
        blocco_finale.to_excel(writer, sheet_name="Foglio Presenze", index=False, startrow=len(intestazione) + len(tabella) + 5)
    output.seek(0)
    return output.getvalue()


# =========================
# APP
# =========================

render_header()
ensure_session_keys()

st.markdown('<div class="sezione-step"></div>', unsafe_allow_html=True)
st.subheader("Caricamento master reali")

col_up_1, col_up_2, col_up_3 = st.columns(3)
with col_up_1:
    file_edicola = st.file_uploader("Master Edicola", type=["xlsx"], key="master_edicola")
with col_up_2:
    file_libri = st.file_uploader("Master Libri", type=["xlsx"], key="master_libri")
with col_up_3:
    file_spot = st.file_uploader("Master Sostituti Spot", type=["xlsx"], key="master_spot")

st.markdown('<div class="sezione-step"></div>', unsafe_allow_html=True)
st.subheader("Selezione mese")
col_mese_1, col_mese_2 = st.columns(2)
with col_mese_1:
    anno = st.selectbox("Anno", [2025, 2026, 2027], index=1)
with col_mese_2:
    mese = st.selectbox("Mese", options=list(MESI.keys()), format_func=lambda x: MESI[x], index=0)

if not file_edicola or not file_libri:
    st.info("Carica almeno Master Edicola e Master Libri per procedere con la generazione dei fogli presenze.")
    st.stop()

try:
    df_edicola_raw = pd.read_excel(file_edicola)
    df_libri_raw = pd.read_excel(file_libri)
    df_spot_raw = pd.read_excel(file_spot) if file_spot else pd.DataFrame(columns=COLONNE_MASTER_SPOT)
except Exception as exc:
    st.error(f"Errore nella lettura dei file Excel: {exc}")
    st.stop()

missing_edicola = validate_columns(clean_columns(df_edicola_raw), COLONNE_MASTER_EDICOLA)
missing_libri = validate_columns(clean_columns(df_libri_raw), COLONNE_MASTER_LIBRI)
missing_spot = validate_columns(clean_columns(df_spot_raw), COLONNE_MASTER_SPOT) if not df_spot_raw.empty else []

if missing_edicola:
    st.error(f"Master Edicola non valido. Colonne mancanti: {', '.join(missing_edicola)}")
    st.stop()
if missing_libri:
    st.error(f"Master Libri non valido. Colonne mancanti: {', '.join(missing_libri)}")
    st.stop()
if file_spot and missing_spot:
    st.error(f"Master Sostituti Spot non valido. Colonne mancanti: {', '.join(missing_spot)}")
    st.stop()

df_edicola = normalize_master_edicola(df_edicola_raw)
df_libri = normalize_master_libri(df_libri_raw)
df_spot = normalize_master_spot(df_spot_raw) if not df_spot_raw.empty else df_spot_raw

st.success("Master caricati correttamente")

with st.expander("Visualizza master caricati"):
    st.markdown("**Master Edicola**")
    st.dataframe(df_edicola, use_container_width=True)
    st.markdown("**Master Libri**")
    st.dataframe(df_libri, use_container_width=True)
    if not df_spot.empty:
        st.markdown("**Master Sostituti Spot**")
        st.dataframe(df_spot, use_container_width=True)

anagrafica_fogli = build_anagrafica_pairs(df_edicola, df_libri)
if anagrafica_fogli.empty:
    st.warning("Nessun dipendente/società disponibile per la generazione dei fogli.")
    st.stop()

st.markdown('<div class="sezione-step"></div>', unsafe_allow_html=True)
st.subheader("STEP 3 - Generazione fogli presenze reali")

anagrafica_display = anagrafica_fogli.copy()
anagrafica_display.insert(0, "SELEZIONA", False)
st.caption("1 foglio = 1 dipendente × 1 società × 1 mese")

edited_selection = st.data_editor(
    anagrafica_display,
    hide_index=True,
    use_container_width=True,
    disabled=["MHS_TITOLARE", "COD_FISCALE", "AGENZIA", "TEL_MHS", "MAIL_MHS", "NETTO_ORA", "COMPENSO_MENSILE", "CHIAVE"],
    column_config={
        "SELEZIONA": st.column_config.CheckboxColumn("Seleziona"),
        "MHS_TITOLARE": st.column_config.TextColumn("Nome"),
        "COD_FISCALE": st.column_config.TextColumn("CF"),
        "AGENZIA": st.column_config.TextColumn("Società"),
        "TEL_MHS": st.column_config.TextColumn("Telefono"),
        "MAIL_MHS": st.column_config.TextColumn("Email"),
        "NETTO_ORA": st.column_config.NumberColumn("Netto orario", format="%.2f €"),
        "COMPENSO_MENSILE": st.column_config.NumberColumn("NETTO MESE", format="%.2f €"),
        "CHIAVE": st.column_config.TextColumn("Chiave"),
    },
)

selected_rows = edited_selection[edited_selection["SELEZIONA"] == True]
selected_keys = selected_rows["CHIAVE"].tolist()

col_btn_1, col_btn_2 = st.columns([1, 2])
with col_btn_1:
    genera_btn = st.button("Genera fogli presenze selezionati", type="primary", use_container_width=True)
with col_btn_2:
    st.write("")

if genera_btn:
    if not selected_keys:
        st.warning("Seleziona almeno un dipendente/società.")
    else:
        for chiave in selected_keys:
            pair_row = anagrafica_fogli[anagrafica_fogli["CHIAVE"] == chiave].iloc[0]
            record_key = f"{chiave}__{anno}__{mese:02d}"
            st.session_state["fogli_generati"][record_key] = init_sheet_record(pair_row, df_edicola, df_libri, anno, mese)
            st.session_state["chiave_foglio_attivo"] = record_key
        st.success("Fogli presenze generati correttamente.")

fogli_generati = st.session_state["fogli_generati"]
if not fogli_generati:
    st.stop()

st.markdown('<div class="sezione-step"></div>', unsafe_allow_html=True)
st.subheader("Fogli presenze generati")

fogli_options = list(fogli_generati.keys())
def format_sheet_option(key: str) -> str:
    record = fogli_generati[key]
    return f"{record['nome']} | {record['societa']} | {MESI[record['mese']]} {record['anno']}"

active_key_default = st.session_state["chiave_foglio_attivo"] if st.session_state["chiave_foglio_attivo"] in fogli_options else fogli_options[0]
selected_sheet_key = st.selectbox(
    "Seleziona foglio attivo",
    options=fogli_options,
    index=fogli_options.index(active_key_default),
    format_func=format_sheet_option,
)
st.session_state["chiave_foglio_attivo"] = selected_sheet_key
record = fogli_generati[selected_sheet_key]

update_sheet_totals(record)
locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

st.markdown('<div class="box-intestazione">', unsafe_allow_html=True)
col_i1, col_i2, col_i3, col_i4 = st.columns(4)
with col_i1:
    st.text_input("Società", value=record["societa"], disabled=True)
    st.text_input("Nome", value=record["nome"], disabled=True)
    st.text_input("CF", value=record["cf"], disabled=True)
with col_i2:
    st.text_input("Mese", value=f"{MESI[record['mese']]} {record['anno']}", disabled=True)
    record["tipo_contratto"] = st.text_input("Tipo contratto", value=record["tipo_contratto"], disabled=locked)
    record["netto_mese"] = st.number_input("NETTO MESE", value=float(record["netto_mese"]), step=0.50, disabled=locked)
with col_i3:
    record["netto_ora"] = st.number_input("Netto orario", value=float(record["netto_ora"]), step=0.10, disabled=locked)
    st.number_input("Giorni lavorati", value=int(record["giorni_lavorati"]), disabled=True)
    st.number_input("Giorni modificati", value=int(record["giorni_modificati"]), disabled=True)
with col_i4:
    st.number_input("Tot ore lavorative mese", value=float(record["tot_ore_lavorative_mese"]), disabled=True)
    st.number_input("Tot ore azzerate", value=float(record["tot_ore_azzerate"]), disabled=True)
    st.number_input("Tot € da scalare", value=float(record["tot_euro_da_scalare"]), disabled=True)

col_lock_1, col_lock_2 = st.columns(2)
with col_lock_1:
    record["lucchetto_foglio"] = st.checkbox("Lucchetto foglio", value=record["lucchetto_foglio"], disabled=record["lucchetto_mese"])
with col_lock_2:
    record["lucchetto_mese"] = st.checkbox("Lucchetto mese", value=record["lucchetto_mese"])
st.markdown('</div>', unsafe_allow_html=True)

locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

st.markdown('<div class="sezione-step"></div>', unsafe_allow_html=True)
st.markdown("**Tabella giornaliera**")

editable_df = record["tabella"].copy()
editable_df = st.data_editor(
    editable_df,
    hide_index=True,
    use_container_width=True,
    disabled=locked,
    num_rows="fixed",
    column_config={
        "GIORNO_NUM": st.column_config.NumberColumn("Giorno", disabled=True),
        "DATA": st.column_config.TextColumn("Data", disabled=True),
        "GIORNO_SETTIMANA": st.column_config.TextColumn("Giorno settimana", disabled=True),
        "EDICOLA_ORE": st.column_config.NumberColumn("Edicola Ore", min_value=0.0, step=0.5, format="%.2f"),
        "EDICOLA_€": st.column_config.NumberColumn("Edicola €", format="%.2f €", disabled=True),
        "EDICOLA_TIPO_ASSENZA": st.column_config.SelectboxColumn("Edicola Tipo assenza", options=TIPI_ASSENZA),
        "EDICOLA_PDV": st.column_config.TextColumn("Edicola PDV"),
        "MONDADORI_ORE": st.column_config.NumberColumn("Mondadori Ore", min_value=0.0, step=0.5, format="%.2f"),
        "MONDADORI_€": st.column_config.NumberColumn("Mondadori €", format="%.2f €", disabled=True),
        "MONDADORI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Mondadori Tipo assenza", options=TIPI_ASSENZA),
        "MONDADORI_PDV": st.column_config.TextColumn("Mondadori PDV"),
        "GIUNTI_ORE": st.column_config.NumberColumn("Giunti Ore", min_value=0.0, step=0.5, format="%.2f"),
        "GIUNTI_€": st.column_config.NumberColumn("Giunti €", format="%.2f €", disabled=True),
        "GIUNTI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Giunti Tipo assenza", options=TIPI_ASSENZA),
        "GIUNTI_PDV": st.column_config.TextColumn("Giunti PDV"),
        "FESTIVO": st.column_config.CheckboxColumn("Festivo"),
    },
)
record["tabella"] = editable_df
update_sheet_totals(record)

st.markdown('<div class="sezione-step"></div>', unsafe_allow_html=True)
st.markdown("**Blocco inferiore**")
col_b1, col_b2, col_b3, col_b4 = st.columns(4)
with col_b1:
    record["arretrati"] = st.number_input("€ arretrato", value=float(record["arretrati"]), step=0.50, disabled=locked)
with col_b2:
    record["extra"] = st.number_input("€ extra", value=float(record["extra"]), step=0.50, disabled=locked)
with col_b3:
    record["domeniche"] = st.number_input("€ domeniche", value=float(record["domeniche"]), step=0.50, disabled=locked)
with col_b4:
    record["rimborso"] = st.number_input("€ rimborso", value=float(record["rimborso"]), step=0.50, disabled=locked)

uploaded_docs = st.file_uploader(
    "Allegati rimborso",
    accept_multiple_files=True,
    disabled=locked,
    key=f"upload_allegati_{selected_sheet_key}",
)
if uploaded_docs is not None:
    record["rimborso_allegati"] = [file.name for file in uploaded_docs]
if record["rimborso_allegati"]:
    st.caption("Allegati caricati: " + ", ".join(record["rimborso_allegati"]))

record["note_generali"] = st.text_area(
    "NOTE GENERALI DEL MESE",
    value=record["note_generali"],
    height=140,
    disabled=locked,
)

update_sheet_totals(record)

st.markdown('<div class="box-totale">', unsafe_allow_html=True)
st.metric("TOT NETTO MESE", f"€ {record['tot_netto_mese']:.2f}")
st.caption("Formula: Tot attività + Arretrati + Extra + Domeniche + Rimborsi")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="sezione-step"></div>', unsafe_allow_html=True)
col_a1, col_a2 = st.columns(2)
with col_a1:
    if st.button("Azzera foglio corrente", disabled=locked, use_container_width=True):
        empty_table = record["tabella"].copy()
        for col in ["EDICOLA_ORE", "MONDADORI_ORE", "GIUNTI_ORE", "EDICOLA_€", "MONDADORI_€", "GIUNTI_€"]:
            empty_table[col] = 0.0
        for col in ["EDICOLA_TIPO_ASSENZA", "MONDADORI_TIPO_ASSENZA", "GIUNTI_TIPO_ASSENZA", "EDICOLA_PDV", "MONDADORI_PDV", "GIUNTI_PDV"]:
            empty_table[col] = ""
        empty_table["FESTIVO"] = False
        record["tabella"] = empty_table
        record["arretrati"] = 0.0
        record["extra"] = 0.0
        record["domeniche"] = 0.0
        record["rimborso"] = 0.0
        record["note_generali"] = ""
        record["rimborso_allegati"] = []
        update_sheet_totals(record)
        st.rerun()
with col_a2:
    export_bytes = export_single_sheet(record)
    filename = f"foglio_presenze_{record['societa'].lower()}_{record['cf']}_{record['anno']}_{record['mese']:02d}.xlsx"
    st.download_button(
        "Export foglio corrente Excel",
        data=export_bytes,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
