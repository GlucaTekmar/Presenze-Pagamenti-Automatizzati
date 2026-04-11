import calendar
from copy import deepcopy
from datetime import date, datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Presenze e Pagamenti Automatizzati", layout="wide")

LOGO_URL = "https://raw.githubusercontent.com/GlucaTekmar/operativita-pdv/refs/heads/main/logo.png"

COLOR_ROSSO = "#C62828"
BG_APP = "#EEF1F4"
BG_BOX = "#F7F8FA"
BG_FIELD = "#FFFFFF"
BORDER_COLOR = "#97A3AF"
BORDER_COLOR_STRONG = "#7F8C99"
TEXT_COLOR = "#1E2A36"
TEXT_MUTED = "#425466"

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
TIPI_ASSENZA = ["", "Ferie", "Malattia", "Permesso", "Assenza", "Altro"]

COLONNE_MASTER_EDICOLA = [
    "LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM",
    "COMPENSO_MENSILE", "NETTO_ORA", "ID_GDMS", "AGENZIA", "PDV",
    "MHS_TITOLARE", "TEL_MHS", "MAIL_MHS", "COD_FISCALE",
    "TIPO_CONTRATTO", "SCADENZA_CONTRATTO",
]

COLONNE_MASTER_LIBRI = [
    "ID_GDMS", "PDV", "MHS_TITOLARE", "TEL_MHS", "MAIL_MHS",
    "COD_FISCALE", "AGENZIA", "TIPO_LIBRI", "ELEMENTI_BANCO",
    "LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM", "NETTO_ORA",
    "TIPO_CONTRATTO", "SCADENZA_CONTRATTO",
]

COLONNE_MASTER_SPOT = [
    "MHS_SOSTITUTO_SPOT", "COD_FISCALE", "TEL", "MAIL", "NETTO_ORA",
    "TIPO_CONTRATTO", "SCADENZA_CONTRATTO",
]

HEADER_ALIASES = {
    "CODICE_FISCALE": "COD_FISCALE",
    "CF": "COD_FISCALE",
    "MHS TITOLARE": "MHS_TITOLARE",
    "TEL MHS": "TEL_MHS",
    "MAIL MHS": "MAIL_MHS",
    "TIPO CONTRATTO": "TIPO_CONTRATTO",
    "SCADENZA CONTRATTO": "SCADENZA_CONTRATTO",
    "NETTO ORA": "NETTO_ORA",
    "COMPENSO MENSILE": "COMPENSO_MENSILE",
    "TIPO LIBRI": "TIPO_LIBRI",
    "ELEMENTI BANCO": "ELEMENTI_BANCO",
}

ORIGINE_EDICOLA = "EDICOLA"
ORIGINE_LIBRI = "LIBRI"

COLONNE_BASE_ALL = [
    "BASE_EDICOLA_ORE",
    "BASE_MONDADORI_ORE",
    "BASE_GIUNTI_ORE",
]

COLONNE_TABELLA_TECNICHE = [
    "GIORNO_NUM",
    "DATA",
    "GIORNO_SETTIMANA",
    "DATA_VIEW",
    "EDICOLA_ORE",
    "EDICOLA_€",
    "EDICOLA_TIPO_ASSENZA",
    "MONDADORI_ORE",
    "MONDADORI_€",
    "MONDADORI_TIPO_ASSENZA",
    "GIUNTI_ORE",
    "GIUNTI_€",
    "GIUNTI_TIPO_ASSENZA",
    "FESTIVO",
    "ROW_STATUS",
    "BASE_EDICOLA_ORE",
    "BASE_MONDADORI_ORE",
    "BASE_GIUNTI_ORE",
]


# =========================
# STILE
# =========================

