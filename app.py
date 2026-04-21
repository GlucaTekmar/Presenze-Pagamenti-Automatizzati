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


def calculate_sheet_stats(df: pd.DataFrame, origine_master: str, netto_ora: float = 0.0, societa: str = "") -> dict:
    if origine_master == ORIGINE_EDICOLA:
        current_hours = df["EDICOLA_ORE"].apply(safe_float)
        base_hours = df["BASE_EDICOLA_ORE"].apply(safe_float)

        current_euro_series = df["EDICOLA_€"].apply(safe_float)
        base_euro_series = df.apply(
            lambda row: calculate_row_amount(
                safe_float(row["BASE_EDICOLA_ORE"]),
                netto_ora,
                bool(row["FESTIVO"]),
                societa,
            ),
            axis=1,
        )
    else:
        current_hours = df["MONDADORI_ORE"].apply(safe_float) + df["GIUNTI_ORE"].apply(safe_float)
        base_hours = df["BASE_MONDADORI_ORE"].apply(safe_float) + df["BASE_GIUNTI_ORE"].apply(safe_float)

        current_euro_series = df["MONDADORI_€"].apply(safe_float) + df["GIUNTI_€"].apply(safe_float)
        base_euro_series = df.apply(
            lambda row: (
                calculate_row_amount(
                    safe_float(row["BASE_MONDADORI_ORE"]),
                    netto_ora,
                    bool(row["FESTIVO"]),
                    societa,
                )
                + calculate_row_amount(
                    safe_float(row["BASE_GIUNTI_ORE"]),
                    netto_ora,
                    bool(row["FESTIVO"]),
                    societa,
                )
            ),
            axis=1,
        )

    giorni_lavorati = int((current_hours > 0).sum())
    giorni_modificati = int((df["ROW_STATUS"].astype(str).str.strip() != "").sum())
    tot_ore = round(current_hours.sum(), 2)
    tot_ore_azzerate = round((base_hours - current_hours).clip(lower=0).sum(), 2)
    tot_euro = round(current_euro_series.sum(), 2)
    riduzioni_euro = round((base_euro_series - current_euro_series).clip(lower=0).sum(), 2)

    return {
        "GIORNI_LAVORATI": giorni_lavorati,
        "GIORNI_MODIFICATI": giorni_modificati,
        "TOT_ORE_LAVORATIVE_MESE": tot_ore,
        "TOT_ORE_AZZERATE": tot_ore_azzerate,
        "TOT_€_DA_SCALARE": riduzioni_euro,
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
    stats = calculate_sheet_stats(
        tabella,
        normalize_upper(row["ORIGINE_MASTER"]),
        netto_ora=safe_float(row["NETTO_ORA"]),
        societa=normalize_text(row["SOCIETA"]),
    )

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
    stats = calculate_sheet_stats(
        record["tabella"],
        normalize_upper(record["origine_master"]),
        netto_ora=record["netto_ora"],
        societa=record["societa"],
    )
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
        st.rerun()

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

    filtro_nome = st.text_input("Filtro semplice nome/cognome", placeholder="Scrivi nome o cognome", key="step3_filtro_nome")

    full_table = st.session_state["generation_table"].copy()
    if full_table.empty:
        st.warning("Nessuna riga disponibile per la generazione dei fogli.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    generation_table = full_table.copy()

    def is_generated(row_id: str) -> bool:
        key = format_sheet_key(normalize_text(row_id), anno, mese)
        return key in st.session_state["fogli_generati"]

    generation_table["GENERATO"] = generation_table["ROW_ID"].apply(lambda rid: "🟢" if is_generated(rid) else "")

    if filtro_nome.strip():
        mask = generation_table["NOME"].astype(str).str.upper().str.contains(filtro_nome.strip().upper(), na=False)
        generation_table = generation_table[mask].copy()

    if generation_table.empty:
        st.info("Nessun risultato trovato con il filtro inserito.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="soft-note">
            <b>Selezione multipla assistita</b><br>
            Scegli una riga di partenza e usa il tasto dedicato per selezionare fino a 50 righe consecutive.<br>
            Il pallino verde indica i fogli già generati per mese/anno selezionati.
        </div>
        """,
        unsafe_allow_html=True,
    )

    generation_table = generation_table.reset_index(drop=True)

    start_row_idx = st.selectbox(
        "Riga di partenza per selezione multipla (max 50 righe)",
        options=list(generation_table.index),
        format_func=lambda i: (
            f"{generation_table.loc[i, 'NOME']} | "
            f"{generation_table.loc[i, 'SOCIETA']} | "
            f"{generation_table.loc[i, 'PDV']} | "
            f"{generation_table.loc[i, 'ATTIVITA_RIGA']}"
        ),
        key="step3_start_row_idx",
    )

    col_sel1, col_sel2 = st.columns(2)

    with col_sel1:
        if st.button("Seleziona 50 righe da qui in giù", use_container_width=True, key="step3_select_50"):
            row_ids_to_select = generation_table.loc[start_row_idx:, "ROW_ID"].tolist()[:50]
            base_table = st.session_state["generation_table"].copy()
            base_table.loc[base_table["ROW_ID"].isin(row_ids_to_select), "SELEZIONA"] = True
            st.session_state["generation_table"] = base_table
            st.rerun()

    with col_sel2:
        if st.button("Deseleziona tutte le righe visibili", use_container_width=True, key="step3_deselect_visible"):
            visible_row_ids = generation_table["ROW_ID"].tolist()
            base_table = st.session_state["generation_table"].copy()
            base_table.loc[base_table["ROW_ID"].isin(visible_row_ids), "SELEZIONA"] = False
            st.session_state["generation_table"] = base_table
            st.rerun()

    editor_table = st.session_state["generation_table"].copy()
    if filtro_nome.strip():
        mask_editor = editor_table["NOME"].astype(str).str.upper().str.contains(filtro_nome.strip().upper(), na=False)
        editor_table = editor_table[mask_editor].copy()

    editor_table["GENERATO"] = editor_table["ROW_ID"].apply(lambda rid: "🟢" if is_generated(rid) else "")

    edited = st.data_editor(
        editor_table.reset_index(drop=True),
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "SELEZIONA": st.column_config.CheckboxColumn("Seleziona"),
            "GENERATO": st.column_config.TextColumn("Creato", disabled=True),
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

    updated_base_table = st.session_state["generation_table"].copy()
    for _, row in edited[["ROW_ID", "SELEZIONA"]].iterrows():
        updated_base_table.loc[updated_base_table["ROW_ID"] == row["ROW_ID"], "SELEZIONA"] = bool(row["SELEZIONA"])
    st.session_state["generation_table"] = updated_base_table

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Genera fogli presenze selezionati", type="primary", use_container_width=True, key="step3_genera_fogli"):
        selected = st.session_state["generation_table"][st.session_state["generation_table"]["SELEZIONA"] == True].copy()

        if selected.empty:
            st.warning("Seleziona almeno una riga.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        if len(selected) > 50:
            st.error("Puoi generare al massimo 50 fogli presenza per volta.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        last_key = None
        for _, row in selected.iterrows():
            key = format_sheet_key(normalize_text(row["ROW_ID"]), anno, mese)
            st.session_state["fogli_generati"][key] = init_sheet_record(
                row=row,
                df_edicola=st.session_state["df_edicola"],
                df_libri=st.session_state["df_libri"],
                anno=anno,
                mese=mese,
            )
            st.session_state["sheet_warnings"][key] = []
            last_key = key

        if last_key:
            st.session_state["foglio_attivo"] = last_key

        updated_base_table = st.session_state["generation_table"].copy()
        updated_base_table.loc[updated_base_table["ROW_ID"].isin(selected["ROW_ID"].tolist()), "SELEZIONA"] = False
        st.session_state["generation_table"] = updated_base_table

        st.success("Fogli presenze generati correttamente.")
        st.rerun()

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
        key="step3_select_foglio_attivo",
    )
    st.session_state["foglio_attivo"] = selected_key
    record = st.session_state["fogli_generati"][selected_key]

    locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        st.text_input("Società", value=record["societa"], disabled=True, key=f"step3_societa_{selected_key}")
        st.text_input("Attività", value=record["attivita_riga"], disabled=True, key=f"step3_attivita_{selected_key}")
        st.text_input("Nome", value=record["nome"], disabled=True, key=f"step3_nome_{selected_key}")
    with col_h2:
        st.text_input("CF", value=record["cf"], disabled=True, key=f"step3_cf_{selected_key}")
        st.text_input("PDV", value=record["pdv"], disabled=True, key=f"step3_pdv_{selected_key}")
        st.text_input("Mese", value=f"{MESI[record['mese']]} {record['anno']}", disabled=True, key=f"step3_mese_{selected_key}")
    with col_h3:
        record["tipo_contratto"] = st.text_input("Tipo contratto", value=record["tipo_contratto"], disabled=locked, key=f"step3_tipo_contratto_{selected_key}")
        record["scadenza_contratto"] = st.text_input("Scadenza contratto", value=record["scadenza_contratto"], disabled=locked, key=f"step3_scadenza_{selected_key}")
        record["netto_mese"] = st.number_input("NETTO MESE", value=float(record["netto_mese"]), step=0.50, disabled=locked, key=f"step3_netto_mese_{selected_key}")
    with col_h4:
        record["netto_ora"] = st.number_input("Netto orario", value=float(record["netto_ora"]), step=0.10, disabled=locked, key=f"step3_netto_ora_{selected_key}")
        st.number_input("Giorni lavorati", value=int(record["giorni_lavorati"]), disabled=True, key=f"step3_giorni_lavorati_{selected_key}")
        st.number_input("Giorni modificati", value=int(record["giorni_modificati"]), disabled=True, key=f"step3_giorni_modificati_{selected_key}")

    col_h5, col_h6, col_h7 = st.columns(3)
    with col_h5:
        st.number_input("Tot ore lavorative mese", value=float(record["tot_ore_lavorative_mese"]), disabled=True, key=f"step3_tot_ore_{selected_key}")
    with col_h6:
        st.number_input("Tot ore azzerate", value=float(record["tot_ore_azzerate"]), disabled=True, key=f"step3_tot_ore_azz_{selected_key}")
    with col_h7:
        st.number_input("Tot € da scalare", value=float(record["tot_euro_da_scalare"]), disabled=True, key=f"step3_tot_scalare_{selected_key}")

    col_lock1, col_lock2 = st.columns(2)
    with col_lock1:
        record["lucchetto_foglio"] = st.checkbox(
            "Lucchetto foglio",
            value=record["lucchetto_foglio"],
            disabled=record["lucchetto_mese"],
            key=f"step3_lock_foglio_{selected_key}",
        )
    with col_lock2:
        record["lucchetto_mese"] = st.checkbox("Lucchetto mese", value=record["lucchetto_mese"], key=f"step3_lock_mese_{selected_key}")

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
            height=1140,
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
            height=1140,
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

            old_display = display_df[visible_cols].copy().reset_index(drop=True)
            new_display = merged.copy().reset_index(drop=True)
            new_display.insert(6, "SEP_1", "│")
            new_visible = new_display[visible_cols].copy().reset_index(drop=True)

            record["tabella"] = merged
            st.session_state["sheet_warnings"][selected_key] = warnings
            update_sheet_totals(record)

            if not new_visible.equals(old_display):
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Fondo foglio</div>', unsafe_allow_html=True)

    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
    with col_b1:
        record["arretrati"] = st.number_input("€ arretrato", value=float(record["arretrati"]), step=0.50, disabled=locked, key=f"step3_arretrati_{selected_key}")
    with col_b2:
        record["extra"] = st.number_input("€ extra", value=float(record["extra"]), step=0.50, disabled=locked, key=f"step3_extra_{selected_key}")
    with col_b3:
        record["affiancamenti"] = st.number_input("€ affiancamento", value=float(record["affiancamenti"]), step=0.50, disabled=locked, key=f"step3_affiancamenti_{selected_key}")
    with col_b4:
        record["domeniche"] = st.number_input("€ domeniche", value=float(record["domeniche"]), step=0.50, disabled=locked, key=f"step3_domeniche_{selected_key}")
    with col_b5:
        record["rimborso"] = st.number_input("€ rimborso", value=float(record["rimborso"]), step=0.50, disabled=locked, key=f"step3_rimborso_{selected_key}")

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
        key=f"step3_note_generali_{selected_key}",
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
        if st.button("Azzera foglio presenza", disabled=locked, use_container_width=True, key=f"step3_azzera_{selected_key}"):
            clear_entire_sheet(record)
            st.session_state["sheet_warnings"][selected_key] = []
            st.rerun()
    with col_reset2:
        st.write("")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# STEP 4 - NUOVO FOGLIO PRESENZA / SOSTITUZIONE
# RISCRITTO
# DA INCOLLARE SUBITO PRIMA DEL BLOCCO APP
# =========================

inject_global_css_step3 = inject_global_css
render_sheet_page_step3 = render_sheet_page


def inject_global_css():
    inject_global_css_step3()
    st.markdown(
        f"""
        <style>
            .step4-master-box {{
                background: #F3F5F7;
                border: 3px solid {BORDER_COLOR_STRONG};
                border-radius: 16px;
                padding: 16px;
                margin-bottom: 18px;
            }}

            .step4-action-box {{
                background: #FFF4F4;
                border: 3px solid {COLOR_ROSSO};
                border-radius: 16px;
                padding: 16px;
                margin-top: 18px;
                margin-bottom: 18px;
            }}

            .step4-action-title {{
                font-size: 1.45rem;
                font-weight: 900;
                color: {COLOR_ROSSO};
                margin: 0 0 0.35rem 0;
            }}

            .step4-action-subtitle {{
                font-size: 1rem;
                font-weight: 700;
                color: {TEXT_COLOR};
                margin: 0 0 0.8rem 0;
            }}

            .step4-legend-box {{
                background: #FFFFFF;
                border: 2px solid {BORDER_COLOR_STRONG};
                border-radius: 12px;
                padding: 10px 12px;
                margin-bottom: 12px;
            }}

            .step4-help {{
                font-size: 0.98rem;
                color: {TEXT_MUTED};
                margin-bottom: 8px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def step4_ensure_session_state():
    defaults = {
        "step4_last_created_key": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def step4_is_single_date_in_month(value, anno: int, mese: int) -> bool:
    if value is None:
        return False
    return value.year == anno and value.month == mese


def step4_get_selected_days(anno: int, mese: int, modo: str, giorno_singolo_value, periodo_value) -> list[int]:
    if modo == "Giorno singolo":
        if not step4_is_single_date_in_month(giorno_singolo_value, anno, mese):
            return []
        return [int(giorno_singolo_value.day)]

    if not periodo_value or len(periodo_value) != 2:
        return []

    data_inizio, data_fine = periodo_value
    if not data_inizio or not data_fine:
        return []

    if data_inizio > data_fine:
        return []

    primo_giorno = date(anno, mese, 1)
    ultimo_giorno = date(anno, mese, calendar.monthrange(anno, mese)[1])

    if data_inizio < primo_giorno or data_fine > ultimo_giorno:
        return []

    giorni = []
    current = data_inizio
    while current <= data_fine:
        giorni.append(current.day)
        current = date.fromordinal(current.toordinal() + 1)

    return giorni


def step4_days_text(selected_days: list[int]) -> str:
    if not selected_days:
        return ""
    if len(selected_days) == 1:
        return f"Giorno {selected_days[0]}"
    return f"Giorni da {min(selected_days)} a {max(selected_days)}"


def step4_build_empty_presence_dataframe(attivita: str, anno: int, mese: int, selected_days: list[int]) -> pd.DataFrame:
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
                "STEP4_RECORD": True,
                "STEP4_SELECTED_DAY": giorno_num in selected_days,
            }
        )

    return pd.DataFrame(righe)


def step4_get_societa_options() -> list[str]:
    societa = set()

    if not st.session_state["df_edicola"].empty:
        societa.update(st.session_state["df_edicola"]["AGENZIA"].dropna().astype(str).str.strip().tolist())

    if not st.session_state["df_libri"].empty:
        societa.update(st.session_state["df_libri"]["AGENZIA"].dropna().astype(str).str.strip().tolist())

    return sorted([x for x in societa if normalize_text(x) != ""])


def step4_build_dipendenti_table(societa: str, attivita: str, modalita: str) -> pd.DataFrame:
    righe = []
    societa_up = normalize_upper(societa)
    attivita_up = normalize_upper(attivita)
    modalita_up = normalize_upper(modalita)

    if modalita_up == "SOSTITUZIONE CON SOSTITUTO SPOT":
        df = st.session_state["df_spot"].copy()
        for idx, row in df.reset_index(drop=True).iterrows():
            righe.append(
                {
                    "SELEZIONA": False,
                    "SOURCE_ID": f"SPOT_{idx}",
                    "NOMINATIVO": normalize_text(row["MHS_SOSTITUTO_SPOT"]),
                    "CODICE_FISCALE": normalize_text(row["COD_FISCALE"]),
                    "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                    "SCADENZA_CONTRATTO": normalize_text(row["SCADENZA_CONTRATTO"]),
                    "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                    "TEL": normalize_text(row["TEL"]),
                    "MAIL": normalize_text(row["MAIL"]),
                }
            )
    else:
        if attivita_up == ORIGINE_EDICOLA:
            df = st.session_state["df_edicola"].copy()
            df = df[df["AGENZIA"].astype(str).str.strip().str.upper() == societa_up].copy()

            for idx, row in df.reset_index(drop=True).iterrows():
                righe.append(
                    {
                        "SELEZIONA": False,
                        "SOURCE_ID": f"EDICOLA_DIP_{idx}",
                        "NOMINATIVO": normalize_text(row["MHS_TITOLARE"]),
                        "CODICE_FISCALE": normalize_text(row["COD_FISCALE"]),
                        "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                        "SCADENZA_CONTRATTO": normalize_text(row["SCADENZA_CONTRATTO"]),
                        "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                        "TEL": normalize_text(row["TEL_MHS"]),
                        "MAIL": normalize_text(row["MAIL_MHS"]),
                    }
                )
        else:
            df = st.session_state["df_libri"].copy()
            df = df[df["AGENZIA"].astype(str).str.strip().str.upper() == societa_up].copy()

            for idx, row in df.reset_index(drop=True).iterrows():
                righe.append(
                    {
                        "SELEZIONA": False,
                        "SOURCE_ID": f"LIBRI_DIP_{idx}",
                        "NOMINATIVO": normalize_text(row["MHS_TITOLARE"]),
                        "CODICE_FISCALE": normalize_text(row["COD_FISCALE"]),
                        "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                        "SCADENZA_CONTRATTO": normalize_text(row["SCADENZA_CONTRATTO"]),
                        "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                        "TEL": normalize_text(row["TEL_MHS"]),
                        "MAIL": normalize_text(row["MAIL_MHS"]),
                    }
                )

    return pd.DataFrame(righe)


def step4_build_pdv_table(societa: str, attivita: str) -> pd.DataFrame:
    righe = []
    societa_up = normalize_upper(societa)
    attivita_up = normalize_upper(attivita)

    if attivita_up == ORIGINE_EDICOLA:
        df = st.session_state["df_edicola"].copy()
        df = df[df["AGENZIA"].astype(str).str.strip().str.upper() == societa_up].copy()

        for idx, row in df.reset_index(drop=True).iterrows():
            righe.append(
                {
                    "SELEZIONA": False,
                    "SOURCE_ID": f"EDICOLA_PDV_{idx}",
                    "PUNTO_VENDITA": normalize_text(row["PDV"]),
                    "TIPO_ATTIVITA": "EDICOLA",
                    "LUNEDI": safe_float(row["LUN"]),
                    "MARTEDI": safe_float(row["MAR"]),
                    "MERCOLEDI": safe_float(row["MER"]),
                    "GIOVEDI": safe_float(row["GIO"]),
                    "VENERDI": safe_float(row["VEN"]),
                    "SABATO": safe_float(row["SAB"]),
                    "DOMENICA": safe_float(row["DOM"]),
                    "MON_LUN": 0.0,
                    "MON_MAR": 0.0,
                    "MON_MER": 0.0,
                    "MON_GIO": 0.0,
                    "MON_VEN": 0.0,
                    "MON_SAB": 0.0,
                    "MON_DOM": 0.0,
                    "GIU_LUN": 0.0,
                    "GIU_MAR": 0.0,
                    "GIU_MER": 0.0,
                    "GIU_GIO": 0.0,
                    "GIU_VEN": 0.0,
                    "GIU_SAB": 0.0,
                    "GIU_DOM": 0.0,
                }
            )
    else:
        df = st.session_state["df_libri"].copy()
        df = df[df["AGENZIA"].astype(str).str.strip().str.upper() == societa_up].copy()

        grouped = {}
        for _, row in df.iterrows():
            pdv = normalize_text(row["PDV"])
            if pdv not in grouped:
                grouped[pdv] = {
                    "PUNTO_VENDITA": pdv,
                    "TIPO_ATTIVITA": "LIBRI",
                    "LUNEDI": 0.0,
                    "MARTEDI": 0.0,
                    "MERCOLEDI": 0.0,
                    "GIOVEDI": 0.0,
                    "VENERDI": 0.0,
                    "SABATO": 0.0,
                    "DOMENICA": 0.0,
                    "MON_LUN": 0.0,
                    "MON_MAR": 0.0,
                    "MON_MER": 0.0,
                    "MON_GIO": 0.0,
                    "MON_VEN": 0.0,
                    "MON_SAB": 0.0,
                    "MON_DOM": 0.0,
                    "GIU_LUN": 0.0,
                    "GIU_MAR": 0.0,
                    "GIU_MER": 0.0,
                    "GIU_GIO": 0.0,
                    "GIU_VEN": 0.0,
                    "GIU_SAB": 0.0,
                    "GIU_DOM": 0.0,
                }

            tipo_libri = normalize_upper(row["TIPO_LIBRI"])
            lun = safe_float(row["LUN"])
            mar = safe_float(row["MAR"])
            mer = safe_float(row["MER"])
            gio = safe_float(row["GIO"])
            ven = safe_float(row["VEN"])
            sab = safe_float(row["SAB"])
            dom = safe_float(row["DOM"])

            grouped[pdv]["LUNEDI"] += lun
            grouped[pdv]["MARTEDI"] += mar
            grouped[pdv]["MERCOLEDI"] += mer
            grouped[pdv]["GIOVEDI"] += gio
            grouped[pdv]["VENERDI"] += ven
            grouped[pdv]["SABATO"] += sab
            grouped[pdv]["DOMENICA"] += dom

            if tipo_libri == "MONDADORI":
                grouped[pdv]["MON_LUN"] += lun
                grouped[pdv]["MON_MAR"] += mar
                grouped[pdv]["MON_MER"] += mer
                grouped[pdv]["MON_GIO"] += gio
                grouped[pdv]["MON_VEN"] += ven
                grouped[pdv]["MON_SAB"] += sab
                grouped[pdv]["MON_DOM"] += dom
            elif tipo_libri == "GIUNTI":
                grouped[pdv]["GIU_LUN"] += lun
                grouped[pdv]["GIU_MAR"] += mar
                grouped[pdv]["GIU_MER"] += mer
                grouped[pdv]["GIU_GIO"] += gio
                grouped[pdv]["GIU_VEN"] += ven
                grouped[pdv]["GIU_SAB"] += sab
                grouped[pdv]["GIU_DOM"] += dom

        for idx, pdv_data in enumerate(grouped.values()):
            pdv_data["SELEZIONA"] = False
            pdv_data["SOURCE_ID"] = f"LIBRI_PDV_{idx}"
            righe.append(pdv_data)

    return pd.DataFrame(righe)


def step4_get_single_selected_row(df: pd.DataFrame):
    if df.empty:
        return None, 0

    selected = df[df["SELEZIONA"] == True].copy()
    count = len(selected)
    if count == 1:
        return selected.iloc[0].to_dict(), 1
    return None, count


def step4_apply_selected_rows_to_record(record: dict, dip_row: dict | None, pdv_row: dict | None):
    selected_days = record.get("step4_selected_days", [])
    attivita_up = normalize_upper(record["attivita_riga"])

    if dip_row:
        record["nome"] = normalize_text(dip_row.get("NOMINATIVO", ""))
        record["cf"] = normalize_text(dip_row.get("CODICE_FISCALE", ""))
        record["tipo_contratto"] = normalize_text(dip_row.get("TIPO_CONTRATTO", ""))
        record["scadenza_contratto"] = normalize_text(dip_row.get("SCADENZA_CONTRATTO", ""))
        record["netto_ora"] = round(safe_float(dip_row.get("NETTO_ORA", 0.0)), 2)
        record["telefono"] = normalize_text(dip_row.get("TEL", ""))
        record["email"] = normalize_text(dip_row.get("MAIL", ""))

    if pdv_row:
        record["pdv"] = normalize_text(pdv_row.get("PUNTO_VENDITA", ""))
        df = record["tabella"].copy()

        for idx in df.index:
            giorno_num = int(df.at[idx, "GIORNO_NUM"])
            if giorno_num not in selected_days:
                continue

            giorno_settimana = normalize_upper(df.at[idx, "GIORNO_SETTIMANA"])

            if attivita_up == ORIGINE_EDICOLA:
                ore_value = 0.0
                if giorno_settimana == "LUN":
                    ore_value = safe_float(pdv_row.get("LUNEDI", 0.0))
                elif giorno_settimana == "MAR":
                    ore_value = safe_float(pdv_row.get("MARTEDI", 0.0))
                elif giorno_settimana == "MER":
                    ore_value = safe_float(pdv_row.get("MERCOLEDI", 0.0))
                elif giorno_settimana == "GIO":
                    ore_value = safe_float(pdv_row.get("GIOVEDI", 0.0))
                elif giorno_settimana == "VEN":
                    ore_value = safe_float(pdv_row.get("VENERDI", 0.0))
                elif giorno_settimana == "SAB":
                    ore_value = safe_float(pdv_row.get("SABATO", 0.0))
                elif giorno_settimana == "DOM":
                    ore_value = safe_float(pdv_row.get("DOMENICA", 0.0))

                df.at[idx, "BASE_EDICOLA_ORE"] = ore_value
                df.at[idx, "EDICOLA_ORE"] = ore_value
            else:
                mon_value = 0.0
                giu_value = 0.0

                if giorno_settimana == "LUN":
                    mon_value = safe_float(pdv_row.get("MON_LUN", 0.0))
                    giu_value = safe_float(pdv_row.get("GIU_LUN", 0.0))
                elif giorno_settimana == "MAR":
                    mon_value = safe_float(pdv_row.get("MON_MAR", 0.0))
                    giu_value = safe_float(pdv_row.get("GIU_MAR", 0.0))
                elif giorno_settimana == "MER":
                    mon_value = safe_float(pdv_row.get("MON_MER", 0.0))
                    giu_value = safe_float(pdv_row.get("GIU_MER", 0.0))
                elif giorno_settimana == "GIO":
                    mon_value = safe_float(pdv_row.get("MON_GIO", 0.0))
                    giu_value = safe_float(pdv_row.get("GIU_GIO", 0.0))
                elif giorno_settimana == "VEN":
                    mon_value = safe_float(pdv_row.get("MON_VEN", 0.0))
                    giu_value = safe_float(pdv_row.get("GIU_VEN", 0.0))
                elif giorno_settimana == "SAB":
                    mon_value = safe_float(pdv_row.get("MON_SAB", 0.0))
                    giu_value = safe_float(pdv_row.get("GIU_SAB", 0.0))
                elif giorno_settimana == "DOM":
                    mon_value = safe_float(pdv_row.get("MON_DOM", 0.0))
                    giu_value = safe_float(pdv_row.get("GIU_DOM", 0.0))

                df.at[idx, "BASE_MONDADORI_ORE"] = mon_value
                df.at[idx, "MONDADORI_ORE"] = mon_value
                df.at[idx, "BASE_GIUNTI_ORE"] = giu_value
                df.at[idx, "GIUNTI_ORE"] = giu_value

        record["tabella"] = df


def step4_create_record(modalita: str, societa: str, attivita: str, anno: int, mese: int, selected_days: list[int]) -> dict:
    tabella = step4_build_empty_presence_dataframe(attivita, anno, mese, selected_days)

    return {
        "row_id": f"STEP4_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "origine_master": ORIGINE_EDICOLA if normalize_upper(attivita) == ORIGINE_EDICOLA else ORIGINE_LIBRI,
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
        "step4_modalita": normalize_text(modalita),
        "step4_selected_days": list(selected_days),
    }

def render_generation_page():
    step4_ensure_session_state()

    # Base reale pagina 2 STEP 3:
    # mantiene selezione massiva, eventuale stato righe generate,
    # tabella principale e logica coerente del mese.
    render_generation_page_step3()

    if not st.session_state["master_loaded"]:
        return

    anno = int(st.session_state.get("anno_step3", date.today().year))
    mese = int(st.session_state.get("mese_step3", date.today().month))

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="step4-action-box">', unsafe_allow_html=True)
    st.markdown('<div class="step4-action-title">NUOVO FOGLIO PRESENZA / SOSTITUZIONE</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step4-action-subtitle">Crea un foglio nuovo fuori dal flusso standard del master</div>',
        unsafe_allow_html=True,
    )

    societa_options = step4_get_societa_options()

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        step4_modalita = st.selectbox(
            "Cosa vuoi fare",
            ["Sostituzione con titolare", "Sostituzione con sostituto spot", "Foglio presenza vuoto"],
            key="step4_modalita",
        )
    with col_s2:
        step4_societa = st.selectbox("Società", societa_options, key="step4_societa")

    col_s3, col_s4 = st.columns(2)
    with col_s3:
        step4_attivita = st.selectbox("Attività", [ORIGINE_EDICOLA, ORIGINE_LIBRI], key="step4_attivita")
    with col_s4:
        step4_tipo_giorno = st.selectbox(
            "Giorno singolo oppure periodo",
            ["Giorno singolo", "Periodo"],
            key="step4_tipo_giorno",
        )

    giorni_mese = calendar.monthrange(anno, mese)[1]
    primo_giorno = date(anno, mese, 1)
    ultimo_giorno = date(anno, mese, giorni_mese)

    giorno_singolo_value = None
    periodo_value = None

    if step4_tipo_giorno == "Giorno singolo":
        giorno_singolo_value = st.date_input(
            "Giorno singolo",
            value=primo_giorno,
            min_value=primo_giorno,
            max_value=ultimo_giorno,
            key="step4_giorno_singolo_cal",
        )
    else:
        periodo_value = st.date_input(
            "Periodo",
            value=(primo_giorno, primo_giorno),
            min_value=primo_giorno,
            max_value=ultimo_giorno,
            key="step4_periodo_value",
        )

    selected_days = step4_get_selected_days(
        anno=anno,
        mese=mese,
        modo=step4_tipo_giorno,
        giorno_singolo_value=giorno_singolo_value,
        periodo_value=periodo_value,
    )

    dipendenti_table = pd.DataFrame()
    pdv_table = pd.DataFrame()

    if normalize_upper(step4_modalita) != "FOGLIO PRESENZA VUOTO":
        dipendenti_table = step4_build_dipendenti_table(step4_societa, step4_attivita, step4_modalita)
        pdv_table = step4_build_pdv_table(step4_societa, step4_attivita)

        filtro_dip = st.text_input(
            "Filtro tabella dipendenti",
            placeholder="Nome / cognome",
            key="step4_filtro_dip",
        )
        filtro_pdv = st.text_input(
            "Filtro tabella punto vendita",
            placeholder="Città / pdv",
            key="step4_filtro_pdv",
        )

        if filtro_dip.strip() and not dipendenti_table.empty:
            mask_dip = dipendenti_table["NOMINATIVO"].astype(str).str.upper().str.contains(filtro_dip.strip().upper(), na=False)
            dipendenti_table = dipendenti_table[mask_dip].copy()

        if filtro_pdv.strip() and not pdv_table.empty:
            mask_pdv = (
                pdv_table["PDV"].astype(str).str.upper().str.contains(filtro_pdv.strip().upper(), na=False)
                | pdv_table["CITTA"].astype(str).str.upper().str.contains(filtro_pdv.strip().upper(), na=False)
            )
            pdv_table = pdv_table[mask_pdv].copy()

        st.markdown('<div class="step4-legend-box">', unsafe_allow_html=True)
        st.markdown("<b>Tabella dipendenti</b>", unsafe_allow_html=True)

        if dipendenti_table.empty:
            st.info("Nessun dipendente coerente trovato.")
        else:
            dipendenti_table = dipendenti_table.reset_index(drop=True)
            dipendenti_table.insert(0, "SELEZIONA", False)

            dipendenti_table = st.data_editor(
                dipendenti_table,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "SELEZIONA": st.column_config.CheckboxColumn("Seleziona"),
                    "SOURCE_ID": None,
                    "NOMINATIVO": st.column_config.TextColumn("Nominativo", disabled=True),
                    "CODICE_FISCALE": st.column_config.TextColumn("Codice fiscale", disabled=True),
                    "TIPO_CONTRATTO": st.column_config.TextColumn("Tipo contratto", disabled=True),
                    "SCADENZA_CONTRATTO": st.column_config.TextColumn("Scadenza contratto", disabled=True),
                    "NETTO_ORA": st.column_config.NumberColumn("Netto orario", format="%.2f €", disabled=True),
                    "TEL": st.column_config.TextColumn("Tel", disabled=True),
                    "MAIL": st.column_config.TextColumn("Mail", disabled=True),
                },
                key="step4_table_dip",
            )

        st.markdown("<br><b>Tabella punto vendita</b>", unsafe_allow_html=True)

        if pdv_table.empty:
            st.info("Nessun PDV coerente trovato.")
        else:
            pdv_table = pdv_table.reset_index(drop=True)
            pdv_table.insert(0, "SELEZIONA", False)

            pdv_table = st.data_editor(
                pdv_table,
                hide_index=True,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "SELEZIONA": st.column_config.CheckboxColumn("Seleziona"),
                    "SOURCE_ID": None,
                    "PDV": st.column_config.TextColumn("PDV", disabled=True),
                    "CITTA": st.column_config.TextColumn("Città", disabled=True),
                    "TIPO_ATTIVITA": st.column_config.TextColumn("Tipo attività", disabled=True),
                    "LUN": st.column_config.NumberColumn("Lunedì", format="%.2f", disabled=True),
                    "MAR": st.column_config.NumberColumn("Martedì", format="%.2f", disabled=True),
                    "MER": st.column_config.NumberColumn("Mercoledì", format="%.2f", disabled=True),
                    "GIO": st.column_config.NumberColumn("Giovedì", format="%.2f", disabled=True),
                    "VEN": st.column_config.NumberColumn("Venerdì", format="%.2f", disabled=True),
                    "SAB": st.column_config.NumberColumn("Sabato", format="%.2f", disabled=True),
                    "DOM": st.column_config.NumberColumn("Domenica", format="%.2f", disabled=True),
                },
                key="step4_table_pdv",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    if normalize_upper(step4_modalita) == "FOGLIO PRESENZA VUOTO":
        if st.button("NUOVO FOGLIO PRESENZA / SOSTITUZIONE", type="primary", use_container_width=True):
            if not selected_days:
                st.error("Giorno o periodo non valido per il mese selezionato.")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                return

            record = step4_create_record(step4_modalita, step4_societa, step4_attivita, anno, mese, selected_days)
            key = format_sheet_key(record["row_id"], anno, mese)
            st.session_state["fogli_generati"][key] = record
            st.session_state["foglio_attivo"] = key
            st.session_state["sheet_warnings"][key] = []
            st.session_state["step4_last_created_key"] = key
            st.success("Nuovo foglio presenza vuoto creato correttamente.")
            st.rerun()
    else:
        if st.button("NUOVO FOGLIO PRESENZA / SOSTITUZIONE", type="primary", use_container_width=True):
            if not selected_days:
                st.error("Giorno o periodo non valido per il mese selezionato.")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                return

            dip_row, dip_count = step4_get_single_selected_row(
                dipendenti_table if not dipendenti_table.empty else pd.DataFrame()
            )
            pdv_row, pdv_count = step4_get_single_selected_row(
                pdv_table if not pdv_table.empty else pd.DataFrame()
            )

            if dip_count > 1 or pdv_count > 1:
                st.error("Selezionare una sola riga di origine dati per la compilazione del nuovo foglio presenza.")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                return

            if dip_count == 0 and pdv_count == 0:
                st.error("Selezionare almeno una riga dalle tabelle di scelta.")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                return

            record = step4_create_record(step4_modalita, step4_societa, step4_attivita, anno, mese, selected_days)
            step4_apply_selected_rows_to_record(record, dip_row, pdv_row)

            key = format_sheet_key(record["row_id"], anno, mese)
            st.session_state["fogli_generati"][key] = record
            st.session_state["foglio_attivo"] = key
            st.session_state["sheet_warnings"][key] = []
            st.session_state["step4_last_created_key"] = key
            st.success("Nuovo foglio presenza / sostituzione creato correttamente.")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# STEP 5 - CHIUSURA LOGICHE / FUNZIONI STEP 4
# VERSIONE DEFINITIVA
# DA INCOLLARE AL POSTO DELLO STEP 5 ATTUALE
# =========================

calculate_sheet_stats_step3 = calculate_sheet_stats
update_sheet_totals_step3 = update_sheet_totals
update_data_view_step3 = update_data_view


def step5_is_step4_dataframe(df: pd.DataFrame) -> bool:
    return "STEP4_RECORD" in df.columns


def step5_allowed_activity_columns(origine_master: str):
    if normalize_upper(origine_master) == ORIGINE_EDICOLA:
        return [
            ("EDICOLA_ORE", "EDICOLA_€", "EDICOLA_TIPO_ASSENZA", "BASE_EDICOLA_ORE"),
        ]
    return [
        ("MONDADORI_ORE", "MONDADORI_€", "MONDADORI_TIPO_ASSENZA", "BASE_MONDADORI_ORE"),
        ("GIUNTI_ORE", "GIUNTI_€", "GIUNTI_TIPO_ASSENZA", "BASE_GIUNTI_ORE"),
    ]


def step5_base_amount_for_row(df: pd.DataFrame, idx: int, netto_ora: float, societa: str, origine_master: str) -> float:
    totale = 0.0
    for _, _, _, base_col in step5_allowed_activity_columns(origine_master):
        base_ore = safe_float(df.at[idx, base_col])
        totale += calculate_row_amount(base_ore, netto_ora, bool(df.at[idx, "FESTIVO"]), societa)
    return round(totale, 2)


def step5_current_amount_for_row(df: pd.DataFrame, idx: int, origine_master: str) -> float:
    totale = 0.0
    for _, euro_col, _, _ in step5_allowed_activity_columns(origine_master):
        totale += safe_float(df.at[idx, euro_col])
    return round(totale, 2)


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

    is_step4 = step5_is_step4_dataframe(df)

    if is_step4:
        if has_assenza or current_tot < base_tot:
            return "RIDOTTA"
        if current_tot > base_tot:
            return "AUMENTATA"
        return ""

    if has_assenza or current_tot < base_tot:
        return "MODIFICATA"
    return ""


def update_data_view(df: pd.DataFrame) -> pd.DataFrame:
    updated = df.copy()
    is_step4 = step5_is_step4_dataframe(updated)

    for idx in updated.index:
        base_data = normalize_text(updated.at[idx, "DATA"])
        status = normalize_upper(updated.at[idx, "ROW_STATUS"])
        selected_day = bool(updated.at[idx, "STEP4_SELECTED_DAY"]) if "STEP4_SELECTED_DAY" in updated.columns else False

        prefix = []
        if selected_day:
            prefix.append("🟨")
        if status in {"RIDOTTA", "MODIFICATA"}:
            prefix.append("🔴")
        elif status == "AUMENTATA":
            prefix.append("🔵")

        if is_step4:
            updated.at[idx, "DATA_VIEW"] = f"{' '.join(prefix)} {base_data}".strip()
        else:
            if status == "MODIFICATA":
                updated.at[idx, "DATA_VIEW"] = f"🔴 {base_data}"
            else:
                updated.at[idx, "DATA_VIEW"] = base_data

    return updated


def apply_step3_rules(tabella: pd.DataFrame, netto_ora: float, societa: str, origine_master: str) -> tuple[pd.DataFrame, list[str]]:
    df = tabella.copy()
    warnings = []
    is_step4 = step5_is_step4_dataframe(df)

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
            new_value = max(0.0, safe_float(df.at[idx, ore_col]))

            if (not is_step4) and new_value > base_value:
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


def calculate_sheet_stats(df: pd.DataFrame, origine_master: str, netto_ora: float = 0.0, societa: str = "") -> dict:
    if not step5_is_step4_dataframe(df):
        return calculate_sheet_stats_step3(df, origine_master)

    current_hours_list = []
    base_hours_list = []
    base_euro_list = []
    current_euro_list = []
    zeroed_hours_only = []

    for idx in df.index:
        base_hours = round(
            safe_float(df.at[idx, "BASE_EDICOLA_ORE"])
            + safe_float(df.at[idx, "BASE_MONDADORI_ORE"])
            + safe_float(df.at[idx, "BASE_GIUNTI_ORE"]),
            2,
        )
        current_hours = round(
            safe_float(df.at[idx, "EDICOLA_ORE"])
            + safe_float(df.at[idx, "MONDADORI_ORE"])
            + safe_float(df.at[idx, "GIUNTI_ORE"]),
            2,
        )

        base_euro = step5_base_amount_for_row(df, idx, netto_ora, societa, origine_master)
        current_euro = step5_current_amount_for_row(df, idx, origine_master)

        current_hours_list.append(current_hours)
        base_hours_list.append(base_hours)
        base_euro_list.append(base_euro)
        current_euro_list.append(current_euro)

        if base_hours > 0 and current_hours == 0:
            zeroed_hours_only.append(base_hours)
        else:
            zeroed_hours_only.append(0.0)

    giorni_lavorati = int(sum(1 for x in current_hours_list if x > 0))
    giorni_modificati = int((df["ROW_STATUS"].astype(str).str.strip() != "").sum())
    tot_ore = round(sum(current_hours_list), 2)
    tot_ore_azzerate = round(sum(zeroed_hours_only), 2)

    riduzioni_euro = 0.0
    for base_euro, current_euro in zip(base_euro_list, current_euro_list):
        riduzioni_euro += max(0.0, round(base_euro - current_euro, 2))

    tot_attivita = round(sum(current_euro_list), 2)

    return {
        "GIORNI_LAVORATI": giorni_lavorati,
        "GIORNI_MODIFICATI": giorni_modificati,
        "TOT_ORE_LAVORATIVE_MESE": tot_ore,
        "TOT_ORE_AZZERATE": tot_ore_azzerate,
        "TOT_€_DA_SCALARE": round(riduzioni_euro, 2),
        "TOT_ATTIVITA_€": tot_attivita,
    }


def update_sheet_totals(record: dict):
    record["tabella"], _ = apply_step3_rules(
        tabella=record["tabella"],
        netto_ora=record["netto_ora"],
        societa=record["societa"],
        origine_master=normalize_upper(record["origine_master"]),
    )

    stats = calculate_sheet_stats(
        df=record["tabella"],
        origine_master=normalize_upper(record["origine_master"]),
        netto_ora=record["netto_ora"],
        societa=record["societa"],
    )

    record["giorni_lavorati"] = stats["GIORNI_LAVORATI"]
    record["giorni_modificati"] = stats["GIORNI_MODIFICATI"]
    record["tot_ore_lavorative_mese"] = stats["TOT_ORE_LAVORATIVE_MESE"]
    record["tot_ore_azzerate"] = stats["TOT_ORE_AZZERATE"]
    record["tot_euro_da_scalare"] = stats["TOT_€_DA_SCALARE"]
    record["tot_attivita"] = stats["TOT_ATTIVITA_€"]

    if record.get("is_step4", False):
        if not record.get("netto_mese_bloccato", False):
            if round(stats["TOT_ATTIVITA_€"], 2) > 0:
                record["netto_mese"] = round(stats["TOT_ATTIVITA_€"], 2)
                record["netto_mese_bloccato"] = True

        record["tot_netto_mese"] = round(
            safe_float(record["netto_mese"])
            - safe_float(record["tot_euro_da_scalare"])
            + safe_float(record["arretrati"])
            + safe_float(record["extra"])
            + safe_float(record["affiancamenti"])
            + safe_float(record["domeniche"])
            + safe_float(record["rimborso"]),
            2,
        )
    else:
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

    record["tabella"] = df

    update_sheet_totals(record)


def render_sheet_page():
    step4_ensure_session_state()

    if not st.session_state["fogli_generati"]:
        render_sheet_page_step3()
        return

    keys = list(st.session_state["fogli_generati"].keys())
    active_key = st.session_state["foglio_attivo"]

    if active_key not in keys:
        st.session_state["foglio_attivo"] = keys[0]
        active_key = keys[0]

    if not st.session_state["fogli_generati"][active_key].get("is_step4", False):
        render_sheet_page_step3()
        return

    render_page_title("3. Gestione foglio presenze")
    st.markdown('<div class="section-box">', unsafe_allow_html=True)

    selected_key = st.selectbox(
        "Seleziona foglio attivo",
        options=keys,
        index=keys.index(active_key),
        format_func=lambda k: (
            f"{st.session_state['fogli_generati'][k]['nome'] or 'SENZA NOME'} | "
            f"{st.session_state['fogli_generati'][k]['societa']} | "
            f"{st.session_state['fogli_generati'][k]['pdv'] or 'SENZA PDV'} | "
            f"{st.session_state['fogli_generati'][k]['attivita_riga']} | "
            f"{MESI[st.session_state['fogli_generati'][k]['mese']]} {st.session_state['fogli_generati'][k]['anno']}"
        ),
        key="step5_select_foglio_attivo",
    )
    st.session_state["foglio_attivo"] = selected_key
    record = st.session_state["fogli_generati"][selected_key]

    if not record.get("is_step4", False):
        st.markdown("</div>", unsafe_allow_html=True)
        render_sheet_page_step3()
        return

    if "netto_mese_bloccato" not in record:
        record["netto_mese_bloccato"] = round(safe_float(record.get("netto_mese", 0.0)), 2) > 0

    locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="soft-note">
            <b>Foglio creato con STEP 4</b><br>
            Modalità: {record.get('step4_modalita', '')}<br>
            Giorno/Periodo selezionato: {step4_days_text(record.get('step4_selected_days', []))}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="step4-legend-box">
            <b>Legenda righe</b><br>
            🟨 = giorno/periodo scelto<br>
            🔴 = riduzione o azzeramento ore<br>
            🔵 = aumento ore
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        record["societa"] = st.text_input("Società", value=record["societa"], disabled=locked, key=f"step5_societa_{selected_key}")
        st.text_input("Attività", value=record["attivita_riga"], disabled=True)
        record["nome"] = st.text_input("Nome", value=record["nome"], disabled=locked, key=f"step5_nome_{selected_key}")
    with col_h2:
        record["cf"] = st.text_input("CF", value=record["cf"], disabled=locked, key=f"step5_cf_{selected_key}")
        record["pdv"] = st.text_input("PDV", value=record["pdv"], disabled=locked, key=f"step5_pdv_{selected_key}")
        st.text_input("Mese", value=f"{MESI[record['mese']]} {record['anno']}", disabled=True)
    with col_h3:
        record["tipo_contratto"] = st.text_input("Tipo contratto", value=record["tipo_contratto"], disabled=locked, key=f"step5_tipo_contratto_{selected_key}")
        record["scadenza_contratto"] = st.text_input("Scadenza contratto", value=record["scadenza_contratto"], disabled=locked, key=f"step5_scadenza_{selected_key}")
        st.text_input("NETTO MESE", value=f"€ {record['netto_mese']:.2f}", disabled=True)

    with col_h4:
        record["netto_ora"] = st.number_input("Netto orario", value=float(record["netto_ora"]), step=0.10, disabled=locked, key=f"step5_netto_ora_{selected_key}")
        st.text_input("Giorni lavorati", value=str(int(record["giorni_lavorati"])), disabled=True)
        st.text_input("Giorni modificati", value=str(int(record["giorni_modificati"])), disabled=True)

    col_h5, col_h6, col_h7 = st.columns(3)
    with col_h5:
        st.text_input("Tot ore lavorative mese", value=f"{float(record['tot_ore_lavorative_mese']):.2f}", disabled=True)
    with col_h6:
        st.text_input("Tot ore azzerate", value=f"{float(record['tot_ore_azzerate']):.2f}", disabled=True)
    with col_h7:
        st.text_input("Tot € da scalare", value=f"€ {float(record['tot_euro_da_scalare']):.2f}", disabled=True)

    col_lock1, col_lock2 = st.columns(2)
    with col_lock1:
        record["lucchetto_foglio"] = st.checkbox(
            "Lucchetto foglio",
            value=record["lucchetto_foglio"],
            disabled=record["lucchetto_mese"],
            key=f"step5_lock_foglio_{selected_key}",
        )
    with col_lock2:
        record["lucchetto_mese"] = st.checkbox("Lucchetto mese", value=record["lucchetto_mese"], key=f"step5_lock_mese_{selected_key}")

    st.markdown("</div>", unsafe_allow_html=True)

    locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

    if selected_key in st.session_state["sheet_warnings"] and st.session_state["sheet_warnings"][selected_key]:
        for msg in st.session_state["sheet_warnings"][selected_key]:
            render_warning_box(msg)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Corpo foglio presenze</div>', unsafe_allow_html=True)

    if normalize_upper(record["origine_master"]) == ORIGINE_EDICOLA:
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
            height=1140,
            column_config={
                "GIORNO_NUM": st.column_config.NumberColumn("Giorno", disabled=True),
                "DATA_VIEW": st.column_config.TextColumn("Data", disabled=True),
                "GIORNO_SETTIMANA": st.column_config.TextColumn("Giorno settimana", disabled=True),
                "EDICOLA_ORE": st.column_config.NumberColumn("Edicola Ore", min_value=0.0, step=0.5, format="%.2f"),
                "EDICOLA_€": st.column_config.NumberColumn("Edicola €", format="%.2f €", disabled=True),
                "EDICOLA_TIPO_ASSENZA": st.column_config.SelectboxColumn("Edicola Tipo assenza", options=TIPI_ASSENZA),
                "FESTIVO": st.column_config.CheckboxColumn("Festivo"),
            },
            key=f"step5_editor_tabella_{selected_key}",
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
                    "STEP4_RECORD",
                    "STEP4_SELECTED_DAY",
                ]
            ].copy().reset_index(drop=True)

            merged = pd.concat([edited.copy().reset_index(drop=True), hidden_cols], axis=1)
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
                    "STEP4_RECORD",
                    "STEP4_SELECTED_DAY",
                ]
            ]

            old_visible = record["tabella"][visible_cols].copy().reset_index(drop=True)

            merged, warnings = apply_step3_rules(
                tabella=merged,
                netto_ora=record["netto_ora"],
                societa=record["societa"],
                origine_master=normalize_upper(record["origine_master"]),
            )

            record["tabella"] = merged
            st.session_state["sheet_warnings"][selected_key] = warnings
            update_sheet_totals(record)

            new_visible = merged[visible_cols].copy().reset_index(drop=True)
            if not new_visible.equals(old_visible):
                st.rerun()
    else:
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
            height=1140,
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
            key=f"step5_editor_tabella_{selected_key}",
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
                    "STEP4_RECORD",
                    "STEP4_SELECTED_DAY",
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
                    "STEP4_RECORD",
                    "STEP4_SELECTED_DAY",
                ]
            ]

            old_display = record["tabella"].copy().reset_index(drop=True)
            old_display.insert(6, "SEP_1", "│")
            old_visible = old_display[visible_cols].copy().reset_index(drop=True)

            merged, warnings = apply_step3_rules(
                tabella=merged,
                netto_ora=record["netto_ora"],
                societa=record["societa"],
                origine_master=normalize_upper(record["origine_master"]),
            )

            record["tabella"] = merged
            st.session_state["sheet_warnings"][selected_key] = warnings
            update_sheet_totals(record)

            new_display = merged.copy().reset_index(drop=True)
            new_display.insert(6, "SEP_1", "│")
            new_visible = new_display[visible_cols].copy().reset_index(drop=True)

            if not new_visible.equals(old_visible):
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Fondo foglio</div>', unsafe_allow_html=True)

    prev_fondo_values = (
        float(record["arretrati"]),
        float(record["extra"]),
        float(record["affiancamenti"]),
        float(record["domeniche"]),
        float(record["rimborso"]),
        record["note_generali"],
    )

    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
    with col_b1:
        record["arretrati"] = st.number_input("€ arretrato", value=float(record["arretrati"]), step=0.50, disabled=locked, key=f"step5_arretrati_{selected_key}")
    with col_b2:
        record["extra"] = st.number_input("€ extra", value=float(record["extra"]), step=0.50, disabled=locked, key=f"step5_extra_{selected_key}")
    with col_b3:
        record["affiancamenti"] = st.number_input("€ affiancamento", value=float(record["affiancamenti"]), step=0.50, disabled=locked, key=f"step5_affiancamenti_{selected_key}")
    with col_b4:
        record["domeniche"] = st.number_input("€ domeniche", value=float(record["domeniche"]), step=0.50, disabled=locked, key=f"step5_domeniche_{selected_key}")
    with col_b5:
        record["rimborso"] = st.number_input("€ rimborso", value=float(record["rimborso"]), step=0.50, disabled=locked, key=f"step5_rimborso_{selected_key}")

    uploaded_docs = st.file_uploader(
        "Allegati rimborso",
        accept_multiple_files=True,
        disabled=locked,
        key=f"step5_rimborso_upload_{selected_key}",
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
        key=f"step5_note_generali_{selected_key}",
    )

    update_sheet_totals(record)

    new_fondo_values = (
        float(record["arretrati"]),
        float(record["extra"]),
        float(record["affiancamenti"]),
        float(record["domeniche"]),
        float(record["rimborso"]),
        record["note_generali"],
    )

    if new_fondo_values != prev_fondo_values:
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="inner-box">', unsafe_allow_html=True)
    st.markdown('<div class="table-title">Totale finale</div>', unsafe_allow_html=True)

    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.markdown(
            """
            <div class="soft-note">
                <b>Formula STEP 4/5</b><br>
                TOT NETTO MESE = Netto Mese - Tot € da scalare + Arretrati + Extra + Affiancamenti + Domeniche + Rimborsi
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_t2:
        st.metric("TOT NETTO MESE", f"€ {record['tot_netto_mese']:.2f}")

    st.markdown("</div>", unsafe_allow_html=True)

    col_reset1, col_reset2 = st.columns([1, 1])

    with col_reset1:
        if st.button("Azzera ore foglio", disabled=locked, use_container_width=True, key=f"step5_azzera_{selected_key}"):
            clear_entire_sheet(record)
            st.session_state["sheet_warnings"][selected_key] = []
            st.rerun()

    with col_reset2:
        st.write("")

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# STEP 5,25 - AZZERAMENTO MASSIVO
# VERSIONE CORRETTA
# DA INCOLLARE AL POSTO DELLO STEP 5,25 ATTUALE
# =========================

render_generation_page_step45 = render_generation_page


def step525_get_selected_days(anno: int, mese: int, modo: str, giorno_singolo_value, periodo_value) -> list[int]:
    if modo == "Giorno singolo":
        if giorno_singolo_value is None:
            return []
        if giorno_singolo_value.year != anno or giorno_singolo_value.month != mese:
            return []
        return [int(giorno_singolo_value.day)]

    if not periodo_value or len(periodo_value) != 2:
        return []

    data_inizio, data_fine = periodo_value
    if not data_inizio or not data_fine:
        return []

    if data_inizio > data_fine:
        return []

    primo_giorno = date(anno, mese, 1)
    ultimo_giorno = date(anno, mese, calendar.monthrange(anno, mese)[1])

    if data_inizio < primo_giorno or data_fine > ultimo_giorno:
        return []

    giorni = []
    current = data_inizio
    while current <= data_fine:
        giorni.append(current.day)
        current = date.fromordinal(current.toordinal() + 1)

    return giorni


def step525_days_text(selected_days: list[int]) -> str:
    if not selected_days:
        return ""
    if len(selected_days) == 1:
        return f"Giorno {selected_days[0]}"
    return f"Giorni da {min(selected_days)} a {max(selected_days)}"


def step525_resolve_tipo_attivita(record: dict) -> str:
    origine_master = normalize_upper(record.get("origine_master", ""))
    attivita_riga = normalize_upper(record.get("attivita_riga", ""))

    if "EDICOLA" in origine_master or "EDICOLA" in attivita_riga:
        return ORIGINE_EDICOLA
    if "LIBRI" in origine_master or "LIBRI" in attivita_riga:
        return ORIGINE_LIBRI

    return origine_master or attivita_riga


def step525_build_massive_table(anno: int, mese: int, societa: str, attivita: str) -> pd.DataFrame:
    righe = []
    societa_up = normalize_upper(societa)
    attivita_up = normalize_upper(attivita)

    for key, record in st.session_state.get("fogli_generati", {}).items():
        if int(record.get("anno", 0)) != int(anno):
            continue
        if int(record.get("mese", 0)) != int(mese):
            continue
        if normalize_upper(record.get("societa", "")) != societa_up:
            continue

        tipo_attivita_record = step525_resolve_tipo_attivita(record)
        if normalize_upper(tipo_attivita_record) != attivita_up:
            continue

        righe.append(
            {
                "SELEZIONA": False,
                "FOGLIO_KEY": key,
                "NOMINATIVO_DIPENDENTE": normalize_text(record.get("nome", "")),
                "PDV": normalize_text(record.get("pdv", "")),
                "SOCIETA": normalize_text(record.get("societa", "")),
                "TIPO_ATTIVITA": normalize_text(tipo_attivita_record),
            }
        )

    if not righe:
        return pd.DataFrame(columns=["SELEZIONA", "FOGLIO_KEY", "NOMINATIVO_DIPENDENTE", "PDV", "SOCIETA", "TIPO_ATTIVITA"])

    return pd.DataFrame(righe)


def step525_zero_selected_days_on_record(record: dict, selected_days: list[int]):
    df = record["tabella"].copy()
    origine_master = step525_resolve_tipo_attivita(record)

    for idx in df.index:
        giorno_num = int(df.at[idx, "GIORNO_NUM"])
        if giorno_num not in selected_days:
            continue

        if origine_master == ORIGINE_EDICOLA:
            df.at[idx, "EDICOLA_ORE"] = 0.0
            df.at[idx, "EDICOLA_€"] = 0.0
        else:
            df.at[idx, "MONDADORI_ORE"] = 0.0
            df.at[idx, "MONDADORI_€"] = 0.0
            df.at[idx, "GIUNTI_ORE"] = 0.0
            df.at[idx, "GIUNTI_€"] = 0.0

    record["tabella"] = df
    update_sheet_totals(record)


def render_generation_page():
    render_generation_page_step45()

    if not st.session_state.get("master_loaded", False):
        return

    anno = int(st.session_state.get("anno_step3", date.today().year))
    mese = int(st.session_state.get("mese_step3", date.today().month))

    societa_options = sorted(
        list(
            set(
                st.session_state["df_edicola"]["AGENZIA"].dropna().astype(str).str.strip().tolist()
                + st.session_state["df_libri"]["AGENZIA"].dropna().astype(str).str.strip().tolist()
            )
        )
    )

    if not societa_options:
        return

    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<div class="step4-action-box">', unsafe_allow_html=True)
    st.markdown('<div class="step4-action-title">AZZERAMENTO MASSIVO</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step4-action-subtitle">Azzera le ore di più fogli presenza insieme senza aprirli uno per uno</div>',
        unsafe_allow_html=True,
    )

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        step525_societa = st.selectbox("Società", societa_options, key="step525_societa")
    with col_m2:
        step525_attivita = st.selectbox("Attività", [ORIGINE_EDICOLA, ORIGINE_LIBRI], key="step525_attivita")

    col_m3, col_m4 = st.columns(2)
    with col_m3:
        step525_tipo_giorno = st.selectbox(
            "Giorno singolo oppure periodo",
            ["Giorno singolo", "Periodo"],
            key="step525_tipo_giorno",
        )
    with col_m4:
        primo_giorno = date(anno, mese, 1)
        ultimo_giorno = date(anno, mese, calendar.monthrange(anno, mese)[1])

        giorno_singolo_value = None
        periodo_value = None

        if step525_tipo_giorno == "Giorno singolo":
            giorno_singolo_value = st.date_input(
                "Giorno singolo",
                value=primo_giorno,
                min_value=primo_giorno,
                max_value=ultimo_giorno,
                key="step525_giorno_singolo",
            )
        else:
            periodo_value = st.date_input(
                "Periodo",
                value=(primo_giorno, primo_giorno),
                min_value=primo_giorno,
                max_value=ultimo_giorno,
                key="step525_periodo",
            )

    selected_days = step525_get_selected_days(
        anno=anno,
        mese=mese,
        modo=step525_tipo_giorno,
        giorno_singolo_value=giorno_singolo_value,
        periodo_value=periodo_value,
    )

    filtro_nome = st.text_input(
        "Filtro tabella azzeramento massivo",
        placeholder="Nome / cognome / pdv",
        key="step525_filtro",
    )

    massive_table = step525_build_massive_table(
        anno=anno,
        mese=mese,
        societa=step525_societa,
        attivita=step525_attivita,
    )

    if filtro_nome.strip() and not massive_table.empty:
        filtro_up = filtro_nome.strip().upper()
        mask = (
            massive_table["NOMINATIVO_DIPENDENTE"].astype(str).str.upper().str.contains(filtro_up, na=False)
            | massive_table["PDV"].astype(str).str.upper().str.contains(filtro_up, na=False)
        )
        massive_table = massive_table[mask].copy()

    st.markdown('<div class="separator-help"><b>Seleziona i fogli presenza da azzerare</b></div>', unsafe_allow_html=True)

    if massive_table.empty:
        st.info("Nessun foglio presenza coerente trovato per i criteri selezionati.")
    else:
        edited_massive = st.data_editor(
            massive_table,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "SELEZIONA": st.column_config.CheckboxColumn("Seleziona"),
                "FOGLIO_KEY": None,
                "NOMINATIVO_DIPENDENTE": st.column_config.TextColumn("Nominativo dipendente", disabled=True),
                "PDV": st.column_config.TextColumn("PDV", disabled=True),
                "SOCIETA": st.column_config.TextColumn("Società", disabled=True),
                "TIPO_ATTIVITA": st.column_config.TextColumn("Tipo attività", disabled=True),
            },
            key="step525_massive_table",
        )

        selected_rows = edited_massive[edited_massive["SELEZIONA"] == True].copy()
        count_selected = len(selected_rows)

        if selected_days and count_selected > 0:
            st.markdown(
                f"""
                <div class="soft-note">
                    <b>Conferma operativa</b><br>
                    Fogli selezionati: {count_selected}<br>
                    Intervallo da azzerare: {step525_days_text(selected_days)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("AZZERA ORE", type="primary", use_container_width=True, key="step525_btn_azzera"):
            if not selected_days:
                st.error("Giorno o periodo non valido per il mese selezionato.")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                return

            if count_selected == 0:
                st.error("Seleziona almeno un foglio presenza dalla tabella.")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                return

            modificati = 0

            for _, row in selected_rows.iterrows():
                foglio_key = row["FOGLIO_KEY"]
                if foglio_key not in st.session_state["fogli_generati"]:
                    continue

                record = st.session_state["fogli_generati"][foglio_key]

                if record.get("lucchetto_mese", False) or record.get("lucchetto_foglio", False):
                    continue

                step525_zero_selected_days_on_record(record, selected_days)
                st.session_state["sheet_warnings"][foglio_key] = []
                modificati += 1

            st.success(f"Azzeramento massivo completato correttamente. Fogli modificati: {modificati}")

    st.markdown("</div>", unsafe_allow_html=True)
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
