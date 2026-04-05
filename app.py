import calendar
from copy import deepcopy
from datetime import date, datetime

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

COLONNE_TABELLA = [
    "GIORNO_NUM",
    "DATA",
    "GIORNO_SETTIMANA",
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
]

COLONNE_BASE_ORE = [
    "BASE_EDICOLA_ORE",
    "BASE_MONDADORI_ORE",
    "BASE_GIUNTI_ORE",
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


# =========================
# STILE
# =========================

def render_header():
    st.markdown(
        f"""
        <style>
            .block-container {{
                padding-top: 1.0rem;
                padding-bottom: 2rem;
            }}
            .app-box {{
                border: 1px solid #D9D9D9;
                border-radius: 12px;
                padding: 14px;
                background: #FFFFFF;
                margin-bottom: 12px;
            }}
            .titolo-admin {{
                font-size: 1.8rem;
                font-weight: 700;
                color: {COLOR_ROSSO};
                margin: 0;
            }}
            .sottotitolo-admin {{
                font-size: 1.05rem;
                font-weight: 600;
                color: #111111;
                margin: 0.2rem 0 0.8rem 0;
            }}
            .sezione-titolo {{
                font-size: 1.15rem;
                font-weight: 700;
                color: {COLOR_ROSSO};
                margin-bottom: 0.5rem;
            }}
            .note-box {{
                border-left: 4px solid {COLOR_ROSSO};
                background: #FFF8F8;
                padding: 10px 12px;
                border-radius: 8px;
                margin-bottom: 10px;
            }}
            .stButton > button {{
                border: 1px solid #CFCFCF;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_html = ""
    if LOGO_URL.strip():
        logo_html = f'<img src="{LOGO_URL}" style="max-height:72px; margin-bottom:10px;">'

    st.markdown(
        f"""
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


def format_sheet_key(cod_fiscale: str, societa: str, pdv: str, anno: int, mese: int) -> str:
    return f"{normalize_upper(cod_fiscale)}__{normalize_upper(societa)}__{normalize_upper(pdv)}__{anno}__{mese:02d}"


def style_presence_preview(df: pd.DataFrame):
    def row_style(row):
        stato = normalize_upper(row.get("STATO_RIGA", ""))
        if stato == "ASSENZA":
            return ["background-color: #FDECEC"] * len(row)
        if stato == "SOSTITUZIONE":
            return ["background-color: #EAF2FF"] * len(row)
        return [""] * len(row)

    return df.style.apply(row_style, axis=1)


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
# COSTRUZIONE RIGHE GENERAZIONE
# =========================

def build_generation_table(df_edicola: pd.DataFrame, df_libri: pd.DataFrame) -> pd.DataFrame:
    righe = []

    if not df_edicola.empty:
        ed = df_edicola.copy()
        ed["FONTE"] = "EDICOLA"
        for _, row in ed.iterrows():
            righe.append(
                {
                    "NOME": normalize_text(row["MHS_TITOLARE"]),
                    "COD_FISCALE": normalize_text(row["COD_FISCALE"]),
                    "SOCIETA": normalize_text(row["AGENZIA"]),
                    "PDV": normalize_text(row["PDV"]),
                    "TELEFONO": normalize_text(row["TEL_MHS"]),
                    "EMAIL": normalize_text(row["MAIL_MHS"]),
                    "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                    "NETTO_MESE": safe_float(row["COMPENSO_MENSILE"]),
                    "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                    "SCADENZA_CONTRATTO": normalize_text(row["SCADENZA_CONTRATTO"]),
                    "FONTE": "EDICOLA",
                }
            )

    if not df_libri.empty:
        lb = df_libri.copy()
        lb["FONTE"] = "LIBRI"
        for _, row in lb.iterrows():
            righe.append(
                {
                    "NOME": normalize_text(row["MHS_TITOLARE"]),
                    "COD_FISCALE": normalize_text(row["COD_FISCALE"]),
                    "SOCIETA": normalize_text(row["AGENZIA"]),
                    "PDV": normalize_text(row["PDV"]),
                    "TELEFONO": normalize_text(row["TEL_MHS"]),
                    "EMAIL": normalize_text(row["MAIL_MHS"]),
                    "NETTO_ORA": safe_float(row["NETTO_ORA"]),
                    "NETTO_MESE": 0.0,
                    "TIPO_CONTRATTO": normalize_text(row["TIPO_CONTRATTO"]),
                    "SCADENZA_CONTRATTO": normalize_text(row["SCADENZA_CONTRATTO"]),
                    "FONTE": "LIBRI",
                }
            )

    base = pd.DataFrame(righe)
    if base.empty:
        return base

    base["CHIAVE_BASE"] = base.apply(
        lambda row: f"{normalize_upper(row['COD_FISCALE'])}__{normalize_upper(row['SOCIETA'])}__{normalize_upper(row['PDV'])}",
        axis=1,
    )

    righe_finali = []
    for _, group in base.groupby("CHIAVE_BASE", dropna=False):
        first = group.iloc[0]
        netto_ora_list = [safe_float(v) for v in group["NETTO_ORA"].tolist() if safe_float(v) > 0]
        netto_mese_list = [safe_float(v) for v in group["NETTO_MESE"].tolist() if safe_float(v) > 0]
        tipo_list = [normalize_text(v) for v in group["TIPO_CONTRATTO"].tolist() if normalize_text(v)]
        scadenza_list = [normalize_text(v) for v in group["SCADENZA_CONTRATTO"].tolist() if normalize_text(v)]

        has_edicola = "EDICOLA" in set(group["FONTE"].tolist())
        has_libri = "LIBRI" in set(group["FONTE"].tolist())

        righe_finali.append(
            {
                "SELEZIONA": False,
                "NOME": normalize_text(first["NOME"]),
                "COD_FISCALE": normalize_text(first["COD_FISCALE"]),
                "SOCIETA": normalize_text(first["SOCIETA"]),
                "PDV": normalize_text(first["PDV"]),
                "TELEFONO": normalize_text(first["TELEFONO"]),
                "EMAIL": normalize_text(first["EMAIL"]),
                "NETTO_ORA": netto_ora_list[0] if netto_ora_list else 0.0,
                "NETTO_MESE": round(sum(netto_mese_list), 2),
                "TIPO_CONTRATTO": tipo_list[0] if tipo_list else "",
                "SCADENZA_CONTRATTO": scadenza_list[0] if scadenza_list else "",
                "ATTIVITA_PRESENTI": ", ".join(
                    [att for att, ok in [("EDICOLA", has_edicola), ("LIBRI", has_libri)] if ok]
                ),
                "CHIAVE_BASE": normalize_text(first["CHIAVE_BASE"]),
            }
        )

    result = pd.DataFrame(righe_finali)
    result = result.sort_values(["NOME", "SOCIETA", "PDV"]).reset_index(drop=True)
    return result


# =========================
# COSTRUZIONE FOGLIO
# =========================

def get_subset_by_key(df: pd.DataFrame, cod_fiscale: str, societa: str, pdv: str) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    return df[
        (df["COD_FISCALE"].apply(normalize_upper) == normalize_upper(cod_fiscale))
        & (df["AGENZIA"].apply(normalize_upper) == normalize_upper(societa))
        & (df["PDV"].apply(normalize_upper) == normalize_upper(pdv))
    ].copy()


def sum_hours_for_day(df: pd.DataFrame, giorno_label: str) -> float:
    if df.empty:
        return 0.0
    return round(df[giorno_label].apply(safe_float).sum(), 2)


def build_presence_dataframe(
    sub_edicola: pd.DataFrame,
    sub_libri: pd.DataFrame,
    netto_ora: float,
    societa: str,
    anno: int,
    mese: int,
) -> pd.DataFrame:
    giorni_mese = calendar.monthrange(anno, mese)[1]
    mondadori_df = sub_libri[sub_libri["TIPO_LIBRI"].apply(normalize_upper) == "MONDADORI"].copy()
    giunti_df = sub_libri[sub_libri["TIPO_LIBRI"].apply(normalize_upper) == "GIUNTI"].copy()

    righe = []
    for giorno_num in range(1, giorni_mese + 1):
        current_date = date(anno, mese, giorno_num)
        giorno_label = get_day_label(current_date)
        festivo_default = current_date.weekday() == 6

        edicola_ore = sum_hours_for_day(sub_edicola, giorno_label)
        mondadori_ore = sum_hours_for_day(mondadori_df, giorno_label)
        giunti_ore = sum_hours_for_day(giunti_df, giorno_label)

        righe.append(
            {
                "GIORNO_NUM": giorno_num,
                "DATA": current_date.strftime("%d/%m/%Y"),
                "GIORNO_SETTIMANA": giorno_label,
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
                "BASE_EDICOLA_ORE": edicola_ore,
                "BASE_MONDADORI_ORE": mondadori_ore,
                "BASE_GIUNTI_ORE": giunti_ore,
                "STATO_RIGA": "",
            }
        )

    return pd.DataFrame(righe)


def calculate_sheet_stats(df: pd.DataFrame) -> dict:
    edicola_ore = df["EDICOLA_ORE"].apply(safe_float)
    mondadori_ore = df["MONDADORI_ORE"].apply(safe_float)
    giunti_ore = df["GIUNTI_ORE"].apply(safe_float)

    base_edicola = df["BASE_EDICOLA_ORE"].apply(safe_float)
    base_mondadori = df["BASE_MONDADORI_ORE"].apply(safe_float)
    base_giunti = df["BASE_GIUNTI_ORE"].apply(safe_float)

    tot_ore = round((edicola_ore + mondadori_ore + giunti_ore).sum(), 2)
    tot_ore_azzerate = round(((base_edicola - edicola_ore) + (base_mondadori - mondadori_ore) + (base_giunti - giunti_ore)).sum(), 2)

    tot_euro = round(
        df["EDICOLA_€"].apply(safe_float).sum()
        + df["MONDADORI_€"].apply(safe_float).sum()
        + df["GIUNTI_€"].apply(safe_float).sum(),
        2,
    )

    giorni_lavorati = int(((edicola_ore + mondadori_ore + giunti_ore) > 0).sum())
    giorni_modificati = int((df["STATO_RIGA"].astype(str).str.strip() != "").sum())

    return {
        "GIORNI_LAVORATI": giorni_lavorati,
        "GIORNI_MODIFICATI": giorni_modificati,
        "TOT_ORE_LAVORATIVE_MESE": tot_ore,
        "TOT_ORE_AZZERATE": tot_ore_azzerate,
        "TOT_€_DA_SCALARE": 0.0,
        "TOT_ATTIVITA_€": tot_euro,
    }


def apply_step3_rules(tabella: pd.DataFrame, netto_ora: float, societa: str) -> tuple[pd.DataFrame, list[str]]:
    df = tabella.copy()
    warnings = []

    for col in ["EDICOLA_ORE", "MONDADORI_ORE", "GIUNTI_ORE"]:
        df[col] = df[col].apply(safe_float)

    for idx in df.index:
        for attivita, base_col in [
            ("EDICOLA", "BASE_EDICOLA_ORE"),
            ("MONDADORI", "BASE_MONDADORI_ORE"),
            ("GIUNTI", "BASE_GIUNTI_ORE"),
        ]:
            ore_col = f"{attivita}_ORE"
            euro_col = f"{attivita}_€"
            assenza_col = f"{attivita}_TIPO_ASSENZA"

            base_value = safe_float(df.at[idx, base_col])
            new_value = safe_float(df.at[idx, ore_col])

            if new_value > base_value:
                df.at[idx, ore_col] = base_value
                warnings.append(
                    f"Giorno {int(df.at[idx, 'GIORNO_NUM'])}: sulle ore {attivita} non è consentito aumentare oltre il valore generato."
                )

            if safe_float(df.at[idx, ore_col]) > 0 and normalize_text(df.at[idx, assenza_col]) != "":
                df.at[idx, assenza_col] = ""

            df.at[idx, euro_col] = calculate_row_amount(df.at[idx, ore_col], netto_ora, bool(df.at[idx, "FESTIVO"]), societa)

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
            df.at[idx, "STATO_RIGA"] = "ASSENZA"
        else:
            df.at[idx, "STATO_RIGA"] = ""

    if warnings:
        warnings = list(dict.fromkeys(warnings))

    return df, warnings


def init_sheet_record(row: pd.Series, df_edicola: pd.DataFrame, df_libri: pd.DataFrame, anno: int, mese: int) -> dict:
    sub_edicola = get_subset_by_key(df_edicola, row["COD_FISCALE"], row["SOCIETA"], row["PDV"])
    sub_libri = get_subset_by_key(df_libri, row["COD_FISCALE"], row["SOCIETA"], row["PDV"])

    tabella = build_presence_dataframe(
        sub_edicola=sub_edicola,
        sub_libri=sub_libri,
        netto_ora=safe_float(row["NETTO_ORA"]),
        societa=row["SOCIETA"],
        anno=anno,
        mese=mese,
    )
    tabella, _ = apply_step3_rules(tabella, safe_float(row["NETTO_ORA"]), row["SOCIETA"])
    stats = calculate_sheet_stats(tabella)

    record = {
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
        "scadenza_contratto": normalize_text(row["SCADENZA_CONTRATTO"]),
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
        "originale_step3": deepcopy(tabella),
        "tot_attivita": stats["TOT_ATTIVITA_€"],
        "tot_netto_mese": 0.0,
    }
    update_sheet_totals(record)
    return record


def update_sheet_totals(record: dict):
    record["tabella"], _ = apply_step3_rules(record["tabella"], record["netto_ora"], record["societa"])
    stats = calculate_sheet_stats(record["tabella"])
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
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================
# PAGINE
# =========================

def render_master_page():
    st.markdown('<div class="sezione-titolo">1. Caricamento master reali</div>', unsafe_allow_html=True)

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


def render_generation_page():
    st.markdown('<div class="sezione-titolo">2. Generazione fogli presenze</div>', unsafe_allow_html=True)

    if not st.session_state["master_loaded"]:
        st.warning("Prima carica e verifica i master nella sezione 'Caricamento master'.")
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
        return

    if filtro_nome.strip():
        mask = generation_table["NOME"].str.upper().str.contains(filtro_nome.strip().upper(), na=False)
        generation_table = generation_table[mask].copy()

    if generation_table.empty:
        st.info("Nessun risultato trovato con il filtro inserito.")
        return

    edited = st.data_editor(
        generation_table,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "SELEZIONA": st.column_config.CheckboxColumn("Seleziona"),
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
            "ATTIVITA_PRESENTI": st.column_config.TextColumn("Attività presenti", disabled=True),
            "CHIAVE_BASE": None,
        },
        key="editor_generation_table",
    )

    if st.button("Genera fogli presenze selezionati", type="primary", use_container_width=True):
        selected = edited[edited["SELEZIONA"] == True].copy()
        if selected.empty:
            st.warning("Seleziona almeno una riga.")
            return

        for _, row in selected.iterrows():
            key = format_sheet_key(row["COD_FISCALE"], row["SOCIETA"], row["PDV"], anno, mese)
            st.session_state["fogli_generati"][key] = init_sheet_record(
                row=row,
                df_edicola=st.session_state["df_edicola"],
                df_libri=st.session_state["df_libri"],
                anno=anno,
                mese=mese,
            )
            st.session_state["foglio_attivo"] = key

        st.success("Fogli presenze generati correttamente.")


def render_sheet_page():
    st.markdown('<div class="sezione-titolo">3. Gestione foglio presenze</div>', unsafe_allow_html=True)

    if not st.session_state["fogli_generati"]:
        st.warning("Prima genera almeno un foglio nella sezione 'Generazione fogli'.")
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
            f"{MESI[st.session_state['fogli_generati'][k]['mese']]} {st.session_state['fogli_generati'][k]['anno']}"
        ),
    )
    st.session_state["foglio_attivo"] = selected_key
    record = st.session_state["fogli_generati"][selected_key]

    locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1:
        st.text_input("Società", value=record["societa"], disabled=True)
        st.text_input("Nome", value=record["nome"], disabled=True)
        st.text_input("CF", value=record["cf"], disabled=True)
    with col_h2:
        st.text_input("PDV", value=record["pdv"], disabled=True)
        st.text_input("Mese", value=f"{MESI[record['mese']]} {record['anno']}", disabled=True)
        record["tipo_contratto"] = st.text_input("Tipo contratto", value=record["tipo_contratto"], disabled=locked)
    with col_h3:
        record["scadenza_contratto"] = st.text_input("Scadenza contratto", value=record["scadenza_contratto"], disabled=locked)
        record["netto_mese"] = st.number_input("NETTO MESE", value=float(record["netto_mese"]), step=0.50, disabled=locked)
        record["netto_ora"] = st.number_input("Netto orario", value=float(record["netto_ora"]), step=0.10, disabled=locked)
    with col_h4:
        st.number_input("Giorni lavorati", value=int(record["giorni_lavorati"]), disabled=True)
        st.number_input("Giorni modificati", value=int(record["giorni_modificati"]), disabled=True)
        st.number_input("Tot ore lavorative mese", value=float(record["tot_ore_lavorative_mese"]), disabled=True)

    col_h5, col_h6, col_h7 = st.columns(3)
    with col_h5:
        st.number_input("Tot ore azzerate", value=float(record["tot_ore_azzerate"]), disabled=True)
    with col_h6:
        st.number_input("Tot € da scalare", value=float(record["tot_euro_da_scalare"]), disabled=True)
    with col_h7:
        st.write("")

    col_lock1, col_lock2 = st.columns(2)
    with col_lock1:
        record["lucchetto_foglio"] = st.checkbox(
            "Lucchetto foglio",
            value=record["lucchetto_foglio"],
            disabled=record["lucchetto_mese"],
        )
    with col_lock2:
        record["lucchetto_mese"] = st.checkbox("Lucchetto mese", value=record["lucchetto_mese"])

    locked = record["lucchetto_mese"] or record["lucchetto_foglio"]

    st.markdown("#### Corpo foglio presenze")
    st.caption("Nel corpo foglio sono consentiti solo: invariato, riduzione ore, azzeramento ore. Aumento ore non consentito nello STEP 3.")

    editable_df = record["tabella"].copy()
    editor_key = f"editor_tabella_{selected_key}"

    visible_cols = COLONNE_TABELLA
    edited = st.data_editor(
        editable_df[visible_cols],
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=locked,
        column_config={
            "GIORNO_NUM": st.column_config.NumberColumn("Giorno", disabled=True),
            "DATA": st.column_config.TextColumn("Data", disabled=True),
            "GIORNO_SETTIMANA": st.column_config.TextColumn("Giorno settimana", disabled=True),
            "EDICOLA_ORE": st.column_config.NumberColumn("Edicola Ore", min_value=0.0, step=0.5, format="%.2f"),
            "EDICOLA_€": st.column_config.NumberColumn("Edicola €", format="%.2f €", disabled=True),
            "EDICOLA_TIPO_ASSENZA": st.column_config.SelectboxColumn("Edicola Tipo assenza", options=TIPI_ASSENZA),
            "MONDADORI_ORE": st.column_config.NumberColumn("Mondadori Ore", min_value=0.0, step=0.5, format="%.2f"),
            "MONDADORI_€": st.column_config.NumberColumn("Mondadori €", format="%.2f €", disabled=True),
            "MONDADORI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Mondadori Tipo assenza", options=TIPI_ASSENZA),
            "GIUNTI_ORE": st.column_config.NumberColumn("Giunti Ore", min_value=0.0, step=0.5, format="%.2f"),
            "GIUNTI_€": st.column_config.NumberColumn("Giunti €", format="%.2f €", disabled=True),
            "GIUNTI_TIPO_ASSENZA": st.column_config.SelectboxColumn("Giunti Tipo assenza", options=TIPI_ASSENZA),
            "FESTIVO": st.column_config.CheckboxColumn("Festivo"),
        },
        key=editor_key,
    )

    if not locked:
        hidden_cols = record["tabella"][COLONNE_BASE_ORE + ["STATO_RIGA"]].copy().reset_index(drop=True)
        merged = pd.concat([edited.reset_index(drop=True), hidden_cols], axis=1)
        merged, warnings = apply_step3_rules(merged, record["netto_ora"], record["societa"])
        record["tabella"] = merged
        update_sheet_totals(record)

        if warnings:
            for msg in warnings:
                st.warning(msg)
    else:
        update_sheet_totals(record)

    col_reset1, col_reset2 = st.columns([1, 2])
    with col_reset1:
        if st.button("Azzera foglio corrente", disabled=locked, use_container_width=True):
            record["tabella"] = deepcopy(record["originale_step3"])
            record["arretrati"] = 0.0
            record["extra"] = 0.0
            record["affiancamenti"] = 0.0
            record["domeniche"] = 0.0
            record["rimborso"] = 0.0
            record["rimborso_allegati"] = []
            record["note_generali"] = ""
            update_sheet_totals(record)
            st.rerun()

    st.markdown("#### Fondo foglio")
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

    st.markdown("#### Totale finale")
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.markdown(
            f"""
            <div class="note-box">
                <b>Formula STEP 3</b><br>
                TOT NETTO MESE = Tot attività + Arretrati + Extra + Affiancamenti + Domeniche + Rimborsi
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_t2:
        st.metric("TOT NETTO MESE", f"€ {record['tot_netto_mese']:.2f}")

    st.markdown("#### Evidenziazione righe")
    preview_df = record["tabella"][[
        "GIORNO_NUM", "DATA", "GIORNO_SETTIMANA",
        "EDICOLA_ORE", "EDICOLA_TIPO_ASSENZA",
        "MONDADORI_ORE", "MONDADORI_TIPO_ASSENZA",
        "GIUNTI_ORE", "GIUNTI_TIPO_ASSENZA",
        "FESTIVO", "STATO_RIGA"
    ]].copy()
    st.dataframe(style_presence_preview(preview_df), use_container_width=True, hide_index=True)


# =========================
# APP
# =========================

ensure_session_state()
render_header()

with st.sidebar:
    st.image(LOGO_URL, width=160)
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