def inject_global_css():
    st.markdown(
        f"""
        <style>
            :root {{
                --app-bg: {BG_APP};
                --box-bg: {BG_BOX};
                --field-bg: {BG_FIELD};
                --border: {BORDER_COLOR};
                --border-strong: {BORDER_COLOR_STRONG};
                --text: {TEXT_COLOR};
                --muted: {TEXT_MUTED};
                --red: {COLOR_ROSSO};
            }}

            html, body, [class*="css"], .stApp {{
                color: var(--text);
                font-size: 16px !important;
            }}

            .stApp {{
                background: var(--app-bg);
            }}

            .block-container {{
                padding-top: 0.8rem;
                padding-bottom: 2rem;
                max-width: 96%;
            }}

            section[data-testid="stSidebar"] {{
                background: #E3E8EE !important;
                border-right: 2px solid var(--border-strong);
            }}

            section[data-testid="stSidebar"] * {{
                font-size: 18px !important;
                color: var(--text) !important;
            }}

            .sidebar-logo-wrap {{
                padding-top: 6px;
                padding-bottom: 12px;
                border-bottom: 2px solid var(--border-strong);
                margin-bottom: 14px;
            }}

            .main-header-box {{
                background: var(--box-bg);
                border: 2px solid var(--border-strong);
                border-radius: 16px;
                padding: 16px 18px;
                margin-bottom: 18px;
            }}

            .page-title-box {{
                background: var(--box-bg);
                border: 2px solid var(--border-strong);
                border-radius: 16px;
                padding: 14px 16px;
                margin-bottom: 16px;
            }}

            .main-header-title {{
                font-size: 2rem;
                font-weight: 800;
                color: var(--red);
                margin: 0;
                line-height: 1.1;
            }}

            .main-header-subtitle {{
                font-size: 1.25rem;
                font-weight: 700;
                color: var(--text);
                margin: 0.35rem 0 0 0;
            }}

            .section-title {{
                font-size: 1.65rem;
                font-weight: 800;
                color: var(--red);
                margin: 0;
                line-height: 1.15;
            }}

            .section-box {{
                background: var(--box-bg);
                border: 2px solid var(--border-strong);
                border-radius: 16px;
                padding: 16px;
                margin-bottom: 16px;
            }}

            .inner-box {{
                background: #F4F6F8;
                border: 2px solid var(--border-strong);
                border-radius: 14px;
                padding: 14px;
                margin-bottom: 14px;
            }}

            .soft-note {{
                border-left: 4px solid var(--red);
                background: #FFF5F5;
                border-radius: 10px;
                padding: 12px 14px;
                font-size: 1rem;
                margin-bottom: 12px;
            }}

            .activity-note {{
                border: 2px dashed var(--border-strong);
                background: #FAFBFC;
                border-radius: 12px;
                padding: 10px 12px;
                font-size: 0.98rem;
                color: var(--muted);
                margin-bottom: 12px;
            }}

            .activity-legend {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 8px;
            }}

            .activity-pill {{
                border-radius: 999px;
                padding: 6px 12px;
                font-size: 0.97rem;
                font-weight: 800;
                border: 2px solid var(--border-strong);
                background: white;
                color: var(--text);
            }}

            .pill-edicola {{
                background: #FFF1F1;
            }}

            .pill-mondadori {{
                background: #EEF4FF;
            }}

            .pill-giunti {{
                background: #F1FAF1;
            }}

            .stMarkdown p, .stCaption, label, .stSelectbox label, .stTextInput label,
            .stNumberInput label, .stTextArea label, .stFileUploader label {{
                font-size: 1rem !important;
            }}

            .stSelectbox label p,
            .stTextInput label p,
            .stNumberInput label p,
            .stTextArea label p,
            .stFileUploader label p,
            .stCheckbox label p {{
                font-size: 1.06rem !important;
                font-weight: 800 !important;
                color: var(--text) !important;
            }}

            [data-testid="stMetricLabel"] {{
                font-size: 1rem !important;
                font-weight: 800 !important;
            }}

            [data-testid="stMetricValue"] {{
                font-size: 2rem !important;
                font-weight: 800 !important;
                color: var(--text) !important;
            }}

            div[data-baseweb="select"] > div,
            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea,
            [data-testid="stFileUploaderDropzone"],
            [data-testid="stDataFrame"],
            [data-testid="stTable"] {{
                background: var(--field-bg) !important;
                border: 2px solid var(--border-strong) !important;
                border-radius: 12px !important;
            }}

            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea {{
                color: var(--text) !important;
                font-size: 1.04rem !important;
            }}

            .stButton > button {{
                background: white !important;
                color: var(--text) !important;
                border: 2px solid var(--border-strong) !important;
                border-radius: 12px !important;
                font-size: 1.04rem !important;
                font-weight: 800 !important;
                min-height: 46px;
            }}

            .stButton > button[kind="primary"] {{
                background: #FFF4F4 !important;
                border: 2px solid #C07F7F !important;
            }}

            .stCheckbox label {{
                font-size: 1.04rem !important;
                font-weight: 800 !important;
            }}

            details {{
                background: white;
                border: 2px solid var(--border-strong);
                border-radius: 12px;
                padding: 6px 10px;
            }}

            .table-title {{
                font-size: 1.32rem;
                font-weight: 800;
                color: var(--text);
                margin-bottom: 0.6rem;
            }}

            .warning-box {{
                background: #FDECEC;
                border: 2px solid #D9534F;
                color: #8B0000;
                border-radius: 12px;
                padding: 12px 14px;
                font-size: 1rem;
                font-weight: 800;
                margin-bottom: 10px;
            }}

            .separator-help {{
                font-size: 0.96rem;
                color: var(--muted);
                margin-bottom: 10px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown('<div class="main-header-box">', unsafe_allow_html=True)
    col_logo, col_text = st.columns([1, 5])
    with col_logo:
        st.image(LOGO_URL, width=150)
    with col_text:
        st.markdown(
            """
            <p class="main-header-title">DASHBOARD ADMIN</p>
            <p class="main-header-subtitle">presenze e pagamenti automatizzati</p>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_page_title(title: str):
    st.markdown(
        f"""
        <div class="page-title-box">
            <p class="section-title">{title}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_warning_box(message: str):
    st.markdown(
        f'<div class="warning-box">ATTENZIONE — {message}</div>',
        unsafe_allow_html=True,
    )


# =========================
# UTILITY
# =========================

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


def normalize_date_text(value) -> str:
    if pd.isna(value) or str(value).strip() == "":
        return ""
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.strftime("%d/%m/%Y")
    return str(value).strip()


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cleaned = []
    for col in df.columns:
        new_col = str(col).strip().replace("\n", " ")
        new_col = " ".join(new_col.split())
        new_col = HEADER_ALIASES.get(new_col.upper(), new_col)
        cleaned.append(new_col)
    df.columns = cleaned
    return df


def validate_columns(df: pd.DataFrame, required_columns: list[str]) -> list[str]:
    return [col for col in required_columns if col not in df.columns]


def get_day_label(day_date: date) -> str:
    return GIORNI_SETTIMANA[day_date.weekday()]


def get_festivo_multiplier(agenzia: str) -> float:
    agenzia_up = normalize_upper(agenzia)
    if agenzia_up == "TEKMAR":
        return 1.30
    if agenzia_up == "UP":
        return 1.20
    return 1.00


def calculate_row_amount(ore: float, netto_ora: float, festivo: bool, agenzia: str) -> float:
    base = round(safe_float(ore) * safe_float(netto_ora), 2)
    if festivo:
        return round(base * get_festivo_multiplier(agenzia), 2)
    return base


def format_sheet_key(row_id: str, anno: int, mese: int) -> str:
    return f"{row_id}__{anno}__{mese:02d}"


def format_scadenza(value: str) -> str:
    return normalize_text(value)


# =========================
# NORMALIZZAZIONE MASTER
# =========================

def normalize_master_edicola(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df).copy()
    for col in ["ID_GDMS", "AGENZIA", "PDV", "MHS_TITOLARE", "TEL_MHS", "MAIL_MHS", "COD_FISCALE", "TIPO_CONTRATTO"]:
        df[col] = df[col].apply(normalize_text)
    df["SCADENZA_CONTRATTO"] = df["SCADENZA_CONTRATTO"].apply(normalize_date_text)
    for col in GIORNI_SETTIMANA + ["COMPENSO_MENSILE", "NETTO_ORA"]:
        df[col] = df[col].apply(safe_float)
    return df


def normalize_master_libri(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df).copy()
    for col in ["ID_GDMS", "PDV", "MHS_TITOLARE", "TEL_MHS", "MAIL_MHS", "COD_FISCALE", "AGENZIA", "TIPO_LIBRI", "TIPO_CONTRATTO"]:
        df[col] = df[col].apply(normalize_text)
    df["ELEMENTI_BANCO"] = df["ELEMENTI_BANCO"].apply(normalize_text)
    df["SCADENZA_CONTRATTO"] = df["SCADENZA_CONTRATTO"].apply(normalize_date_text)
    for col in GIORNI_SETTIMANA + ["NETTO_ORA"]:
        df[col] = df[col].apply(safe_float)
    df["TIPO_LIBRI"] = df["TIPO_LIBRI"].str.upper().str.strip()
    return df


def normalize_master_spot(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df).copy()
    for col in ["MHS_SOSTITUTO_SPOT", "COD_FISCALE", "TEL", "MAIL", "TIPO_CONTRATTO"]:
        df[col] = df[col].apply(normalize_text)
    df["SCADENZA_CONTRATTO"] = df["SCADENZA_CONTRATTO"].apply(normalize_date_text)
    df["NETTO_ORA"] = df["NETTO_ORA"].apply(safe_float)
    return df


# =========================
# RIGHE SELEZIONE SENZA RAGGRUPPAMENTO
# =========================

def build_generation_table(df_edicola: pd.DataFrame, df_libri: pd.DataFrame) -> pd.DataFrame:
    righe = []

    for idx, row in df_edicola.reset_index(drop=True).iterrows():
        row_id = f"EDICOLA_{idx}"
        righe.append(
            {
                "SELEZIONA": False,
                "ROW_ID": row_id,
                "ORIGINE_MASTER": ORIGINE_EDICOLA,
                "TIPO_LIBRI": "",
                "NOME": normalize_text(row["MHS_TITOLARE"]),
                "COD_FISCALE": normalize_text(row["COD_FISCALE"]),
                "SOCIETA": normalize_text(row["AGENZIA"]),
                "PDV": normalize_text(row["PDV"]),
                "TELEFONO": normalize_text(row["TEL_MHS"]),
                "EMAIL": normalize_text(row["MAIL_MHS"]),
                "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                "NETTO_MESE": safe_float(row["COMPENSO_MENSILE"]),
                "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                "SCADENZA_CONTRATTO": format_scadenza(row["SCADENZA_CONTRATTO"]),
                "ATTIVITA_RIGA": "EDICOLA",
                "MASTER_INDEX": idx,
            }
        )

    for idx, row in df_libri.reset_index(drop=True).iterrows():
        tipo_libri = normalize_upper(row["TIPO_LIBRI"])
        attivita_riga = "LIBRI"
        if tipo_libri in {"MONDADORI", "GIUNTI"}:
            attivita_riga = f"LIBRI - {tipo_libri}"

        row_id = f"LIBRI_{idx}"
        righe.append(
            {
                "SELEZIONA": False,
                "ROW_ID": row_id,
                "ORIGINE_MASTER": ORIGINE_LIBRI,
                "TIPO_LIBRI": normalize_text(row["TIPO_LIBRI"]),
                "NOME": normalize_text(row["MHS_TITOLARE"]),
                "COD_FISCALE": normalize_text(row["COD_FISCALE"]),
                "SOCIETA": normalize_text(row["AGENZIA"]),
                "PDV": normalize_text(row["PDV"]),
                "TELEFONO": normalize_text(row["TEL_MHS"]),
                "EMAIL": normalize_text(row["MAIL_MHS"]),
                "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                "NETTO_MESE": 0.0,
                "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                "SCADENZA_CONTRATTO": format_scadenza(row["SCADENZA_CONTRATTO"]),
                "ATTIVITA_RIGA": attivita_riga,
                "MASTER_INDEX": idx,
            }
        )

    result = pd.DataFrame(righe)
    if result.empty:
        return result

    result = result.sort_values(["ORIGINE_MASTER", "NOME", "SOCIETA", "PDV", "TIPO_LIBRI"]).reset_index(drop=True)
    return result


# =========================
# COSTRUZIONE FOGLIO
# =========================

def build_presence_dataframe_from_selection(
    row: pd.Series,
    df_edicola: pd.DataFrame,
    df_libri: pd.DataFrame,
    anno: int,
    mese: int,
) -> pd.DataFrame:
    giorni_mese = calendar.monthrange(anno, mese)[1]
    righe = []

    origine = normalize_upper(row["ORIGINE_MASTER"])
    tipo_libri = normalize_upper(row.get("TIPO_LIBRI", ""))
    societa = normalize_text(row["SOCIETA"])
    netto_ora = safe_float(row["NETTO_ORA"])
    master_index = int(row["MASTER_INDEX"])

    if origine == ORIGINE_EDICOLA:
        source_row = df_edicola.iloc[master_index]
    else:
        source_row = df_libri.iloc[master_index]

    def get_master_hours_for_day(giorno_label: str) -> tuple[float, float, float]:
        if origine == ORIGINE_EDICOLA:
            return safe_float(source_row[giorno_label]), 0.0, 0.0
        if origine == ORIGINE_LIBRI:
            if tipo_libri == "MONDADORI":
                return 0.0, safe_float(source_row[giorno_label]), 0.0
            if tipo_libri == "GIUNTI":
                return 0.0, 0.0, safe_float(source_row[giorno_label])
            return 0.0, 0.0, 0.0
        return 0.0, 0.0, 0.0

    for giorno_num in range(1, giorni_mese + 1):
        current_date = date(anno, mese, giorno_num)
        giorno_label = get_day_label(current_date)
        festivo_default = current_date.weekday() == 6

        edicola_ore, mondadori_ore, giunti_ore = get_master_hours_for_day(giorno_label)

        righe.append(
            {
                "GIORNO_NUM": giorno_num,
                "DATA": current_date.strftime("%d/%m/%Y"),
                "GIORNO_SETTIMANA": giorno_label,
                "DATA_VIEW": current_date.strftime("%d/%m/%Y"),
                "EDICOLA_ORE": edicola_ore,
                "EDICOLA_€": calculate_row_amount(edicola_ore, netto_ora, festivo_default, societa),
                "EDICOLA_TIPO_ASSENZA": "",
                "MONDADORI_ORE": mondadori_ore,
                "MONDADORI_€": calculate_row_amount(mondadori_ore, netto_ora, festivo_default, societa),
                "MONDADORI_TIPO_ASSENZA": "",
                "GIUNTI_ORE": giunti_ore,
                "GIUNTI_€": calculate_row_amount(giunti_ore, netto_ora, festivo_default, societa),
                "GIUNTI_TIPO_ASSENZA": "",
                "FESTIVO": festivo_default,
                "ROW_STATUS": "",
                "BASE_EDICOLA_ORE": edicola_ore,
                "BASE_MONDADORI_ORE": mondadori_ore,
                "BASE_GIUNTI_ORE": giunti_ore,
            }
        )

    return pd.DataFrame(righe, columns=COLONNE_TABELLA_TECNICHE)


def get_row_status(df: pd.DataFrame, idx: int) -> str:
    base_tot = round(
        safe_float(df.at[idx, "BASE_EDICOLA_ORE"])
        + safe_float(df.at[idx, "BASE_MONDADORI_ORE"])
        + safe_float(df.at[idx, "BASE_GIUNTI_ORE"]),
        2,
    )
    current_tot = round(
        safe_float(df.at[idx, "EDICOLA_ORE"])
        + safe_float(df.at[idx, "MONDADORI_ORE"])
        + safe_float(df.at[idx, "GIUNTI_ORE"]),
        2,
    )
    has_assenza = (
        normalize_text(df.at[idx, "EDICOLA_TIPO_ASSENZA"]) != ""
        or normalize_text(df.at[idx, "MONDADORI_TIPO_ASSENZA"]) != ""
        or normalize_text(df.at[idx, "GIUNTI_TIPO_ASSENZA"]) != ""
    )
    if has_assenza or current_tot < base_tot:
        return "MODIFICATA"
    return ""


def update_data_view(df: pd.DataFrame) -> pd.DataFrame:
    updated = df.copy()
    for idx in updated.index:
        base_data = normalize_text(updated.at[idx, "DATA"])
        status = normalize_upper(updated.at[idx, "ROW_STATUS"])
        if status == "MODIFICATA":
            updated.at[idx, "DATA_VIEW"] = f"🔴 {base_data}"
        else:
            updated.at[idx, "DATA_VIEW"] = base_data
    return updated


def apply_step3_rules(tabella: pd.DataFrame, netto_ora: float, societa: str, origine_master: str) -> tuple[pd.DataFrame, list[str]]:
    df = tabella.copy()
    warnings = []

    for col in ["EDICOLA_ORE", "MONDADORI_ORE", "GIUNTI_ORE"]:
        df[col] = df[col].apply(safe_float)

    for idx in df.index:
        if origine_master == ORIGINE_EDICOLA:
            allowed = [("EDICOLA", "BASE_EDICOLA_ORE")]
            blocked = [("MONDADORI", "BASE_MONDADORI_ORE"), ("GIUNTI", "BASE_GIUNTI_ORE")]
        else:
            allowed = [("MONDADORI", "BASE_MONDADORI_ORE"), ("GIUNTI", "BASE_GIUNTI_ORE")]
            blocked = [("EDICOLA", "BASE_EDICOLA_ORE")]

        for attivita, _ in blocked:
            ore_col = f"{attivita}_ORE"
            euro_col = f"{attivita}_€"
            assenza_col = f"{attivita}_TIPO_ASSENZA"
            df.at[idx, ore_col] = 0.0
            df.at[idx, euro_col] = 0.0
            df.at[idx, assenza_col] = ""

        for attivita, base_col in allowed:
            ore_col = f"{attivita}_ORE"
            euro_col = f"{attivita}_€"
            assenza_col = f"{attivita}_TIPO_ASSENZA"

            base_value = safe_float(df.at[idx, base_col])
            new_value = safe_float(df.at[idx, ore_col])

            if new_value > base_value:
                df.at[idx, ore_col] = base_value
                warnings.append(
                    f"Giorno {int(df.at[idx, 'GIORNO_NUM'])}: non è consentito aumentare le ore oltre il valore generato."
                )

            if safe_float(df.at[idx, ore_col]) > 0 and normalize_text(df.at[idx, assenza_col]) != "":
                df.at[idx, assenza_col] = ""

            df.at[idx, euro_col] = calculate_row_amount(
                df.at[idx, ore_col],
                netto_ora,
                bool(df.at[idx, "FESTIVO"]),
                societa,
            )

        df.at[idx, "ROW_STATUS"] = get_row_status(df, idx)

    df = update_data_view(df)

    if warnings:
        warnings = list(dict.fromkeys(warnings))

    return df, warnings


def calculate_sheet_stats(df: pd.DataFrame, origine_master: str) -> dict:
    if origine_master == ORIGINE_EDICOLA:
        current_hours = df["EDICOLA_ORE"].apply(safe_float)
        base_hours = df["BASE_EDICOLA_ORE"].apply(safe_float)
        euro_sum = df["EDICOLA_€"].apply(safe_float).sum()
    else:
        current_hours = df["MONDADORI_ORE"].apply(safe_float) + df["GIUNTI_ORE"].apply(safe_float)
        base_hours = df["BASE_MONDADORI_ORE"].apply(safe_float) + df["BASE_GIUNTI_ORE"].apply(safe_float)
        euro_sum = df["MONDADORI_€"].apply(safe_float).sum() + df["GIUNTI_€"].apply(safe_float).sum()

    giorni_lavorati = int((current_hours > 0).sum())
    giorni_modificati = int((df["ROW_STATUS"].astype(str).str.strip() != "").sum())
    tot_ore = round(current_hours.sum(), 2)
    tot_ore_azzerate = round((base_hours - current_hours).sum(), 2)
    tot_euro = round(euro_sum, 2)

    return {
        "GIORNI_LAVORATI": giorni_lavorati,
        "GIORNI_MODIFICATI": giorni_modificati,
        "TOT_ORE_LAVORATIVE_MESE": tot_ore,
        "TOT_ORE_AZZERATE": tot_ore_azzerate,
        "TOT_€_DA_SCALARE": 0.0,
        "TOT_ATTIVITA_€": tot_euro,
    }


def init_sheet_record(
    row: pd.Series,
    df_edicola: pd.DataFrame,
    df_libri: pd.DataFrame,
    anno: int,
    mese: int,
) -> dict:
    tabella = build_presence_dataframe_from_selection(
        row=row,
        df_edicola=df_edicola,
        df_libri=df_libri,
        anno=anno,
        mese=mese,
    )
    tabella, _ = apply_step3_rules(
        tabella=tabella,
        netto_ora=safe_float(row["NETTO_ORA"]),
        societa=normalize_text(row["SOCIETA"]),
        origine_master=normalize_upper(row["ORIGINE_MASTER"]),
    )
    stats = calculate_sheet_stats(tabella, normalize_upper(row["ORIGINE_MASTER"]))

    record = {
        "row_id": normalize_text(row["ROW_ID"]),
        "origine_master": normalize_text(row["ORIGINE_MASTER"]),
        "tipo_libri": normalize_text(row["TIPO_LIBRI"]),
        "attivita_riga": normalize_text(row["ATTIVITA_RIGA"]),
        "societa": normalize_text(row["SOCIETA"]),
        "mese": mese,
        "anno": anno,
        "nome": normalize_text(row["NOME"]),
        "cf": normalize_text(row["COD_FISCALE"]),
        "pdv": normalize_text(row["PDV"]),
        "telefono": normalize_text(row["TELEFONO"]),
        "email": normalize_text(row["EMAIL"]),
        "netto_mese": round(safe_float(row["NETTO_MESE"]), 2),
        "netto_ora": round(safe_float(row["NETTO_ORA"]), 2),
        "tipo_contratto": normalize_text(row["TIPO_CONTRATTO"]),
        "scadenza_contratto": format_scadenza(row["SCADENZA_CONTRATTO"]),
        "giorni_lavorati": stats["GIORNI_LAVORATI"],
        "giorni_modificati": stats["GIORNI_MODIFICATI"],
        "tot_ore_lavorative_mese": stats["TOT_ORE_LAVORATIVE_MESE"],
        "tot_ore_azzerate": stats["TOT_ORE_AZZERATE"],
        "tot_euro_da_scalare": stats["TOT_€_DA_SCALARE"],
        "lucchetto_foglio": False,
        "lucchetto_mese": False,
        "arretrati": 0.0,
        "extra": 0.0,
        "affiancamenti": 0.0,
        "domeniche": 0.0,
        "rimborso": 0.0,
        "rimborso_allegati": [],
        "note_generali": "",
        "tabella": tabella,
        "tot_attivita": stats["TOT_ATTIVITA_€"],
        "tot_netto_mese": 0.0,
    }
    update_sheet_totals(record)
    return record


def update_sheet_totals(record: dict):
    record["tabella"], _ = apply_step3_rules(
        tabella=record["tabella"],
        netto_ora=record["netto_ora"],
        societa=record["societa"],
        origine_master=normalize_upper(record["origine_master"]),
    )
    stats = calculate_sheet_stats(record["tabella"], normalize_upper(record["origine_master"]))
    record["giorni_lavorati"] = stats["GIORNI_LAVORATI"]
    record["giorni_modificati"] = stats["GIORNI_MODIFICATI"]
    record["tot_ore_lavorative_mese"] = stats["TOT_ORE_LAVORATIVE_MESE"]
    record["tot_ore_azzerate"] = stats["TOT_ORE_AZZERATE"]
    record["tot_euro_da_scalare"] = stats["TOT_€_DA_SCALARE"]
    record["tot_attivita"] = stats["TOT_ATTIVITA_€"]
    record["tot_netto_mese"] = round(
        safe_float(record["tot_attivita"])
        + safe_float(record["arretrati"])
        + safe_float(record["extra"])
        + safe_float(record["affiancamenti"])
        + safe_float(record["domeniche"])
        + safe_float(record["rimborso"]),
        2,
    )


def clear_entire_sheet(record: dict):
    df = record["tabella"].copy()

    df["EDICOLA_ORE"] = 0.0
    df["EDICOLA_€"] = 0.0
    df["EDICOLA_TIPO_ASSENZA"] = ""

    df["MONDADORI_ORE"] = 0.0
    df["MONDADORI_€"] = 0.0
    df["MONDADORI_TIPO_ASSENZA"] = ""

    df["GIUNTI_ORE"] = 0.0
    df["GIUNTI_€"] = 0.0
    df["GIUNTI_TIPO_ASSENZA"] = ""

    df["ROW_STATUS"] = ""
    df = update_data_view(df)
    record["tabella"] = df

    record["arretrati"] = 0.0
    record["extra"] = 0.0
    record["affiancamenti"] = 0.0
    record["domeniche"] = 0.0
    record["rimborso"] = 0.0
    record["rimborso_allegati"] = []
    record["note_generali"] = ""

    record["tabella"], _ = apply_step3_rules(
        tabella=record["tabella"],
        netto_ora=record["netto_ora"],
        societa=record["societa"],
        origine_master=normalize_upper(record["origine_master"]),
    )
    update_sheet_totals(record)


# =========================
# SESSIONE
# =========================

def ensure_session_state():
    defaults = {
        "df_edicola": pd.DataFrame(),
        "df_libri": pd.DataFrame(),
        "df_spot": pd.DataFrame(),
        "generation_table": pd.DataFrame(),
        "fogli_generati": {},
        "foglio_attivo": None,
        "master_loaded": False,
        "sheet_warnings": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================
# PAGINE
# =========================

def render_master_page():
    render_page_title("1. Caricamento master reali")
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        file_edicola = st.file_uploader("Master Edicola", type=["xlsx"], key="upload_edicola")
    with col2:
        file_libri = st.file_uploader("Master Libri", type=["xlsx"], key="upload_libri")
    with col3:
        file_spot = st.file_uploader("Master Sostituti Spot", type=["xlsx"], key="upload_spot")

    if st.button("Verifica e carica master", type="primary", use_container_width=True):
        if not file_edicola or not file_libri or not file_spot:
            st.error("Per lo STEP 3 vanno caricati tutti e 3 i master reali.")
            st.stop()

        try:
            df_edicola_raw = pd.read_excel(file_edicola)
            df_libri_raw = pd.read_excel(file_libri)
            df_spot_raw = pd.read_excel(file_spot)
        except Exception as exc:
            st.error(f"Errore nella lettura dei file Excel: {exc}")
            st.stop()

        df_edicola_raw = clean_columns(df_edicola_raw)
        df_libri_raw = clean_columns(df_libri_raw)
        df_spot_raw = clean_columns(df_spot_raw)

        missing_edicola = validate_columns(df_edicola_raw, COLONNE_MASTER_EDICOLA)
        missing_libri = validate_columns(df_libri_raw, COLONNE_MASTER_LIBRI)
        missing_spot = validate_columns(df_spot_raw, COLONNE_MASTER_SPOT)

        if missing_edicola:
            st.error(f"Master Edicola non valido. Colonne mancanti: {', '.join(missing_edicola)}")
            st.stop()
        if missing_libri:
            st.error(f"Master Libri non valido. Colonne mancanti: {', '.join(missing_libri)}")
            st.stop()
        if missing_spot:
            st.error(f"Master Sostituti Spot non valido. Colonne mancanti: {', '.join(missing_spot)}")
            st.stop()

        st.session_state["df_edicola"] = normalize_master_edicola(df_edicola_raw)
        st.session_state["df_libri"] = normalize_master_libri(df_libri_raw)
        st.session_state["df_spot"] = normalize_master_spot(df_spot_raw)
        st.session_state["generation_table"] = build_generation_table(
            st.session_state["df_edicola"],
            st.session_state["df_libri"],
        )
        st.session_state["master_loaded"] = True
        st.success("Master verificati e caricati correttamente.")

    if st.session_state["master_loaded"]:
        with st.expander("Visualizza intestazioni reali e anteprima master"):
            st.write("**Master Edicola**")
            st.write(list(st.session_state["df_edicola"].columns))
            st.dataframe(st.session_state["df_edicola"].head(10), use_container_width=True)

            st.write("**Master Libri**")
            st.write(list(st.session_state["df_libri"].columns))
            st.dataframe(st.session_state["df_libri"].head(10), use_container_width=True)

            st.write("**Master Sostituti Spot**")
            st.write(list(st.session_state["df_spot"].columns))
            st.dataframe(st.session_state["df_spot"].head(10), use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_generation_page():
    render_page_title("2. Generazione fogli presenze")
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    if not st.session_state["master_loaded"]:
        st.warning("Prima carica e verifica i master nella sezione 'Caricamento master'.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    col1, col2 = st.columns([1, 1])
    with col1:
        anno = st.selectbox("Anno", [2025, 2026, 2027], index=1, key="anno_step3")
    with col2:
        mese = st.selectbox("Mese", list(MESI.keys()), format_func=lambda x: MESI[x], index=0, key="mese_step3")

    filtro_nome = st.text_input("Filtro semplice nome/cognome", placeholder="Scrivi nome o cognome")

    generation_table = st.session_state["generation_table"].copy()
    if generation_table.empty:
        st.warning("Nessuna riga disponibile per la generazione dei fogli.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if filtro_nome.strip():
        mask = generation_table["NOME"].str.upper().str.contains(filtro_nome.strip().upper(), na=False)
        generation_table = generation_table[mask].copy()

    if generation_table.empty:
        st.info("Nessun risultato trovato con il filtro inserito.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    edited = st.data_editor(
        generation_table,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "SELEZIONA": st.column_config.CheckboxColumn("Seleziona"),
            "ROW_ID": None,
            "MASTER_INDEX": None,
            "ORIGINE_MASTER": st.column_config.TextColumn("Master origine", disabled=True),
            "TIPO_LIBRI": st.column_config.TextColumn("Tipo libri", disabled=True),
            "NOME": st.column_config.TextColumn("Nome", disabled=True),
            "COD_FISCALE": st.column_config.TextColumn("CF", disabled=True),
            "SOCIETA": st.column_config.TextColumn("Società", disabled=True),
            "PDV": st.column_config.TextColumn("PDV", disabled=True),
            "TELEFONO": st.column_config.TextColumn("Telefono", disabled=True),
            "EMAIL": st.column_config.TextColumn("Email", disabled=True),
            "NETTO_ORA": st.column_config.NumberColumn("Netto orario", format="%.2f €", disabled=True),
            "NETTO_MESE": st.column_config.NumberColumn("Netto mese", format="%.2f €", disabled=True),
            "TIPO_CONTRATTO": st.column_config.TextColumn("Tipo contratto", disabled=True),
            "SCADENZA_CONTRATTO": st.column_config.TextColumn("Scadenza contratto", disabled=True),
            "ATTIVITA_RIGA": st.column_config.TextColumn("Attività", disabled=True),
        },
        key="editor_generation_table",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Genera fogli presenze selezionati", type="primary", use_container_width=True):
        selected = edited[edited["SELEZIONA"] == True].copy()
        if selected.empty:
            st.warning("Seleziona almeno una riga.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        for _, row in selected.iterrows():
            key = format_sheet_key(normalize_text(row["ROW_ID"]), anno, mese)
            st.session_state["fogli_generati"][key] = init_sheet_record(
                row=row,
                df_edicola=st.session_state["df_edicola"],
                df_libri=st.session_state["df_libri"],
                anno=anno,
                mese=mese,
            )
            st.session_state["foglio_attivo"] = key
            st.session_state["sheet_warnings"][key] = []

        st.success("Fogli presenze generati correttamente.")

    st.markdown("</div>", unsafe_allow_html=True)


def render_sheet_page():
    render_page_title("3. Gestione foglio presenze")
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    if not st.session_state["fogli_generati"]:
        st.warning("Prima genera almeno un foglio nella sezione 'Generazione fogli'.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    keys = list(st.session_state["fogli_generati"].keys())
    if st.session_state["foglio_attivo"] not in keys:
        st.session_state["foglio_attivo"] = keys[0]

    selected_key = st.selectbox(
        "Seleziona foglio attivo",
        options=keys,
        index=keys.index(st.session_state["foglio_attivo"]),
        format_func=lambda k: (
            f"{st.session_state['fogli_generati'][k]['nome']} | "
            f"{st.session_state['fogli_generati'][k]['societa']} | "
            f"{st.session_state['fogli_generati'][k]['pdv']} | "
            f"{st.session_state['fogli_generati'][k]['attivita_riga']} | "
            f"{MESI[st.session_state['fogli_generati'][k]['mese']]} {st.session_state['fogli_generati'][k]['anno']}"
        ),
    )
    st.session_state["foglio_attivo"] = selected_key
    record = st.session_state["fogli_generati"][selected_key]

    locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        st.text_input("Società", value=record["societa"], disabled=True)
        st.text_input("Attività", value=record["attivita_riga"], disabled=True)
        st.text_input("Nome", value=record["nome"], disabled=True)
    with col_h2:
        st.text_input("CF", value=record["cf"], disabled=True)
        st.text_input("PDV", value=record["pdv"], disabled=True)
        st.text_input("Mese", value=f"{MESI[record['mese']]} {record['anno']}", disabled=True)
    with col_h3:
        record["tipo_contratto"] = st.text_input("Tipo contratto", value=record["tipo_contratto"], disabled=locked)
        record["scadenza_contratto"] = st.text_input("Scadenza contratto", value=record["scadenza_contratto"], disabled=locked)
        record["netto_mese"] = st.number_input("NETTO MESE", value=float(record["netto_mese"]), step=0.50, disabled=locked)
    with col_h4:
        record["netto_ora"] = st.number_input("Netto orario", value=float(record["netto_ora"]), step=0.10, disabled=locked)
        st.number_input("Giorni lavorati", value=int(record["giorni_lavorati"]), disabled=True)
        st.number_input("Giorni modificati", value=int(record["giorni_modificati"]), disabled=True)

    col_h5, col_h6, col_h7 = st.columns(3)
    with col_h5:
        st.number_input("Tot ore lavorative mese", value=float(record["tot_ore_lavorative_mese"]), disabled=True)
    with col_h6:
        st.number_input("Tot ore azzerate", value=float(record["tot_ore_azzerate"]), disabled=True)
    with col_h7:
        st.number_input("Tot € da scalare", value=float(record["tot_euro_da_scalare"]), disabled=True)

    col_lock1, col_lock2 = st.columns(2)
    with col_lock1:
        record["lucchetto_foglio"] = st.checkbox(
            "Lucchetto foglio",
            value=record["lucchetto_foglio"],
            disabled=record["lucchetto_mese"],
        )
    with col_lock2:
        record["lucchetto_mese"] = st.checkbox("Lucchetto mese", value=record["lucchetto_mese"])

    st.markdown("</div>", unsafe_allow_html=True)

    locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

    if selected_key in st.session_state["sheet_warnings"] and st.session_state["sheet_warnings"][selected_key]:
        for msg in st.session_state["sheet_warnings"][selected_key]:
            render_warning_box(msg)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Corpo foglio presenze</div>', unsafe_allow_html=True)

    if normalize_upper(record["origine_master"]) == ORIGINE_EDICOLA:
        st.markdown(
            """
            <div class="activity-note">
                Foglio presenza generato da riga Master Edicola.
                <div class="activity-legend">
                    <span class="activity-pill pill-edicola">EDICOLA</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        visible_cols = [
            "GIORNO_NUM",
            "DATA_VIEW",
            "GIORNO_SETTIMANA",
            "EDICOLA_ORE",
            "EDICOLA_€",
            "EDICOLA_TIPO_ASSENZA",
            "FESTIVO",
        ]

        display_df = record["tabella"][COLONNE_TABELLA_TECNICHE].copy().reset_index(drop=True)

        edited = st.data_editor(
            display_df[visible_cols],
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=locked,
            column_config={
                "GIORNO_NUM": st.column_config.NumberColumn("Giorno", disabled=True),
                "DATA_VIEW": st.column_config.TextColumn("Data", disabled=True),
                "GIORNO_SETTIMANA": st.column_config.TextColumn("Giorno settimana", disabled=True),
                "EDICOLA_ORE": st.column_config.NumberColumn("Edicola Ore", min_value=0.0, step=0.5, format="%.2f"),
                "EDICOLA_€": st.column_config.NumberColumn("Edicola €", format="%.2f €", disabled=True),
                "EDICOLA_TIPO_ASSENZA": st.column_config.SelectboxColumn("Edicola Tipo assenza", options=TIPI_ASSENZA),
                "FESTIVO": st.column_config.CheckboxColumn("Festivo"),
            },
            key=f"editor_tabella_{selected_key}",
        )

        if not locked:
            hidden_cols = record["tabella"][
                ["DATA", "ROW_STATUS"] + COLONNE_BASE_ALL + ["MONDADORI_ORE", "MONDADORI_€", "MONDADORI_TIPO_ASSENZA", "GIUNTI_ORE", "GIUNTI_€", "GIUNTI_TIPO_ASSENZA"]
            ].copy().reset_index(drop=True)

            edited_clean = edited.copy().reset_index(drop=True)
            merged = pd.concat([edited_clean, hidden_cols], axis=1)

            merged = merged[
                [
                    "GIORNO_NUM",
                    "DATA",
                    "GIORNO_SETTIMANA",
                    "DATA_VIEW",
                    "EDICOLA_ORE",
                    "EDICOLA_€",
                    "EDICOLA_TIPO_ASSENZA",
                    "MONDADORI_ORE",
                    "MONDADORI_€",
                    "MONDADORI_TIPO_ASSENZA",
                    "GIUNTI_ORE",
                    "GIUNTI_€",
                    "GIUNTI_TIPO_ASSENZA",
                    "FESTIVO",
                    "ROW_STATUS",
                    "BASE_EDICOLA_ORE",
                    "BASE_MONDADORI_ORE",
                    "BASE_GIUNTI_ORE",
                ]
            ]

            merged, warnings = apply_step3_rules(
                tabella=merged,
                netto_ora=record["netto_ora"],
                societa=record["societa"],
                origine_master=normalize_upper(record["origine_master"]),
            )

            old_visible = record["tabella"][visible_cols].copy().reset_index(drop=True)
            new_visible = merged[visible_cols].copy().reset_index(drop=True)

            record["tabella"] = merged
            st.session_state["sheet_warnings"][selected_key] = warnings
            update_sheet_totals(record)

            if not new_visible.equals(old_visible):
                st.rerun()

    else:
        st.markdown(
            """
            <div class="activity-note">
                Foglio presenza generato da riga Master Libri.
                <div class="activity-legend">
                    <span class="activity-pill pill-mondadori">MONDADORI</span>
                    <span class="activity-pill pill-giunti">GIUNTI</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        visible_cols = [
            "GIORNO_NUM",
            "DATA_VIEW",
            "GIORNO_SETTIMANA",
            "MONDADORI_ORE",
            "MONDADORI_€",
            "MONDADORI_TIPO_ASSENZA",
            "SEP_1",
            "GIUNTI_ORE",
            "GIUNTI_€",
            "GIUNTI_TIPO_ASSENZA",
            "FESTIVO",
        ]

        display_df = record["tabella"][COLONNE_TABELLA_TECNICHE].copy().reset_index(drop=True)
        display_df.insert(6, "SEP_1", "│")

        edited = st.data_editor(
            display_df[visible_cols],
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=locked,
            column_config={
                "GIORNO_NUM": st.column_config.NumberColumn("Giorno", disabled=True),
                "DATA_VIEW": st.column_config.TextColumn("Data", disabled=True),
                "GIORNO_SETTIMANA": st.column_config.TextColumn("Giorno settimana", disabled=True),
                "MONDADORI_ORE": st.column_config.NumberColumn("Mondadori Ore", min_value=0.0, step=0.5, format="%.2f"),
                "MONDADORI_€": st.column_config.NumberColumn("Mondadori €", format="%.2f €", disabled=True),
                "MONDADORI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Mondadori Tipo assenza", options=TIPI_ASSENZA),
                "SEP_1": st.column_config.TextColumn("│", disabled=True),
                "GIUNTI_ORE": st.column_config.NumberColumn("Giunti Ore", min_value=0.0, step=0.5, format="%.2f"),
                "GIUNTI_€": st.column_config.NumberColumn("Giunti €", format="%.2f €", disabled=True),
                "GIUNTI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Giunti Tipo assenza", options=TIPI_ASSENZA),
                "FESTIVO": st.column_config.CheckboxColumn("Festivo"),
            },
            key=f"editor_tabella_{selected_key}",
        )

        if not locked:
            edited_clean = edited.drop(columns=["SEP_1"]).copy().reset_index(drop=True)
            hidden_cols = record["tabella"][
                ["DATA", "ROW_STATUS"] + COLONNE_BASE_ALL + ["EDICOLA_ORE", "EDICOLA_€", "EDICOLA_TIPO_ASSENZA"]
            ].copy().reset_index(drop=True)

            merged = pd.concat([edited_clean, hidden_cols], axis=1)
            merged = merged[
                [
                    "GIORNO_NUM",
                    "DATA",
                    "GIORNO_SETTIMANA",
                    "DATA_VIEW",
                    "EDICOLA_ORE",
                    "EDICOLA_€",
                    "EDICOLA_TIPO_ASSENZA",
                    "MONDADORI_ORE",
                    "MONDADORI_€",
                    "MONDADORI_TIPO_ASSENZA",
                    "GIUNTI_ORE",
                    "GIUNTI_€",
                    "GIUNTI_TIPO_ASSENZA",
                    "FESTIVO",
                    "ROW_STATUS",
                    "BASE_EDICOLA_ORE",
                    "BASE_MONDADORI_ORE",
                    "BASE_GIUNTI_ORE",
                ]
            ]

            merged, warnings = apply_step3_rules(
                tabella=merged,
                netto_ora=record["netto_ora"],
                societa=record["societa"],
                origine_master=normalize_upper(record["origine_master"]),
            )

            old_visible = display_df[visible_cols].copy().reset_index(drop=True)
            new_display = merged.copy().reset_index(drop=True)
            new_display.insert(6, "SEP_1", "│")
            new_visible = new_display[visible_cols].copy().reset_index(drop=True)

            record["tabella"] = merged
            st.session_state["sheet_warnings"][selected_key] = warnings
            update_sheet_totals(record)

            if not new_visible.equals(old_visible):
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Fondo foglio</div>', unsafe_allow_html=True)

    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
    with col_b1:
        record["arretrati"] = st.number_input("€ arretrato", value=float(record["arretrati"]), step=0.50, disabled=locked)
    with col_b2:
        record["extra"] = st.number_input("€ extra", value=float(record["extra"]), step=0.50, disabled=locked)
    with col_b3:
        record["affiancamenti"] = st.number_input("€ affiancamento", value=float(record["affiancamenti"]), step=0.50, disabled=locked)
    with col_b4:
        record["domeniche"] = st.number_input("€ domeniche", value=float(record["domeniche"]), step=0.50, disabled=locked)
    with col_b5:
        record["rimborso"] = st.number_input("€ rimborso", value=float(record["rimborso"]), step=0.50, disabled=locked)

    uploaded_docs = st.file_uploader(
        "Allegati rimborso",
        accept_multiple_files=True,
        disabled=locked,
        key=f"rimborso_upload_{selected_key}",
    )
    if uploaded_docs is not None:
        record["rimborso_allegati"] = [file.name for file in uploaded_docs]

    if record["rimborso_allegati"]:
        st.caption("Allegati caricati: " + ", ".join(record["rimborso_allegati"]))

    record["note_generali"] = st.text_area(
        "NOTE GENERALI DEL MESE",
        value=record["note_generali"],
        height=130,
        disabled=locked,
    )

    update_sheet_totals(record)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Totale finale</div>', unsafe_allow_html=True)

    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.markdown(
            """
            <div class="soft-note">
                <b>Formula STEP 3</b><br>
                TOT NETTO MESE = Tot attività + Arretrati + Extra + Affiancamenti + Domeniche + Rimborsi
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_t2:
        st.metric("TOT NETTO MESE", f"€ {record['tot_netto_mese']:.2f}")

    st.markdown("</div>", unsafe_allow_html=True)

    col_reset1, col_reset2 = st.columns([1, 1])
    with col_reset1:
        if st.button("Azzera foglio presenza", disabled=locked, use_container_width=True):
            clear_entire_sheet(record)
            st.session_state["sheet_warnings"][selected_key] = []
            st.rerun()
    with col_reset2:
        st.write("")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# STEP 4 - NUOVO FOGLIO PRESENZA / SOSTITUZIONE
# DA INCOLLARE SUBITO PRIMA DEL BLOCCO APP
# =========================

STEP4_MODO_TITOLARE = "SOSTITUZIONE CON TITOLARE"
STEP4_MODO_SPOT = "SOSTITUZIONE CON SOSTITUTO SPOT"
STEP4_MODO_VUOTO = "FOGLIO PRESENZA VUOTO"


def ensure_session_state():
    defaults = {
        "df_edicola": pd.DataFrame(),
        "df_libri": pd.DataFrame(),
        "df_spot": pd.DataFrame(),
        "generation_table": pd.DataFrame(),
        "fogli_generati": {},
        "foglio_attivo": None,
        "master_loaded": False,
        "sheet_warnings": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def step4_build_empty_presence_dataframe(attivita: str, anno: int, mese: int) -> pd.DataFrame:
    giorni_mese = calendar.monthrange(anno, mese)[1]
    righe = []

    for giorno_num in range(1, giorni_mese + 1):
        current_date = date(anno, mese, giorno_num)
        festivo_default = current_date.weekday() == 6

        righe.append(
            {
                "GIORNO_NUM": giorno_num,
                "DATA": current_date.strftime("%d/%m/%Y"),
                "GIORNO_SETTIMANA": get_day_label(current_date),
                "DATA_VIEW": current_date.strftime("%d/%m/%Y"),
                "EDICOLA_ORE": 0.0,
                "EDICOLA_€": 0.0,
                "EDICOLA_TIPO_ASSENZA": "",
                "MONDADORI_ORE": 0.0,
                "MONDADORI_€": 0.0,
                "MONDADORI_TIPO_ASSENZA": "",
                "GIUNTI_ORE": 0.0,
                "GIUNTI_€": 0.0,
                "GIUNTI_TIPO_ASSENZA": "",
                "FESTIVO": festivo_default,
                "ROW_STATUS": "",
                "BASE_EDICOLA_ORE": 0.0,
                "BASE_MONDADORI_ORE": 0.0,
                "BASE_GIUNTI_ORE": 0.0,
                "STEP4_ALLOW_MANUAL": True,
            }
        )

    df = pd.DataFrame(righe)
    if normalize_upper(attivita) == ORIGINE_EDICOLA:
        df["MONDADORI_ORE"] = 0.0
        df["MONDADORI_€"] = 0.0
        df["MONDADORI_TIPO_ASSENZA"] = ""
        df["GIUNTI_ORE"] = 0.0
        df["GIUNTI_€"] = 0.0
        df["GIUNTI_TIPO_ASSENZA"] = ""
    else:
        df["EDICOLA_ORE"] = 0.0
        df["EDICOLA_€"] = 0.0
        df["EDICOLA_TIPO_ASSENZA"] = ""

    return df


def step4_get_societa_options() -> list[str]:
    societa = set()

    if not st.session_state["df_edicola"].empty:
        societa.update(st.session_state["df_edicola"]["AGENZIA"].dropna().astype(str).str.strip().tolist())

    if not st.session_state["df_libri"].empty:
        societa.update(st.session_state["df_libri"]["AGENZIA"].dropna().astype(str).str.strip().tolist())

    return sorted([x for x in societa if normalize_text(x) != ""])


def step4_extract_main_candidates(societa: str, attivita: str) -> list[dict]:
    candidati = []

    if normalize_upper(attivita) == ORIGINE_EDICOLA:
        df = st.session_state["df_edicola"].copy()
        if not df.empty:
            df = df[df["AGENZIA"].astype(str).str.strip().str.upper() == normalize_upper(societa)].copy()

            for idx, row in df.reset_index(drop=True).iterrows():
                candidati.append(
                    {
                        "CANDIDATE_ID": f"MAIN_EDICOLA_{idx}",
                        "MASTER_INDEX": idx,
                        "ORIGINE_MASTER": ORIGINE_EDICOLA,
                        "ATTIVITA": "EDICOLA",
                        "TIPO_LIBRI": "",
                        "NOME": normalize_text(row["MHS_TITOLARE"]),
                        "COD_FISCALE": normalize_text(row["COD_FISCALE"]),
                        "SOCIETA": normalize_text(row["AGENZIA"]),
                        "PDV": normalize_text(row["PDV"]),
                        "TELEFONO": normalize_text(row["TEL_MHS"]),
                        "EMAIL": normalize_text(row["MAIL_MHS"]),
                        "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                        "NETTO_MESE": safe_float(row["COMPENSO_MENSILE"]),
                        "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                        "SCADENZA_CONTRATTO": format_scadenza(row["SCADENZA_CONTRATTO"]),
                        "ORE_LUN": safe_float(row["LUN"]),
                        "ORE_MAR": safe_float(row["MAR"]),
                        "ORE_MER": safe_float(row["MER"]),
                        "ORE_GIO": safe_float(row["GIO"]),
                        "ORE_VEN": safe_float(row["VEN"]),
                        "ORE_SAB": safe_float(row["SAB"]),
                        "ORE_DOM": safe_float(row["DOM"]),
                    }
                )
    else:
        df = st.session_state["df_libri"].copy()
        if not df.empty:
            df = df[df["AGENZIA"].astype(str).str.strip().str.upper() == normalize_upper(societa)].copy()

            for idx, row in df.reset_index(drop=True).iterrows():
                tipo_libri = normalize_upper(row["TIPO_LIBRI"])
                candidati.append(
                    {
                        "CANDIDATE_ID": f"MAIN_LIBRI_{idx}",
                        "MASTER_INDEX": idx,
                        "ORIGINE_MASTER": ORIGINE_LIBRI,
                        "ATTIVITA": "LIBRI",
                        "TIPO_LIBRI": tipo_libri,
                        "NOME": normalize_text(row["MHS_TITOLARE"]),
                        "COD_FISCALE": normalize_text(row["COD_FISCALE"]),
                        "SOCIETA": normalize_text(row["AGENZIA"]),
                        "PDV": normalize_text(row["PDV"]),
                        "TELEFONO": normalize_text(row["TEL_MHS"]),
                        "EMAIL": normalize_text(row["MAIL_MHS"]),
                        "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                        "NETTO_MESE": 0.0,
                        "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                        "SCADENZA_CONTRATTO": format_scadenza(row["SCADENZA_CONTRATTO"]),
                        "ORE_LUN": safe_float(row["LUN"]),
                        "ORE_MAR": safe_float(row["MAR"]),
                        "ORE_MER": safe_float(row["MER"]),
                        "ORE_GIO": safe_float(row["GIO"]),
                        "ORE_VEN": safe_float(row["VEN"]),
                        "ORE_SAB": safe_float(row["SAB"]),
                        "ORE_DOM": safe_float(row["DOM"]),
                    }
                )

    return candidati


def step4_extract_spot_candidates() -> list[dict]:
    candidati = []
    df = st.session_state["df_spot"].copy()

    if df.empty:
        return candidati

    for idx, row in df.reset_index(drop=True).iterrows():
        candidati.append(
            {
                "CANDIDATE_ID": f"SPOT_{idx}",
                "NOME": normalize_text(row["MHS_SOSTITUTO_SPOT"]),
                "COD_FISCALE": normalize_text(row["COD_FISCALE"]),
                "TELEFONO": normalize_text(row["TEL"]),
                "EMAIL": normalize_text(row["MAIL"]),
                "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                "SCADENZA_CONTRATTO": format_scadenza(row["SCADENZA_CONTRATTO"]),
            }
        )

    return candidati


def step4_get_candidate_label(candidato: dict) -> str:
    tipo_libri = normalize_text(candidato.get("TIPO_LIBRI", ""))
    suffix = f" | {tipo_libri}" if tipo_libri else ""
    return (
        f"{normalize_text(candidato.get('NOME', ''))}"
        f" | {normalize_text(candidato.get('PDV', ''))}"
        f" | {normalize_text(candidato.get('COD_FISCALE', ''))}"
        f"{suffix}"
    )


def step4_get_spot_label(candidato: dict) -> str:
    return (
        f"{normalize_text(candidato.get('NOME', ''))}"
        f" | {normalize_text(candidato.get('COD_FISCALE', ''))}"
        f" | Netto/ora {safe_float(candidato.get('NETTO_ORA', 0.0)):.2f}"
    )


def step4_find_candidate_by_id(candidati: list[dict], candidate_id: str) -> dict | None:
    for candidato in candidati:
        if normalize_text(candidato.get("CANDIDATE_ID", "")) == normalize_text(candidate_id):
            return candidato
    return None


def step4_get_selected_days_list(tipo_periodo: str, anno: int, mese: int, giorno_singolo: int | None, periodo_range) -> list[int]:
    if tipo_periodo == "Giorno singolo":
        if giorno_singolo is None:
            return []
        return [int(giorno_singolo)]

    if not periodo_range or len(periodo_range) != 2:
        return []

    data_inizio, data_fine = periodo_range
    if not data_inizio or not data_fine:
        return []

    if data_inizio > data_fine:
        return []

    primo_giorno_mese = date(anno, mese, 1)
    ultimo_giorno_mese = date(anno, mese, calendar.monthrange(anno, mese)[1])

    if data_inizio < primo_giorno_mese or data_fine > ultimo_giorno_mese:
        return []

    giorni = []
    current = data_inizio
    while current <= data_fine:
        giorni.append(current.day)
        current = current.fromordinal(current.toordinal() + 1)

    return giorni


def step4_days_to_text(giorni: list[int]) -> str:
    if not giorni:
        return ""
    if len(giorni) == 1:
        return f"Giorno {giorni[0]}"
    return f"Giorni da {min(giorni)} a {max(giorni)}"


def step4_init_sheet_record(
    modo_creazione: str,
    societa: str,
    attivita: str,
    anno: int,
    mese: int,
    selected_days: list[int],
    main_candidates: list[dict],
    spot_candidates: list[dict],
) -> dict:
    row_id = f"STEP4_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    origine_master = ORIGINE_EDICOLA if normalize_upper(attivita) == ORIGINE_EDICOLA else ORIGINE_LIBRI
    tabella = step4_build_empty_presence_dataframe(attivita=attivita, anno=anno, mese=mese)

    record = {
        "row_id": row_id,
        "origine_master": origine_master,
        "tipo_libri": "",
        "attivita_riga": normalize_upper(attivita),
        "societa": normalize_text(societa),
        "mese": mese,
        "anno": anno,
        "nome": "",
        "cf": "",
        "pdv": "",
        "telefono": "",
        "email": "",
        "netto_mese": 0.0,
        "netto_ora": 0.0,
        "tipo_contratto": "",
        "scadenza_contratto": "",
        "giorni_lavorati": 0,
        "giorni_modificati": 0,
        "tot_ore_lavorative_mese": 0.0,
        "tot_ore_azzerate": 0.0,
        "tot_euro_da_scalare": 0.0,
        "lucchetto_foglio": False,
        "lucchetto_mese": False,
        "arretrati": 0.0,
        "extra": 0.0,
        "affiancamenti": 0.0,
        "domeniche": 0.0,
        "rimborso": 0.0,
        "rimborso_allegati": [],
        "note_generali": "",
        "tabella": tabella,
        "tot_attivita": 0.0,
        "tot_netto_mese": 0.0,
        "is_step4": True,
        "step4_mode": normalize_text(modo_creazione),
        "step4_selected_days": list(selected_days),
        "step4_main_candidates": deepcopy(main_candidates),
        "step4_spot_candidates": deepcopy(spot_candidates),
        "step4_main_candidate_id": "",
        "step4_spot_candidate_id": "",
    }

    update_sheet_totals(record)
    return record


def step4_apply_main_candidate_to_record(record: dict, candidato: dict):
    if not candidato:
        return

    selected_days = record.get("step4_selected_days", [])
    attivita = normalize_upper(record["attivita_riga"])
    modo = normalize_upper(record.get("step4_mode", ""))

    record["step4_main_candidate_id"] = normalize_text(candidato["CANDIDATE_ID"])
    record["societa"] = normalize_text(candidato["SOCIETA"])
    record["pdv"] = normalize_text(candidato["PDV"])

    if modo != STEP4_MODO_SPOT:
        record["nome"] = normalize_text(candidato["NOME"])
        record["cf"] = normalize_text(candidato["COD_FISCALE"])
        record["telefono"] = normalize_text(candidato["TELEFONO"])
        record["email"] = normalize_text(candidato["EMAIL"])
        record["netto_ora"] = round(safe_float(candidato["NETTO_ORA"]), 2)
        record["netto_mese"] = round(safe_float(candidato["NETTO_MESE"]), 2)
        record["tipo_contratto"] = normalize_text(candidato["TIPO_CONTRATTO"])
        record["scadenza_contratto"] = normalize_text(candidato["SCADENZA_CONTRATTO"])

    record["tipo_libri"] = normalize_text(candidato.get("TIPO_LIBRI", ""))

    df = record["tabella"].copy()

    for idx in df.index:
        giorno_num = int(df.at[idx, "GIORNO_NUM"])
        if giorno_num not in selected_days:
            continue

        giorno_settimana = normalize_upper(df.at[idx, "GIORNO_SETTIMANA"])
        ore_master = safe_float(candidato.get(f"ORE_{giorno_settimana}", 0.0))

        if attivita == ORIGINE_EDICOLA:
            df.at[idx, "BASE_EDICOLA_ORE"] = ore_master
            df.at[idx, "EDICOLA_ORE"] = ore_master
            df.at[idx, "EDICOLA_TIPO_ASSENZA"] = ""
        else:
            tipo_libri = normalize_upper(candidato.get("TIPO_LIBRI", ""))
            if tipo_libri == "MONDADORI":
                df.at[idx, "BASE_MONDADORI_ORE"] = ore_master
                df.at[idx, "MONDADORI_ORE"] = ore_master
                df.at[idx, "MONDADORI_TIPO_ASSENZA"] = ""
            elif tipo_libri == "GIUNTI":
                df.at[idx, "BASE_GIUNTI_ORE"] = ore_master
                df.at[idx, "GIUNTI_ORE"] = ore_master
                df.at[idx, "GIUNTI_TIPO_ASSENZA"] = ""

    record["tabella"] = df
    update_sheet_totals(record)


def step4_apply_spot_candidate_to_record(record: dict, candidato: dict):
    if not candidato:
        return

    record["step4_spot_candidate_id"] = normalize_text(candidato["CANDIDATE_ID"])
    record["nome"] = normalize_text(candidato["NOME"])
    record["cf"] = normalize_text(candidato["COD_FISCALE"])
    record["telefono"] = normalize_text(candidato["TELEFONO"])
    record["email"] = normalize_text(candidato["EMAIL"])
    record["netto_ora"] = round(safe_float(candidato["NETTO_ORA"]), 2)
    record["tipo_contratto"] = normalize_text(candidato["TIPO_CONTRATTO"])
    record["scadenza_contratto"] = normalize_text(candidato["SCADENZA_CONTRATTO"])

    update_sheet_totals(record)


def get_row_status(df: pd.DataFrame, idx: int) -> str:
    base_tot = round(
        safe_float(df.at[idx, "BASE_EDICOLA_ORE"])
        + safe_float(df.at[idx, "BASE_MONDADORI_ORE"])
        + safe_float(df.at[idx, "BASE_GIUNTI_ORE"]),
        2,
    )
    current_tot = round(
        safe_float(df.at[idx, "EDICOLA_ORE"])
        + safe_float(df.at[idx, "MONDADORI_ORE"])
        + safe_float(df.at[idx, "GIUNTI_ORE"]),
        2,
    )

    has_assenza = (
        normalize_text(df.at[idx, "EDICOLA_TIPO_ASSENZA"]) != ""
        or normalize_text(df.at[idx, "MONDADORI_TIPO_ASSENZA"]) != ""
        or normalize_text(df.at[idx, "GIUNTI_TIPO_ASSENZA"]) != ""
    )

    manual_mode = False
    if "STEP4_ALLOW_MANUAL" in df.columns:
        manual_mode = bool(df.at[idx, "STEP4_ALLOW_MANUAL"])

    if manual_mode:
        if has_assenza or round(current_tot, 2) != round(base_tot, 2):
            return "MODIFICATA"
        return ""

    if has_assenza or current_tot < base_tot:
        return "MODIFICATA"
    return ""


def apply_step3_rules(tabella: pd.DataFrame, netto_ora: float, societa: str, origine_master: str) -> tuple[pd.DataFrame, list[str]]:
    df = tabella.copy()
    warnings = []

    for col in ["EDICOLA_ORE", "MONDADORI_ORE", "GIUNTI_ORE"]:
        df[col] = df[col].apply(safe_float)

    for idx in df.index:
        manual_mode = False
        if "STEP4_ALLOW_MANUAL" in df.columns:
            manual_mode = bool(df.at[idx, "STEP4_ALLOW_MANUAL"])

        if origine_master == ORIGINE_EDICOLA:
            allowed = [("EDICOLA", "BASE_EDICOLA_ORE")]
            blocked = [("MONDADORI", "BASE_MONDADORI_ORE"), ("GIUNTI", "BASE_GIUNTI_ORE")]
        else:
            allowed = [("MONDADORI", "BASE_MONDADORI_ORE"), ("GIUNTI", "BASE_GIUNTI_ORE")]
            blocked = [("EDICOLA", "BASE_EDICOLA_ORE")]

        for attivita, _ in blocked:
            ore_col = f"{attivita}_ORE"
            euro_col = f"{attivita}_€"
            assenza_col = f"{attivita}_TIPO_ASSENZA"
            df.at[idx, ore_col] = 0.0
            df.at[idx, euro_col] = 0.0
            df.at[idx, assenza_col] = ""

        for attivita, base_col in allowed:
            ore_col = f"{attivita}_ORE"
            euro_col = f"{attivita}_€"
            assenza_col = f"{attivita}_TIPO_ASSENZA"

            base_value = safe_float(df.at[idx, base_col])
            new_value = max(0.0, safe_float(df.at[idx, ore_col]))

            if (not manual_mode) and new_value > base_value:
                df.at[idx, ore_col] = base_value
                warnings.append(
                    f"Giorno {int(df.at[idx, 'GIORNO_NUM'])}: non è consentito aumentare le ore oltre il valore generato."
                )
            else:
                df.at[idx, ore_col] = new_value

            if safe_float(df.at[idx, ore_col]) > 0 and normalize_text(df.at[idx, assenza_col]) != "":
                df.at[idx, assenza_col] = ""

            df.at[idx, euro_col] = calculate_row_amount(
                df.at[idx, ore_col],
                netto_ora,
                bool(df.at[idx, "FESTIVO"]),
                societa,
            )

        df.at[idx, "ROW_STATUS"] = get_row_status(df, idx)

    df = update_data_view(df)

    if warnings:
        warnings = list(dict.fromkeys(warnings))

    return df, warnings


def render_generation_page():
    render_page_title("2. Generazione fogli presenze")
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    if not st.session_state["master_loaded"]:
        st.warning("Prima carica e verifica i master nella sezione 'Caricamento master'.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    col1, col2 = st.columns([1, 1])
    with col1:
        anno = st.selectbox("Anno", [2025, 2026, 2027], index=1, key="anno_step3")
    with col2:
        mese = st.selectbox("Mese", list(MESI.keys()), format_func=lambda x: MESI[x], index=0, key="mese_step3")

    filtro_nome = st.text_input("Filtro semplice nome/cognome", placeholder="Scrivi nome o cognome")

    generation_table = st.session_state["generation_table"].copy()
    if generation_table.empty:
        st.warning("Nessuna riga disponibile per la generazione dei fogli.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if filtro_nome.strip():
        mask = generation_table["NOME"].str.upper().str.contains(filtro_nome.strip().upper(), na=False)
        generation_table = generation_table[mask].copy()

    if generation_table.empty:
        st.info("Nessun risultato trovato con il filtro inserito.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    edited = st.data_editor(
        generation_table,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "SELEZIONA": st.column_config.CheckboxColumn("Seleziona"),
            "ROW_ID": None,
            "MASTER_INDEX": None,
            "ORIGINE_MASTER": st.column_config.TextColumn("Master origine", disabled=True),
            "TIPO_LIBRI": st.column_config.TextColumn("Tipo libri", disabled=True),
            "NOME": st.column_config.TextColumn("Nome", disabled=True),
            "COD_FISCALE": st.column_config.TextColumn("CF", disabled=True),
            "SOCIETA": st.column_config.TextColumn("Società", disabled=True),
            "PDV": st.column_config.TextColumn("PDV", disabled=True),
            "TELEFONO": st.column_config.TextColumn("Telefono", disabled=True),
            "EMAIL": st.column_config.TextColumn("Email", disabled=True),
            "NETTO_ORA": st.column_config.NumberColumn("Netto orario", format="%.2f €", disabled=True),
            "NETTO_MESE": st.column_config.NumberColumn("Netto mese", format="%.2f €", disabled=True),
            "TIPO_CONTRATTO": st.column_config.TextColumn("Tipo contratto", disabled=True),
            "SCADENZA_CONTRATTO": st.column_config.TextColumn("Scadenza contratto", disabled=True),
            "ATTIVITA_RIGA": st.column_config.TextColumn("Attività", disabled=True),
        },
        key="editor_generation_table",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Genera fogli presenze selezionati", type="primary", use_container_width=True):
        selected = edited[edited["SELEZIONA"] == True].copy()
        if selected.empty:
            st.warning("Seleziona almeno una riga.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        for _, row in selected.iterrows():
            key = format_sheet_key(normalize_text(row["ROW_ID"]), anno, mese)
            st.session_state["fogli_generati"][key] = init_sheet_record(
                row=row,
                df_edicola=st.session_state["df_edicola"],
                df_libri=st.session_state["df_libri"],
                anno=anno,
                mese=mese,
            )
            st.session_state["foglio_attivo"] = key
            st.session_state["sheet_warnings"][key] = []

        st.success("Fogli presenze generati correttamente.")

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">STEP 4 - Nuovo foglio presenza / sostituzione</div>', unsafe_allow_html=True)

    societa_options = step4_get_societa_options()
    giorni_mese = calendar.monthrange(anno, mese)[1]
    primo_giorno_mese = date(anno, mese, 1)
    ultimo_giorno_mese = date(anno, mese, giorni_mese)

    col_s41, col_s42 = st.columns(2)
    with col_s41:
        modo_creazione = st.selectbox(
            "Cosa vuoi fare",
            [STEP4_MODO_TITOLARE, STEP4_MODO_SPOT, STEP4_MODO_VUOTO],
            key="step4_modo_creazione",
        )
    with col_s42:
        societa_step4 = st.selectbox(
            "Società",
            societa_options,
            index=0 if societa_options else None,
            key="step4_societa",
        ) if societa_options else st.selectbox("Società", [""], key="step4_societa_fallback")

    col_s43, col_s44 = st.columns(2)
    with col_s43:
        attivita_step4 = st.selectbox("Attività", [ORIGINE_EDICOLA, ORIGINE_LIBRI], key="step4_attivita")
    with col_s44:
        tipo_periodo = st.selectbox("Giorno singolo oppure periodo", ["Giorno singolo", "Periodo"], key="step4_tipo_periodo")

    giorno_singolo = None
    periodo_range = None

    if tipo_periodo == "Giorno singolo":
        giorno_singolo = st.selectbox("Giorno", list(range(1, giorni_mese + 1)), key="step4_giorno_singolo")
    else:
        periodo_range = st.date_input(
            "Periodo",
            value=(primo_giorno_mese, primo_giorno_mese),
            min_value=primo_giorno_mese,
            max_value=ultimo_giorno_mese,
            key="step4_periodo_range",
        )

    if st.button("NUOVO FOGLIO PRESENZA / SOSTITUZIONE", type="primary", use_container_width=True):
        if not normalize_text(societa_step4):
            st.warning("Seleziona la società.")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            return

        selected_days = step4_get_selected_days_list(
            tipo_periodo=tipo_periodo,
            anno=anno,
            mese=mese,
            giorno_singolo=giorno_singolo,
            periodo_range=periodo_range,
        )

        if not selected_days:
            st.warning("Giorno o periodo non valido per il mese selezionato.")
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            return

        main_candidates = step4_extract_main_candidates(societa=societa_step4, attivita=attivita_step4)
        spot_candidates = step4_extract_spot_candidates()

        record = step4_init_sheet_record(
            modo_creazione=modo_creazione,
            societa=societa_step4,
            attivita=attivita_step4,
            anno=anno,
            mese=mese,
            selected_days=selected_days,
            main_candidates=main_candidates,
            spot_candidates=spot_candidates,
        )

        key = format_sheet_key(record["row_id"], anno, mese)
        st.session_state["fogli_generati"][key] = record
        st.session_state["foglio_attivo"] = key
        st.session_state["sheet_warnings"][key] = []

        st.success("Foglio STEP 4 creato correttamente.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_sheet_page():
    render_page_title("3. Gestione foglio presenze")
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    if not st.session_state["fogli_generati"]:
        st.warning("Prima genera almeno un foglio nella sezione 'Generazione fogli'.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    keys = list(st.session_state["fogli_generati"].keys())
    if st.session_state["foglio_attivo"] not in keys:
        st.session_state["foglio_attivo"] = keys[0]

    selected_key = st.selectbox(
        "Seleziona foglio attivo",
        options=keys,
        index=keys.index(st.session_state["foglio_attivo"]),
        format_func=lambda k: (
            f"{st.session_state['fogli_generati'][k]['nome'] or 'SENZA NOME'} | "
            f"{st.session_state['fogli_generati'][k]['societa']} | "
            f"{st.session_state['fogli_generati'][k]['pdv'] or 'SENZA PDV'} | "
            f"{st.session_state['fogli_generati'][k]['attivita_riga']} | "
            f"{MESI[st.session_state['fogli_generati'][k]['mese']]} {st.session_state['fogli_generati'][k]['anno']}"
        ),
    )
    st.session_state["foglio_attivo"] = selected_key
    record = st.session_state["fogli_generati"][selected_key]
    locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

    if record.get("is_step4", False):
        st.markdown('<div class="inner-box">', unsafe_allow_html=True)
        st.markdown('<div class="table-title">Compilazione guidata STEP 4</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="soft-note">
                <b>Modalità:</b> {record.get('step4_mode', '')}<br>
                <b>Periodo selezionato:</b> {step4_days_to_text(record.get('step4_selected_days', []))}<br>
                <b>Regola:</b> dove possibile compilazione guidata; resta comunque possibile la compilazione manuale.
            </div>
            """,
            unsafe_allow_html=True,
        )

        main_candidates = record.get("step4_main_candidates", [])
        main_map = {"": "Seleziona riga da master principale"}
        for candidato in main_candidates:
            main_map[candidato["CANDIDATE_ID"]] = step4_get_candidate_label(candidato)

        selected_main_candidate_id = st.selectbox(
            "Master principale",
            options=list(main_map.keys()),
            index=(list(main_map.keys()).index(record.get("step4_main_candidate_id", "")) if record.get("step4_main_candidate_id", "") in main_map else 0),
            format_func=lambda x: main_map[x],
            key=f"step4_main_candidate_{selected_key}",
            disabled=locked,
        )

        if st.button("Applica dati da master principale", key=f"btn_apply_main_{selected_key}", disabled=locked, use_container_width=True):
            candidato = step4_find_candidate_by_id(main_candidates, selected_main_candidate_id)
            if candidato is None:
                st.warning("Seleziona una riga valida del master principale.")
            else:
                step4_apply_main_candidate_to_record(record, candidato)
                st.session_state["sheet_warnings"][selected_key] = []
                st.rerun()

        if normalize_upper(record.get("step4_mode", "")) == STEP4_MODO_SPOT:
            st.markdown("<br>", unsafe_allow_html=True)

            spot_candidates = record.get("step4_spot_candidates", [])
            spot_map = {"": "Seleziona sostituto spot"}
            for candidato in spot_candidates:
                spot_map[candidato["CANDIDATE_ID"]] = step4_get_spot_label(candidato)

            selected_spot_candidate_id = st.selectbox(
                "Master Sostituti Spot",
                options=list(spot_map.keys()),
                index=(list(spot_map.keys()).index(record.get("step4_spot_candidate_id", "")) if record.get("step4_spot_candidate_id", "") in spot_map else 0),
                format_func=lambda x: spot_map[x],
                key=f"step4_spot_candidate_{selected_key}",
                disabled=locked,
            )

            if st.button("Applica dati da Master Sostituti Spot", key=f"btn_apply_spot_{selected_key}", disabled=locked, use_container_width=True):
                candidato = step4_find_candidate_by_id(spot_candidates, selected_spot_candidate_id)
                if candidato is None:
                    st.warning("Seleziona un sostituto spot valido.")
                else:
                    step4_apply_spot_candidate_to_record(record, candidato)
                    st.session_state["sheet_warnings"][selected_key] = []
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="inner-box">', unsafe_allow_html=True)

        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        with col_h1:
            record["societa"] = st.text_input("Società", value=record["societa"], disabled=locked, key=f"societa_{selected_key}")
            st.text_input("Attività", value=record["attivita_riga"], disabled=True, key=f"attivita_{selected_key}")
            record["nome"] = st.text_input("Nome", value=record["nome"], disabled=locked, key=f"nome_{selected_key}")
        with col_h2:
            record["cf"] = st.text_input("CF", value=record["cf"], disabled=locked, key=f"cf_{selected_key}")
            record["pdv"] = st.text_input("PDV", value=record["pdv"], disabled=locked, key=f"pdv_{selected_key}")
            st.text_input("Mese", value=f"{MESI[record['mese']]} {record['anno']}", disabled=True, key=f"mese_{selected_key}")
        with col_h3:
            record["tipo_contratto"] = st.text_input("Tipo contratto", value=record["tipo_contratto"], disabled=locked, key=f"tipocontratto_{selected_key}")
            record["scadenza_contratto"] = st.text_input("Scadenza contratto", value=record["scadenza_contratto"], disabled=locked, key=f"scadenzacontratto_{selected_key}")
            record["netto_mese"] = st.number_input("NETTO MESE", value=float(record["netto_mese"]), step=0.50, disabled=locked, key=f"nettomese_{selected_key}")
        with col_h4:
            record["netto_ora"] = st.number_input("Netto orario", value=float(record["netto_ora"]), step=0.10, disabled=locked, key=f"nettoora_{selected_key}")
            st.number_input("Giorni lavorati", value=int(record["giorni_lavorati"]), disabled=True, key=f"giornilavorati_{selected_key}")
            st.number_input("Giorni modificati", value=int(record["giorni_modificati"]), disabled=True, key=f"giornimodificati_{selected_key}")

        col_h5, col_h6, col_h7 = st.columns(3)
        with col_h5:
            st.number_input("Tot ore lavorative mese", value=float(record["tot_ore_lavorative_mese"]), disabled=True, key=f"totore_{selected_key}")
        with col_h6:
            st.number_input("Tot ore azzerate", value=float(record["tot_ore_azzerate"]), disabled=True, key=f"totoreazz_{selected_key}")
        with col_h7:
            st.number_input("Tot € da scalare", value=float(record["tot_euro_da_scalare"]), disabled=True, key=f"toteuroscalare_{selected_key}")

        col_lock1, col_lock2 = st.columns(2)
        with col_lock1:
            record["lucchetto_foglio"] = st.checkbox(
                "Lucchetto foglio",
                value=record["lucchetto_foglio"],
                disabled=record["lucchetto_mese"],
                key=f"lockfoglio_{selected_key}",
            )
        with col_lock2:
            record["lucchetto_mese"] = st.checkbox("Lucchetto mese", value=record["lucchetto_mese"], key=f"lockmese_{selected_key}")

        st.markdown("</div>", unsafe_allow_html=True)

        locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

        if selected_key in st.session_state["sheet_warnings"] and st.session_state["sheet_warnings"][selected_key]:
            for msg in st.session_state["sheet_warnings"][selected_key]:
                render_warning_box(msg)

        st.markdown('<div class="inner-box">', unsafe_allow_html=True)
        st.markdown('<div class="table-title">Corpo foglio presenze</div>', unsafe_allow_html=True)

        if normalize_upper(record["origine_master"]) == ORIGINE_EDICOLA:
            st.markdown(
                """
                <div class="activity-note">
                    Foglio presenza STEP 4 struttura Edicola.
                    <div class="activity-legend">
                        <span class="activity-pill pill-edicola">EDICOLA</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            visible_cols = [
                "GIORNO_NUM",
                "DATA_VIEW",
                "GIORNO_SETTIMANA",
                "EDICOLA_ORE",
                "EDICOLA_€",
                "EDICOLA_TIPO_ASSENZA",
                "FESTIVO",
            ]

            display_df = record["tabella"].copy().reset_index(drop=True)

            edited = st.data_editor(
                display_df[visible_cols],
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                disabled=locked,
                column_config={
                    "GIORNO_NUM": st.column_config.NumberColumn("Giorno", disabled=True),
                    "DATA_VIEW": st.column_config.TextColumn("Data", disabled=True),
                    "GIORNO_SETTIMANA": st.column_config.TextColumn("Giorno settimana", disabled=True),
                    "EDICOLA_ORE": st.column_config.NumberColumn("Edicola Ore", min_value=0.0, step=0.5, format="%.2f"),
                    "EDICOLA_€": st.column_config.NumberColumn("Edicola €", format="%.2f €", disabled=True),
                    "EDICOLA_TIPO_ASSENZA": st.column_config.SelectboxColumn("Edicola Tipo assenza", options=TIPI_ASSENZA),
                    "FESTIVO": st.column_config.CheckboxColumn("Festivo"),
                },
                key=f"editor_tabella_{selected_key}",
            )

            if not locked:
                hidden_cols = record["tabella"][
                    [
                        "DATA",
                        "ROW_STATUS",
                        "BASE_EDICOLA_ORE",
                        "BASE_MONDADORI_ORE",
                        "BASE_GIUNTI_ORE",
                        "MONDADORI_ORE",
                        "MONDADORI_€",
                        "MONDADORI_TIPO_ASSENZA",
                        "GIUNTI_ORE",
                        "GIUNTI_€",
                        "GIUNTI_TIPO_ASSENZA",
                        "STEP4_ALLOW_MANUAL",
                    ]
                ].copy().reset_index(drop=True)

                edited_clean = edited.copy().reset_index(drop=True)
                merged = pd.concat([edited_clean, hidden_cols], axis=1)

                merged = merged[
                    [
                        "GIORNO_NUM",
                        "DATA",
                        "GIORNO_SETTIMANA",
                        "DATA_VIEW",
                        "EDICOLA_ORE",
                        "EDICOLA_€",
                        "EDICOLA_TIPO_ASSENZA",
                        "MONDADORI_ORE",
                        "MONDADORI_€",
                        "MONDADORI_TIPO_ASSENZA",
                        "GIUNTI_ORE",
                        "GIUNTI_€",
                        "GIUNTI_TIPO_ASSENZA",
                        "FESTIVO",
                        "ROW_STATUS",
                        "BASE_EDICOLA_ORE",
                        "BASE_MONDADORI_ORE",
                        "BASE_GIUNTI_ORE",
                        "STEP4_ALLOW_MANUAL",
                    ]
                ]

                merged, warnings = apply_step3_rules(
                    tabella=merged,
                    netto_ora=record["netto_ora"],
                    societa=record["societa"],
                    origine_master=normalize_upper(record["origine_master"]),
                )

                old_visible = record["tabella"][visible_cols].copy().reset_index(drop=True)
                new_visible = merged[visible_cols].copy().reset_index(drop=True)

                record["tabella"] = merged
                st.session_state["sheet_warnings"][selected_key] = warnings
                update_sheet_totals(record)

                if not new_visible.equals(old_visible):
                    st.rerun()

        else:
            st.markdown(
                """
                <div class="activity-note">
                    Foglio presenza STEP 4 struttura Libri.
                    <div class="activity-legend">
                        <span class="activity-pill pill-mondadori">MONDADORI</span>
                        <span class="activity-pill pill-giunti">GIUNTI</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            visible_cols = [
                "GIORNO_NUM",
                "DATA_VIEW",
                "GIORNO_SETTIMANA",
                "MONDADORI_ORE",
                "MONDADORI_€",
                "MONDADORI_TIPO_ASSENZA",
                "SEP_1",
                "GIUNTI_ORE",
                "GIUNTI_€",
                "GIUNTI_TIPO_ASSENZA",
                "FESTIVO",
            ]

            display_df = record["tabella"].copy().reset_index(drop=True)
            display_df.insert(6, "SEP_1", "│")

            edited = st.data_editor(
                display_df[visible_cols],
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                disabled=locked,
                column_config={
                    "GIORNO_NUM": st.column_config.NumberColumn("Giorno", disabled=True),
                    "DATA_VIEW": st.column_config.TextColumn("Data", disabled=True),
                    "GIORNO_SETTIMANA": st.column_config.TextColumn("Giorno settimana", disabled=True),
                    "MONDADORI_ORE": st.column_config.NumberColumn("Mondadori Ore", min_value=0.0, step=0.5, format="%.2f"),
                    "MONDADORI_€": st.column_config.NumberColumn("Mondadori €", format="%.2f €", disabled=True),
                    "MONDADORI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Mondadori Tipo assenza", options=TIPI_ASSENZA),
                    "SEP_1": st.column_config.TextColumn("│", disabled=True),
                    "GIUNTI_ORE": st.column_config.NumberColumn("Giunti Ore", min_value=0.0, step=0.5, format="%.2f"),
                    "GIUNTI_€": st.column_config.NumberColumn("Giunti €", format="%.2f €", disabled=True),
                    "GIUNTI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Giunti Tipo assenza", options=TIPI_ASSENZA),
                    "FESTIVO": st.column_config.CheckboxColumn("Festivo"),
                },
                key=f"editor_tabella_{selected_key}",
            )

            if not locked:
                edited_clean = edited.drop(columns=["SEP_1"]).copy().reset_index(drop=True)
                hidden_cols = record["tabella"][
                    [
                        "DATA",
                        "ROW_STATUS",
                        "BASE_EDICOLA_ORE",
                        "BASE_MONDADORI_ORE",
                        "BASE_GIUNTI_ORE",
                        "EDICOLA_ORE",
                        "EDICOLA_€",
                        "EDICOLA_TIPO_ASSENZA",
                        "STEP4_ALLOW_MANUAL",
                    ]
                ].copy().reset_index(drop=True)

                merged = pd.concat([edited_clean, hidden_cols], axis=1)
                merged = merged[
                    [
                        "GIORNO_NUM",
                        "DATA",
                        "GIORNO_SETTIMANA",
                        "DATA_VIEW",
                        "EDICOLA_ORE",
                        "EDICOLA_€",
                        "EDICOLA_TIPO_ASSENZA",
                        "MONDADORI_ORE",
                        "MONDADORI_€",
                        "MONDADORI_TIPO_ASSENZA",
                        "GIUNTI_ORE",
                        "GIUNTI_€",
                        "GIUNTI_TIPO_ASSENZA",
                        "FESTIVO",
                        "ROW_STATUS",
                        "BASE_EDICOLA_ORE",
                        "BASE_MONDADORI_ORE",
                        "BASE_GIUNTI_ORE",
                        "STEP4_ALLOW_MANUAL",
                    ]
                ]

                merged, warnings = apply_step3_rules(
                    tabella=merged,
                    netto_ora=record["netto_ora"],
                    societa=record["societa"],
                    origine_master=normalize_upper(record["origine_master"]),
                )

                old_visible = display_df[visible_cols].copy().reset_index(drop=True)
                new_display = merged.copy().reset_index(drop=True)
                new_display.insert(6, "SEP_1", "│")
                new_visible = new_display[visible_cols].copy().reset_index(drop=True)

                record["tabella"] = merged
                st.session_state["sheet_warnings"][selected_key] = warnings
                update_sheet_totals(record)

                if not new_visible.equals(old_visible):
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="inner-box">', unsafe_allow_html=True)
        st.markdown('<div class="table-title">Fondo foglio</div>', unsafe_allow_html=True)

        col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
        with col_b1:
            record["arretrati"] = st.number_input("€ arretrato", value=float(record["arretrati"]), step=0.50, disabled=locked, key=f"arretrati_{selected_key}")
        with col_b2:
            record["extra"] = st.number_input("€ extra", value=float(record["extra"]), step=0.50, disabled=locked, key=f"extra_{selected_key}")
        with col_b3:
            record["affiancamenti"] = st.number_input("€ affiancamento", value=float(record["affiancamenti"]), step=0.50, disabled=locked, key=f"affiancamenti_{selected_key}")
        with col_b4:
            record["domeniche"] = st.number_input("€ domeniche", value=float(record["domeniche"]), step=0.50, disabled=locked, key=f"domeniche_{selected_key}")
        with col_b5:
            record["rimborso"] = st.number_input("€ rimborso", value=float(record["rimborso"]), step=0.50, disabled=locked, key=f"rimborso_{selected_key}")

        uploaded_docs = st.file_uploader(
            "Allegati rimborso",
            accept_multiple_files=True,
            disabled=locked,
            key=f"rimborso_upload_{selected_key}",
        )
        if uploaded_docs is not None:
            record["rimborso_allegati"] = [file.name for file in uploaded_docs]

        if record["rimborso_allegati"]:
            st.caption("Allegati caricati: " + ", ".join(record["rimborso_allegati"]))

        record["note_generali"] = st.text_area(
            "NOTE GENERALI DEL MESE",
            value=record["note_generali"],
            height=130,
            disabled=locked,
            key=f"note_{selected_key}",
        )

        update_sheet_totals(record)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="inner-box">', unsafe_allow_html=True)
        st.markdown('<div class="table-title">Totale finale</div>', unsafe_allow_html=True)

        col_t1, col_t2 = st.columns([2, 1])
        with col_t1:
            st.markdown(
                """
                <div class="soft-note">
                    <b>Formula STEP 4</b><br>
                    TOT NETTO MESE = Tot attività + Arretrati + Extra + Affiancamenti + Domeniche + Rimborsi
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_t2:
            st.metric("TOT NETTO MESE", f"€ {record['tot_netto_mese']:.2f}")

        st.markdown("</div>", unsafe_allow_html=True)

        col_reset1, col_reset2 = st.columns([1, 1])
        with col_reset1:
            if st.button("Azzera foglio presenza", disabled=locked, use_container_width=True, key=f"azzera_{selected_key}"):
                clear_entire_sheet(record)
                st.session_state["sheet_warnings"][selected_key] = []
                st.rerun()
        with col_reset2:
            st.write("")

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ---- flusso standard STEP 3 invariato ----

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        st.text_input("Società", value=record["societa"], disabled=True)
        st.text_input("Attività", value=record["attivita_riga"], disabled=True)
        st.text_input("Nome", value=record["nome"], disabled=True)
    with col_h2:
        st.text_input("CF", value=record["cf"], disabled=True)
        st.text_input("PDV", value=record["pdv"], disabled=True)
        st.text_input("Mese", value=f"{MESI[record['mese']]} {record['anno']}", disabled=True)
    with col_h3:
        record["tipo_contratto"] = st.text_input("Tipo contratto", value=record["tipo_contratto"], disabled=locked)
        record["scadenza_contratto"] = st.text_input("Scadenza contratto", value=record["scadenza_contratto"], disabled=locked)
        record["netto_mese"] = st.number_input("NETTO MESE", value=float(record["netto_mese"]), step=0.50, disabled=locked)
    with col_h4:
        record["netto_ora"] = st.number_input("Netto orario", value=float(record["netto_ora"]), step=0.10, disabled=locked)
        st.number_input("Giorni lavorati", value=int(record["giorni_lavorati"]), disabled=True)
        st.number_input("Giorni modificati", value=int(record["giorni_modificati"]), disabled=True)

    col_h5, col_h6, col_h7 = st.columns(3)
    with col_h5:
        st.number_input("Tot ore lavorative mese", value=float(record["tot_ore_lavorative_mese"]), disabled=True)
    with col_h6:
        st.number_input("Tot ore azzerate", value=float(record["tot_ore_azzerate"]), disabled=True)
    with col_h7:
        st.number_input("Tot € da scalare", value=float(record["tot_euro_da_scalare"]), disabled=True)

    col_lock1, col_lock2 = st.columns(2)
    with col_lock1:
        record["lucchetto_foglio"] = st.checkbox(
            "Lucchetto foglio",
            value=record["lucchetto_foglio"],
            disabled=record["lucchetto_mese"],
        )
    with col_lock2:
        record["lucchetto_mese"] = st.checkbox("Lucchetto mese", value=record["lucchetto_mese"])

    st.markdown("</div>", unsafe_allow_html=True)

    locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

    if selected_key in st.session_state["sheet_warnings"] and st.session_state["sheet_warnings"][selected_key]:
        for msg in st.session_state["sheet_warnings"][selected_key]:
            render_warning_box(msg)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Corpo foglio presenze</div>', unsafe_allow_html=True)

    if normalize_upper(record["origine_master"]) == ORIGINE_EDICOLA:
        st.markdown(
            """
            <div class="activity-note">
                Foglio presenza generato da riga Master Edicola.
                <div class="activity-legend">
                    <span class="activity-pill pill-edicola">EDICOLA</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        visible_cols = [
            "GIORNO_NUM",
            "DATA_VIEW",
            "GIORNO_SETTIMANA",
            "EDICOLA_ORE",
            "EDICOLA_€",
            "EDICOLA_TIPO_ASSENZA",
            "FESTIVO",
        ]

        display_df = record["tabella"][COLONNE_TABELLA_TECNICHE].copy().reset_index(drop=True)

        edited = st.data_editor(
            display_df[visible_cols],
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=locked,
            column_config={
                "GIORNO_NUM": st.column_config.NumberColumn("Giorno", disabled=True),
                "DATA_VIEW": st.column_config.TextColumn("Data", disabled=True),
                "GIORNO_SETTIMANA": st.column_config.TextColumn("Giorno settimana", disabled=True),
                "EDICOLA_ORE": st.column_config.NumberColumn("Edicola Ore", min_value=0.0, step=0.5, format="%.2f"),
                "EDICOLA_€": st.column_config.NumberColumn("Edicola €", format="%.2f €", disabled=True),
                "EDICOLA_TIPO_ASSENZA": st.column_config.SelectboxColumn("Edicola Tipo assenza", options=TIPI_ASSENZA),
                "FESTIVO": st.column_config.CheckboxColumn("Festivo"),
            },
            key=f"editor_tabella_{selected_key}",
        )

        if not locked:
            hidden_cols = record["tabella"][
                ["DATA", "ROW_STATUS"] + COLONNE_BASE_ALL + ["MONDADORI_ORE", "MONDADORI_€", "MONDADORI_TIPO_ASSENZA", "GIUNTI_ORE", "GIUNTI_€", "GIUNTI_TIPO_ASSENZA"]
            ].copy().reset_index(drop=True)

            edited_clean = edited.copy().reset_index(drop=True)
            merged = pd.concat([edited_clean, hidden_cols], axis=1)

            merged = merged[
                [
                    "GIORNO_NUM",
                    "DATA",
                    "GIORNO_SETTIMANA",
                    "DATA_VIEW",
                    "EDICOLA_ORE",
                    "EDICOLA_€",
                    "EDICOLA_TIPO_ASSENZA",
                    "MONDADORI_ORE",
                    "MONDADORI_€",
                    "MONDADORI_TIPO_ASSENZA",
                    "GIUNTI_ORE",
                    "GIUNTI_€",
                    "GIUNTI_TIPO_ASSENZA",
                    "FESTIVO",
                    "ROW_STATUS",
                    "BASE_EDICOLA_ORE",
                    "BASE_MONDADORI_ORE",
                    "BASE_GIUNTI_ORE",
                ]
            ]

            merged, warnings = apply_step3_rules(
                tabella=merged,
                netto_ora=record["netto_ora"],
                societa=record["societa"],
                origine_master=normalize_upper(record["origine_master"]),
            )

            old_visible = record["tabella"][visible_cols].copy().reset_index(drop=True)
            new_visible = merged[visible_cols].copy().reset_index(drop=True)

            record["tabella"] = merged
            st.session_state["sheet_warnings"][selected_key] = warnings
            update_sheet_totals(record)

            if not new_visible.equals(old_visible):
                st.rerun()

    else:
        st.markdown(
            """
            <div class="activity-note">
                Foglio presenza generato da riga Master Libri.
                <div class="activity-legend">
                    <span class="activity-pill pill-mondadori">MONDADORI</span>
                    <span class="activity-pill pill-giunti">GIUNTI</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        visible_cols = [
            "GIORNO_NUM",
            "DATA_VIEW",
            "GIORNO_SETTIMANA",
            "MONDADORI_ORE",
            "MONDADORI_€",
            "MONDADORI_TIPO_ASSENZA",
            "SEP_1",
            "GIUNTI_ORE",
            "GIUNTI_€",
            "GIUNTI_TIPO_ASSENZA",
            "FESTIVO",
        ]

        display_df = record["tabella"][COLONNE_TABELLA_TECNICHE].copy().reset_index(drop=True)
        display_df.insert(6, "SEP_1", "│")

        edited = st.data_editor(
            display_df[visible_cols],
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=locked,
            column_config={
                "GIORNO_NUM": st.column_config.NumberColumn("Giorno", disabled=True),
                "DATA_VIEW": st.column_config.TextColumn("Data", disabled=True),
                "GIORNO_SETTIMANA": st.column_config.TextColumn("Giorno settimana", disabled=True),
                "MONDADORI_ORE": st.column_config.NumberColumn("Mondadori Ore", min_value=0.0, step=0.5, format="%.2f"),
                "MONDADORI_€": st.column_config.NumberColumn("Mondadori €", format="%.2f €", disabled=True),
                "MONDADORI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Mondadori Tipo assenza", options=TIPI_ASSENZA),
                "SEP_1": st.column_config.TextColumn("│", disabled=True),
                "GIUNTI_ORE": st.column_config.NumberColumn("Giunti Ore", min_value=0.0, step=0.5, format="%.2f"),
                "GIUNTI_€": st.column_config.NumberColumn("Giunti €", format="%.2f €", disabled=True),
                "GIUNTI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Giunti Tipo assenza", options=TIPI_ASSENZA),
                "FESTIVO": st.column_config.CheckboxColumn("Festivo"),
            },
            key=f"editor_tabella_{selected_key}",
        )

        if not locked:
            edited_clean = edited.drop(columns=["SEP_1"]).copy().reset_index(drop=True)
            hidden_cols = record["tabella"][
                ["DATA", "ROW_STATUS"] + COLONNE_BASE_ALL + ["EDICOLA_ORE", "EDICOLA_€", "EDICOLA_TIPO_ASSENZA"]
            ].copy().reset_index(drop=True)

            merged = pd.concat([edited_clean, hidden_cols], axis=1)
            merged = merged[
                [
                    "GIORNO_NUM",
                    "DATA",
                    "GIORNO_SETTIMANA",
                    "DATA_VIEW",
                    "EDICOLA_ORE",
                    "EDICOLA_€",
                    "EDICOLA_TIPO_ASSENZA",
                    "MONDADORI_ORE",
                    "MONDADORI_€",
                    "MONDADORI_TIPO_ASSENZA",
                    "GIUNTI_ORE",
                    "GIUNTI_€",
                    "GIUNTI_TIPO_ASSENZA",
                    "FESTIVO",
                    "ROW_STATUS",
                    "BASE_EDICOLA_ORE",
                    "BASE_MONDADORI_ORE",
                    "BASE_GIUNTI_ORE",
                ]
            ]

            merged, warnings = apply_step3_rules(
                tabella=merged,
                netto_ora=record["netto_ora"],
                societa=record["societa"],
                origine_master=normalize_upper(record["origine_master"]),
            )

            old_visible = display_df[visible_cols].copy().reset_index(drop=True)
            new_display = merged.copy().reset_index(drop=True)
            new_display.insert(6, "SEP_1", "│")
            new_visible = new_display[visible_cols].copy().reset_index(drop=True)

            record["tabella"] = merged
            st.session_state["sheet_warnings"][selected_key] = warnings
            update_sheet_totals(record)

            if not new_visible.equals(old_visible):
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Fondo foglio</div>', unsafe_allow_html=True)

    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
    with col_b1:
        record["arretrati"] = st.number_input("€ arretrato", value=float(record["arretrati"]), step=0.50, disabled=locked)
    with col_b2:
        record["extra"] = st.number_input("€ extra", value=float(record["extra"]), step=0.50, disabled=locked)
    with col_b3:
        record["affiancamenti"] = st.number_input("€ affiancamento", value=float(record["affiancamenti"]), step=0.50, disabled=locked)
    with col_b4:
        record["domeniche"] = st.number_input("€ domeniche", value=float(record["domeniche"]), step=0.50, disabled=locked)
    with col_b5:
        record["rimborso"] = st.number_input("€ rimborso", value=float(record["rimborso"]), step=0.50, disabled=locked)

    uploaded_docs = st.file_uploader(
        "Allegati rimborso",
        accept_multiple_files=True,
        disabled=locked,
        key=f"rimborso_upload_{selected_key}",
    )
    if uploaded_docs is not None:
        record["rimborso_allegati"] = [file.name for file in uploaded_docs]

    if record["rimborso_allegati"]:
        st.caption("Allegati caricati: " + ", ".join(record["rimborso_allegati"]))

    record["note_generali"] = st.text_area(
        "NOTE GENERALI DEL MESE",
        value=record["note_generali"],
        height=130,
        disabled=locked,
    )

    update_sheet_totals(record)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Totale finale</div>', unsafe_allow_html=True)

    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.markdown(
            """
            <div class="soft-note">
                <b>Formula STEP 3</b><br>
                TOT NETTO MESE = Tot attività + Arretrati + Extra + Affiancamenti + Domeniche + Rimborsi
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_t2:
        st.metric("TOT NETTO MESE", f"€ {record['tot_netto_mese']:.2f}")

    st.markdown("</div>", unsafe_allow_html=True)

    col_reset1, col_reset2 = st.columns([1, 1])
    with col_reset1:
        if st.button("Azzera foglio presenza", disabled=locked, use_container_width=True):
            clear_entire_sheet(record)
            st.session_state["sheet_warnings"][selected_key] = []
            st.rerun()
    with col_reset2:
        st.write("")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# APP
# =========================

ensure_session_state()
inject_global_css()
render_header()

with st.sidebar:
    st.markdown('<div class="sidebar-logo-wrap">', unsafe_allow_html=True)
    st.image(LOGO_URL, width=170)
    st.markdown("</div>", unsafe_allow_html=True)

    sezione = st.radio(
        "Sezioni operative",
        [
            "Caricamento master",
            "Generazione fogli",
            "Gestione foglio",
        ],
    )

if sezione == "Caricamento master":
    render_master_page()
elif sezione == "Generazione fogli":
    render_generation_page()
else:
    render_sheet_page()
