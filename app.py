import base64
from datetime import datetime, timedelta
import os
import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Ensure working directory is the app folder
APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)

# ==========================================================
# WEEK HELPER — Sunday-to-Sunday fixed calendar
# Aug 2–8=Wk32, Aug 9–15=Wk33, Aug 16–22=Wk34, Aug 23–29=Wk35
# Week anchor: Aug 2, 2026 = Week 32
# ==========================================================
import datetime as _dt

WEEK_ANCHOR_DATE = _dt.date(2026, 8, 2)  # This date = start of Week 32
WEEK_ANCHOR_NUM  = 32

def get_week(d):
    """Return custom week number based on Sunday-to-Sunday calendar.
    Aug 2–8 = Wk32, Aug 9–15 = Wk33, Aug 16–22 = Wk34, Aug 23–29 = Wk35
    """
    if hasattr(d, 'date'):
        d = d.date()
    delta = (d - WEEK_ANCHOR_DATE).days
    return WEEK_ANCHOR_NUM + delta // 7


st.set_page_config(
    page_title="Workforce Compliance Monitor",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================================
# GLOBAL CSS
# ==========================================================
st.markdown(
    """
    <style>
    #MainMenu {visibility:hidden;}
    header {visibility:hidden;}
    footer {visibility:hidden;}

    [data-testid="stToolbar"] {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    [data-testid="stDecoration"] {display:none !important;}
    [data-testid="stcollapsedControl"] {display:none !important;}
    .viewerBadge_container {display:none !important;}
    .viewerBadge_link {display:none !important;}
    #st-toolbar {display:none !important;}
    .stActionButton {display:none !important;}

    #manage-app-button {display:none !important;}
    div[data-testid="manage-app-button"] {display:none !important;}
    [data-testid="stConnectionStatus"] {display:none !important;}

    div[data-testid="stDownloadButton"] button {
        display:inline-flex !important;
        visibility:visible !important;
    }

    .stApp {
        background-color:#f8fafc;
    }

    .block-container {
        background:#ffffff !important;
        padding:1rem 1.5rem !important;
        border-radius:14px !important;
        margin-top:0.2rem !important;
        box-shadow:0 6px 20px rgba(0,0,0,0.05) !important;
        border:1px solid #e2e8f0 !important;
        max-width:100% !important;
    }

    .direct-header-img {
        width:100%;
        border-radius:14px;
        margin-bottom:12px;
        box-shadow:0 6px 20px rgba(168,85,247,0.12);
        border:1px solid rgba(216,180,254,0.6);
        display:block;
    }

    div[data-testid="stSelectbox"] {
        border:none !important;
        padding:0 !important;
        background:transparent !important;
    }

    div[data-testid="stSelectbox"] label p {
        font-weight:800 !important;
        color:#000000 !important;
        font-size:13px !important;
    }

    div[data-testid="stDateInput"] {
        border:2px dashed #ffb74d !important;
        padding:4px 10px !important;
        border-radius:10px !important;
        background:#fffdf5 !important;
    }

    div[data-testid="stDateInput"] label p {
        font-weight:800 !important;
        color:#000000 !important;
        font-size:13px !important;
    }

    .branch-logo {
        max-height:40px;
        margin-top:6px;
        border-radius:6px;
        object-fit:contain;
    }

    .feature-card {
        padding:12px;
        border-radius:14px;
        height:105px;
        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;
        text-align:center;
        box-shadow:0 3px 12px rgba(0,0,0,0.03);
        border:1.5px solid;
    }

    .fc-blue {
        background:#f0f6ff;
        border-color:#d2e3fc;
    }

    .fc-orange {
        background:#fefce8;
        border-color:#fef08a;
    }

    .fc-green {
        background:#f0fdf4;
        border-color:#bbf7d0;
    }

    .fc-purple {
        background:#faf5ff;
        border-color:#f3e8ff;
    }

    .fc-title {
        font-size:12.5px;
        font-weight:800;
        color:#1e1b4b;
        margin-top:4px;
        margin-bottom:2px;
    }

    .fc-text {
        font-size:10px;
        color:#475569;
        line-height:1.2;
        font-weight:500;
    }

    .metric-card {
        padding:18px;
        border-radius:12px 12px 0 0;
        color:white;
        font-family:sans-serif;
        box-shadow:0 4px 12px rgba(0,0,0,0.08);
        transition:transform 0.2s ease, box-shadow 0.2s ease;
        cursor:pointer;
    }

    .metric-card:hover {
        transform:translateY(-3px);
        box-shadow:0 8px 16px rgba(0,0,0,0.15);
    }

    .card-blue {
        background:linear-gradient(135deg,#3b82f6 0%,#1d4ed8 100%);
    }

    .card-red {
        background:linear-gradient(135deg,#ef4444 0%,#b91c1c 100%);
    }

    .card-orange {
        background:linear-gradient(135deg,#f59e0b 0%,#b45309 100%);
    }

    .card-purple {
        background:linear-gradient(135deg,#8b5cf6 0%,#6d28d9 100%);
    }

    .card-green {
        background:linear-gradient(135deg,#10b981 0%,#047857 100%);
    }

    .card-title {
        font-size:13px;
        font-weight:600;
        opacity:0.9;
        margin-bottom:6px;
        text-transform:uppercase;
        letter-spacing:0.5px;
    }

    .card-value {
        font-size:28px;
        font-weight:800;
    }

    .upl-section {
        background:#f8fafc;
        border:1px solid #e2e8f0;
        border-radius:14px;
        padding:15px;
        margin-top:20px;
    }

    .upl-heading {
        font-size:20px;
        font-weight:800;
        color:#111827;
        margin-bottom:12px;
    }

    .small-note {
        color:#64748b;
        font-size:11px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HELPERS
# ==========================================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""


def clean_id(val):
    try:
        return str(int(float(val))).strip()
    except Exception:
        return str(val).strip().lower()


def normalize_col(c):
    return (
        str(c)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace(".", " ")
    )


def parse_time(time_val):
    if pd.isna(time_val):
        return None

    value = str(time_val).strip()

    if value.lower() in ["nan", "none", "", "nat"]:
        return None

    for fmt in ["%H:%M:%S", "%H:%M", "%I:%M:%S %p", "%I:%M %p"]:
        try:
            return datetime.strptime(value, fmt).time()
        except Exception:
            pass

    return None


def percentage(numerator, denominator):
    if denominator in [0, None] or pd.isna(denominator):
        return 0.0
    return round((numerator / denominator) * 100, 2)


def safe_cell(df, row, col):
    """Safely read a cell from a DataFrame, returning None if out of range/blank."""
    try:
        val = df.iloc[row, col]
        if pd.isna(val):
            return None
        return val
    except Exception:
        return None


def parse_target_pct(val, default):
    """Parse a target percentage from a cell value like '3.50%', '3.50', or 3.5.
    Falls back to `default` if the cell is missing, blank, or unparseable."""
    if val is None:
        return default, False
    try:
        s = str(val).strip().replace('%', '')
        if s == '' or s.lower() in ['nan', 'none']:
            return default, False
        return round(float(s), 2), True
    except Exception:
        return default, False


# ==========================================================
# HEADER
# ==========================================================
header_paths = ["header_banner.png", os.path.join("AUH1", "header_banner.png")]
header_img_str = ""
for hp in header_paths:
    header_img_str = get_base64_of_bin_file(hp)
    if header_img_str:
        break

if header_img_str:
    st.markdown(
        f'<img src="data:image/png;base64,{header_img_str}" '
        'class="direct-header-img">',
        unsafe_allow_html=True,
    )
else:
    st.warning("⚠️ Please upload 'header_banner.png' to the app folder.")


# ==========================================================
# FILTERS
# ==========================================================
f_col1, f_col2 = st.columns([4, 8])

with f_col1:
    selected_warehouse = st.selectbox(
        "📍 Site",
        options=["AUH1", "DXB5", "DXB3"],
    )

    possible_logos = [
        os.path.join(selected_warehouse, f"{selected_warehouse}_logo.png"),
        os.path.join(selected_warehouse, f"{selected_warehouse}_logo.jpeg"),
        os.path.join(selected_warehouse, f"{selected_warehouse}_logo.jpg"),
        f"{selected_warehouse}_logo.png",
        f"{selected_warehouse}_logo.jpeg",
        f"{selected_warehouse}_logo.jpg",
    ]

    logo_path = next(
        (p for p in possible_logos if os.path.exists(p)),
        None,
    )

    if logo_path:
        logo_base64 = get_base64_of_bin_file(logo_path)
        mime_type = (
            "image/jpeg"
            if logo_path.endswith((".jpeg", ".jpg"))
            else "image/png"
        )
        st.markdown(
            f'<img src="data:{mime_type};base64,{logo_base64}" '
            'class="branch-logo">',
            unsafe_allow_html=True,
        )

with f_col2:
    selected_dates_range = st.date_input(
        "Select Date Range • Instant Auto-Fetch",
        value=[],
    )


# ==========================================================
# 7-HOUR / EXCLUDE CONFIGURATION
# ==========================================================
st.sidebar.header("⚙️ 7-Hours Configuration")

seven_hours_default = (
    "205854274, 206247771, 206930332, 206915012, 206065208, 206136723,"
    " 206200811, 205853892, 206192237, 206361774, 206348020, 206348027,"
    " 206348019, 206368537, 206348026, 206348045, 206348030, 206348048,"
    " 206348049, 206348041, 206368538, 206348029, 206348042, 205845552,"
    " 206348052, 206348054, 203875181, 203875184, 203875092, 203875089,"
    " 203875090, 203875180, 203875183, 112463068, 203875088, 203875091,"
    " 203875185, 203875186, 206868000, 206897671, 206897640, 206136735,"
    " 205231290, 205252357, 206192232, 206491343, 206128578, 206136722,"
    " 205252356, 205252538, 205199356, 206230579, 206491328, 206240253,"
    " 206930331, 206868288, 206897649, 206868005, 206239524, 206136718"
)

manual_7_ids = st.sidebar.text_area(
    "Paste 7-Hour Employee IDs (Comma separated)",
    value=seven_hours_default,
)

exclude_ids_input = st.sidebar.text_area(
    "Paste IDs to Ignore",
    value=(
        "203160008, 106495539, 203118578, 203073563, 204043092, 203052485,"
        " 203160007, 113015344, 203160009, 203118579, 203073561, 203052856,"
        " 203073425, 207574273, 202383469, 202383469, 203073699"
    ),
)


# ==========================================================
# LOAD HC MASTER
# ==========================================================
@st.cache_data(show_spinner=False)
def load_permanent_roster():
    roster = pd.DataFrame()

    possible_files = [
        os.path.join("AUH1", "HC.xlsx"),
        os.path.join("AUH1", "hc.xlsx"),
        "HC.xlsx",
        "hc.xlsx",
        "HC.XLSX",
        "hc.XLSX",
    ]

    for filename in possible_files:
        if os.path.exists(filename):
            try:
                roster = pd.read_excel(filename, dtype=str)
                break
            except Exception:
                continue

    if roster.empty:
        return roster

    roster.columns = [str(c).strip() for c in roster.columns]

    norm_map = {normalize_col(c): c for c in roster.columns}

    id_col = None

    for c in roster.columns:
        nc = normalize_col(c)
        if (
            nc in ["id", "employee id", "employee no", "employee number",
                   "psoft id", "psoft", "emp id", "emp no"]
            or "employee id" in nc
            or "psoft" in nc
        ):
            id_col = c
            break

    if id_col is None:
        id_col = roster.columns[0]

    roster["_Clean_ID"] = roster[id_col].apply(clean_id)

    return roster


roster_df = load_permanent_roster()


# ==========================================================
# ROSTER HOURS MAP
# ==========================================================
def build_roster_hours_map(roster):
    result = {}

    if roster.empty:
        return result

    for _, row in roster.iterrows():
        cid = clean_id(row.get("_Clean_ID", ""))

        if not cid:
            continue

        row_text = " ".join(str(v).lower() for v in row.tolist())

        if (
            "7 hour" in row_text
            or "7 hr" in row_text
            or "7hr" in row_text
            or "7.0" in row_text
        ):
            result[cid] = "7 Hours"
        else:
            result[cid] = "9 Hours"

    return result


roster_hours_map = build_roster_hours_map(roster_df)


# ==========================================================
# FILE PATH FINDER
# ==========================================================
def get_possible_paths(d, warehouse):
    d_str = d.strftime("%Y-%m-%d")
    folder = warehouse

    if warehouse == "AUH1":
        return [
            os.path.join(folder, f"{d_str}.xlsx.xlsx"),
            os.path.join(folder, f"{d_str}.xlsx"),
            os.path.join(folder, f"{d_str}.xls"),
            os.path.join(folder, f"{d_str}.csv"),
            f"{d_str}.xlsx.xlsx",
            f"{d_str}.xlsx",
            f"{d_str}.xls",
            f"{d_str}.csv",
        ]

    if warehouse == "DXB5":
        return [
            os.path.join(folder, f"DXB5 {d_str}.xlsx.xlsx"),
            os.path.join(folder, f"DXB5 {d_str}.xlsx"),
            os.path.join(folder, f"DXB5 {d_str}.xls"),
            os.path.join(folder, f"DXB5 {d_str}.csv"),
            os.path.join(folder, f"{d_str}.xlsx.xlsx"),
            os.path.join(folder, f"{d_str}.xlsx"),
            f"DXB5 {d_str}.xlsx.xlsx",
            f"DXB5 {d_str}.xlsx",
        ]

    if warehouse == "DXB3":
        return [
            os.path.join(folder, f"DXB3 {d_str}.xlsx.xlsx"),
            os.path.join(folder, f"DXB3 {d_str}.xlsx"),
            os.path.join(folder, f"DXB3 {d_str}.xls"),
            os.path.join(folder, f"DXB3 {d_str}.csv"),
            os.path.join(folder, f"{d_str}.xlsx.xlsx"),
            os.path.join(folder, f"{d_str}.xlsx"),
            f"DXB3 {d_str}.xlsx.xlsx",
            f"DXB3 {d_str}.xlsx",
        ]

    return [
        os.path.join(folder, f"{d_str}.xlsx.xlsx"),
        os.path.join(folder, f"{d_str}.xlsx"),
        f"{d_str}.xlsx.xlsx",
        f"{d_str}.xlsx",
    ]


# ==========================================================
# READ DAILY FILE
# ==========================================================
def read_daily_file(path):
    try:
        if path.lower().endswith(".csv"):
            return pd.read_csv(path, dtype=str)
        return pd.read_excel(path, sheet_name=0, dtype=str)
    except Exception:
        return pd.DataFrame()


# ==========================================================
# EXISTING ATTENDANCE PROCESSOR
# ==========================================================
@st.cache_data(show_spinner=False)
def process_attendance_data(dates_tuple, warehouse, manual_str, exclude_str, roster_map):
    manual_list = (
        [clean_id(x) for x in manual_str.split(",")]
        if manual_str
        else []
    )

    exclude_list = (
        [clean_id(x) for x in exclude_str.split(",")]
        if exclude_str
        else []
    )

    t_dfs = []
    missing_files = []

    start_d, end_d = dates_tuple

    date_list = [
        start_d + timedelta(days=i)
        for i in range((end_d - start_d).days + 1)
    ]

    for d in date_list:
        d_str = d.strftime("%Y-%m-%d")
        possible_paths = get_possible_paths(d, warehouse)

        f_path = next(
            (p for p in possible_paths if os.path.exists(p)),
            None,
        )

        if not f_path:
            missing_files.append(d_str)
            continue

        tdf = read_daily_file(f_path)

        if tdf.empty:
            missing_files.append(d_str)
            continue

        tdf["Date"] = d_str
        t_dfs.append(tdf)

    if not t_dfs:
        return pd.DataFrame(), missing_files

    a_df = pd.concat(t_dfs, ignore_index=True)
    a_df.columns = [str(c).strip() for c in a_df.columns]

    i_col = a_df.columns[0]
    n_col = a_df.columns[1]

    a_df["Clean_ID"] = a_df[i_col].apply(clean_id)

    if exclude_list:
        a_df = a_df[~a_df["Clean_ID"].isin(exclude_list)].copy()
        a_df.reset_index(drop=True, inplace=True)

    def get_hours(row):
        cid = row["Clean_ID"]
        if cid in manual_list:
            return "7 Hours"
        if cid in roster_map:
            return roster_map[cid]
        return "9 Hours"

    a_df["Working Hours"] = a_df.apply(get_hours, axis=1)

    ignore_kws = [
        "id", "name", "psoft", "employee", "building",
        "country", "working hours", "clean_id", "date",
    ]

    p_cols = [
        col for col in a_df.columns
        if not any(k in col.lower() for k in ignore_kws)
    ]

    if len(p_cols) == 0 and len(a_df.columns) > 4:
        p_cols = [c for c in a_df.columns[4:] if c != "Date"]

    def analyze(row):
        punches = [parse_time(row.get(c)) for c in p_cols]
        punches = [p for p in punches if p is not None]
        total_punches = len(punches)

        target = str(row.get("Working Hours", "9 Hours"))
        min_mins, max_mins = (405, 435) if "7" in target else (525, 555)

        if total_punches == 0:
            return pd.Series([0, target, "00:00", "OK", "Absent", "Clean"])

        if total_punches == 1:
            return pd.Series([1, target, "N/A", "Error", "Single Scan Only", "Mispunch"])

        dummy = datetime(2026, 1, 1)
        total_secs = 0

        for i in range(0, total_punches - (total_punches % 2), 2):
            start = datetime.combine(dummy, punches[i])
            end = datetime.combine(dummy, punches[i + 1])
            if end < start:
                end += timedelta(days=1)
            total_secs += (end - start).total_seconds()

        eff_mins = total_secs / 60
        hr_str = f"{int(total_secs // 3600):02d}:{int((total_secs % 3600) // 60):02d}"

        if total_punches % 2 == 0:
            if min_mins <= eff_mins <= max_mins:
                return pd.Series([total_punches, target, hr_str, "OK", "Complete Within Window", "Clean"])
            elif eff_mins < min_mins:
                return pd.Series([total_punches, target, hr_str, "Error", "Under Time", "Defaulter Hours"])
            else:
                return pd.Series([total_punches, target, hr_str, "Error", "Over Time", "Defaulter Hours"])

        return pd.Series([total_punches, target, hr_str, "Error", "Incomplete Punches", "Mispunch"])

    analyzed = a_df.apply(analyze, axis=1)
    analyzed.columns = [
        "Total Punches", "Assigned Target", "Calculated Hours",
        "Status", "Category", "Issue Type",
    ]

    p_clean = pd.DataFrame()
    for idx, col in enumerate(p_cols):
        label = "IN" if idx % 2 == 0 else "OUT"
        number = (idx // 2) + 1
        clean_col_name = label if number == 1 else f"{label} ({number})"
        p_clean[clean_col_name] = a_df[col].apply(
            lambda x: parse_time(x).strftime("%H:%M") if parse_time(x) else ""
        )

    basic_info = pd.DataFrame({
        "Date": a_df["Date"],
        "P.Soft ID": a_df[i_col].astype(str).str.replace(r"\.0$", "", regex=True).str.strip(),
        "Employee Name": a_df[n_col].astype(str).str.replace(r"\.0$", "", regex=True).str.strip(),
    })

    result = pd.concat([basic_info, analyzed, p_clean], axis=1)

    return result, missing_files


# ==========================================================
# UPL STATUS DETECTOR
# ==========================================================
def find_column(df, keywords):
    if df.empty:
        return None
    for col in df.columns:
        nc = normalize_col(col)
        for keyword in keywords:
            if keyword in nc:
                return col
    return None


def detect_status_from_row(row):
    possible_columns = [
        "status", "attendance status", "leave type", "leave",
        "absence type", "reason", "remarks", "attendance", "type",
    ]

    for col in row.index:
        nc = normalize_col(col)
        if any(keyword in nc for keyword in possible_columns):
            value = str(row.get(col, "")).strip().lower()
            if not value or value == "nan":
                continue
            if "abwi" in value or "absent without" in value:
                return "ABWI"
            if value == "ab" or value == "abs" or "absent" in value:
                return "AB"
            if value == "sl" or "sick leave" in value:
                return "SL"
            if value == "pl" or "planned leave" in value or "annual leave" in value or "vacation" in value:
                return "PL"

    return ""


# ==========================================================
# BUILD HC MASTER INFORMATION
# ==========================================================
def get_roster_master(roster):
    if roster.empty:
        return pd.DataFrame()

    result = roster.copy()

    id_col = None
    for col in result.columns:
        nc = normalize_col(col)
        if (
            "employee id" in nc or "psoft" in nc
            or nc in ["id", "emp id", "employee no", "employee number"]
        ):
            id_col = col
            break

    if id_col is None:
        id_col = result.columns[0]

    result["_Clean_ID"] = result[id_col].apply(clean_id)

    agency_col = find_column(result, ["agency", "vendor", "contractor", "supplier"])
    if agency_col:
        result["_Agency"] = result[agency_col].fillna("").astype(str).str.strip()
    else:
        result["_Agency"] = ""

    shift_col = find_column(result, ["shift", "schedule", "work shift", "shift code"])
    if shift_col:
        result["_Shift"] = result[shift_col].fillna("").astype(str).str.strip()
    else:
        result["_Shift"] = ""

    status_col = find_column(result, ["status", "attendance status", "leave type", "leave status", "absence type", "attendance"])
    if status_col:
        result["_Status"] = result[status_col].fillna("").astype(str).str.strip()
    else:
        result["_Status"] = ""

    return result


roster_master = get_roster_master(roster_df)


# ==========================================================
# UPL PROCESSOR
# ==========================================================
@st.cache_data(show_spinner=False)
def process_upl_report(dates_tuple, warehouse, exclude_str):
    start_d, end_d = dates_tuple

    exclude_list = (
        [clean_id(x) for x in exclude_str.split(",") if str(x).strip()]
        if exclude_str
        else []
    )

    date_list = [
        start_d + timedelta(days=i)
        for i in range((end_d - start_d).days + 1)
    ]

    daily_summary = []
    daily_employee_rows = []
    missing_files = []

    master = roster_master.copy()
    if not master.empty:
        if exclude_list:
            master = master[~master["_Clean_ID"].isin(exclude_list)].copy()

    for d in date_list:
        d_str = d.strftime("%Y-%m-%d")
        possible_paths = get_possible_paths(d, warehouse)

        file_path = next(
            (p for p in possible_paths if os.path.exists(p)),
            None,
        )

        if not file_path:
            missing_files.append(d_str)
            continue

        attendance = read_daily_file(file_path)

        if attendance.empty:
            missing_files.append(d_str)
            continue

        attendance.columns = [str(c).strip() for c in attendance.columns]

        id_col = attendance.columns[0]
        name_col = attendance.columns[1]

        attendance["_Clean_ID"] = attendance[id_col].apply(clean_id)

        if exclude_list:
            attendance = attendance[~attendance["_Clean_ID"].isin(exclude_list)].copy()

        ignore = ["id", "name", "employee", "psoft", "building", "country"]
        punch_cols = [
            c for c in attendance.columns
            if not any(x in normalize_col(c) for x in ignore)
            and normalize_col(c) not in ["date", "clean id"]
        ]

        attendance_ids = set(attendance["_Clean_ID"])

        if not master.empty:
            day_df = master[["_Clean_ID", "_Agency", "_Shift", "_Status"]].copy()
            day_df = day_df.drop_duplicates("_Clean_ID")
        else:
            day_df = pd.DataFrame({
                "_Clean_ID": list(attendance_ids),
                "_Agency": "",
                "_Shift": "",
                "_Status": "",
            })

        att_small = attendance.copy()
        keep_cols = ["_Clean_ID", id_col, name_col] + punch_cols
        keep_cols = list(dict.fromkeys(keep_cols))
        att_small = att_small[[c for c in keep_cols if c in att_small.columns]]

        day_df = day_df.merge(att_small, on="_Clean_ID", how="left")

        result_rows = []

        for _, row in day_df.iterrows():
            emp_id = clean_id(row.get("_Clean_ID", ""))
            name = str(row.get(name_col, "")).strip()
            agency = str(row.get("_Agency", "")).strip()
            shift = str(row.get("_Shift", "")).strip()
            master_status = str(row.get("_Status", "")).strip()

            punches = []
            for c in punch_cols:
                p = parse_time(row.get(c))
                if p:
                    punches.append(p)

            punch_count = len(punches)

            explicit_status = detect_status_from_row(row)
            if not explicit_status:
                explicit_status = master_status.upper()

            status_upper = explicit_status.strip().upper()

            if status_upper in ["PL", "PLANNED LEAVE", "ANNUAL LEAVE", "VACATION"]:
                category = "PL"
            elif status_upper in ["SL", "SICK LEAVE"]:
                category = "SL"
            elif status_upper in ["ABWI", "ABSENT WITHOUT INTIMATION"]:
                category = "ABWI"
            elif status_upper in ["AB", "ABS", "ABSENT"]:
                category = "AB"
            elif punch_count > 0:
                category = "Present"
            else:
                category = "AB"

            result_rows.append({
                "Date": d_str,
                "P.Soft ID": emp_id,
                "Employee Name": name,
                "Agency": agency,
                "Shift": shift,
                "Status Source": explicit_status,
                "Punches": punch_count,
                "UPL Category": category,
            })

        employee_day = pd.DataFrame(result_rows)

        if employee_day.empty:
            continue

        daily_employee_rows.append(employee_day)

        total_hc = len(employee_day)
        sl = int((employee_day["UPL Category"] == "SL").sum())
        ab = int((employee_day["UPL Category"] == "AB").sum())
        abwi = int((employee_day["UPL Category"] == "ABWI").sum())
        total_upl = sl + ab + abwi
        total_pl = int((employee_day["UPL Category"] == "PL").sum())

        shift_text = employee_day["Shift"].fillna("").astype(str).str.upper()
        hc_ns = int(shift_text.str.contains("NS|NIGHT|N", regex=True).sum())
        hc_ds = total_hc - hc_ns

        daily_summary.append({
            "Date": d.strftime("%d-%b-%y"),
            "HC DS": hc_ds,
            "HC NS": hc_ns,
            "Total HC": total_hc,
            "SL": sl,
            "AB": ab,
            "ABWI": abwi,
            "Total UPLs": total_upl,
            "UPL Target": 3.50,
            "UPL Trend": percentage(total_upl, total_hc),
            "Total PLs": total_pl,
            "PL Target": 9.67,
            "PL Trend": percentage(total_pl, total_hc),
        })

    daily_df = pd.DataFrame(daily_summary)

    employee_df = (
        pd.concat(daily_employee_rows, ignore_index=True)
        if daily_employee_rows
        else pd.DataFrame()
    )

    if not daily_df.empty:
        total_hc = int(daily_df["Total HC"].sum())
        total_sl = int(daily_df["SL"].sum())
        total_ab = int(daily_df["AB"].sum())
        total_abwi = int(daily_df["ABWI"].sum())
        total_upl = int(daily_df["Total UPLs"].sum())
        total_pl = int(daily_df["Total PLs"].sum())

        total_row = {
            "Date": "Total",
            "HC DS": int(daily_df["HC DS"].sum()),
            "HC NS": int(daily_df["HC NS"].sum()),
            "Total HC": total_hc,
            "SL": total_sl,
            "AB": total_ab,
            "ABWI": total_abwi,
            "Total UPLs": total_upl,
            "UPL Target": 3.50,
            "UPL Trend": percentage(total_upl, total_hc),
            "Total PLs": total_pl,
            "PL Target": 9.67,
            "PL Trend": percentage(total_pl, total_hc),
        }

        daily_df = pd.concat(
            [daily_df, pd.DataFrame([total_row])],
            ignore_index=True,
        )

    return daily_df, employee_df, missing_files


# ==========================================================
# AGENCY REPORT
# ==========================================================
def build_agency_report(employee_df):
    if employee_df.empty:
        return pd.DataFrame()

    data = employee_df.copy()
    data["Agency"] = data["Agency"].replace(["", "nan", "None"], "Unknown").fillna("Unknown")

    grouped = (
        data.groupby("Agency", dropna=False)
        .agg(
            HC=("P.Soft ID", "nunique"),
            UPL=("UPL Category", lambda x: int(x.isin(["SL", "AB", "ABWI"]).sum())),
            PL=("UPL Category", lambda x: int((x == "PL").sum())),
            SL=("UPL Category", lambda x: int((x == "SL").sum())),
            ABWI=("UPL Category", lambda x: int((x == "ABWI").sum())),
            AB=("UPL Category", lambda x: int((x == "AB").sum())),
        )
        .reset_index()
    )

    grouped["UPL Trend"] = grouped.apply(lambda r: percentage(r["UPL"], r["HC"]), axis=1)
    grouped["PL Trend"] = grouped.apply(lambda r: percentage(r["PL"], r["HC"]), axis=1)

    grouped = grouped[["Agency", "HC", "SL", "ABWI", "AB", "UPL", "UPL Trend", "PL", "PL Trend"]]

    return grouped.sort_values("Agency").reset_index(drop=True)


# ==========================================================
# WEEKLY SUMMARY
# ==========================================================
def build_weekly_summary(daily_df):
    if daily_df.empty:
        return pd.DataFrame()

    actual = daily_df[daily_df["Date"] != "Total"].copy()

    if actual.empty:
        return pd.DataFrame()

    total_hc = actual["Total HC"].sum()
    total_upl = actual["Total UPLs"].sum()
    total_pl = actual["Total PLs"].sum()

    return pd.DataFrame([
        {"Metric": "Unplanned Leave", "Target": 3.50, "Actual": percentage(total_upl, total_hc)},
        {"Metric": "Planned Leave", "Target": 9.67, "Actual": percentage(total_pl, total_hc)},
    ])


# ==========================================================
# MAIN PROCESS
# ==========================================================
if isinstance(selected_dates_range, tuple) and len(selected_dates_range) == 2:

    final_df, missing_files = process_attendance_data(
        tuple(selected_dates_range),
        selected_warehouse,
        manual_7_ids,
        exclude_ids_input,
        roster_hours_map,
    )

    upl_missing = []

    if not final_df.empty:
        mispunches = final_df[final_df["Issue Type"] == "Mispunch"].copy()
        defaulters = final_df[final_df["Issue Type"] == "Defaulter Hours"].copy()

        repeated_mispunches = pd.DataFrame()
        if not mispunches.empty:
            mis_counts = mispunches["P.Soft ID"].value_counts()
            repeated_mispunches = mispunches[
                mispunches["P.Soft ID"].isin(mis_counts[mis_counts > 1].index)
            ]
    else:
        mispunches = pd.DataFrame()
        defaulters = pd.DataFrame()
        repeated_mispunches = pd.DataFrame()

    # Calculate UPL tile value
    upl_tile_value = 0
    try:
        start_d_upl, end_d_upl = selected_dates_range
        for d_idx in range((end_d_upl - start_d_upl).days + 1):
            d_upl = start_d_upl + timedelta(days=d_idx)
            upl_fname_base = f"UPL-{selected_warehouse}-{d_upl.strftime('%d%m%Y')}.xlsx"
            upl_fname_folder = os.path.join(selected_warehouse, upl_fname_base)
            upl_fname = upl_fname_folder if os.path.exists(upl_fname_folder) else upl_fname_base
            if os.path.exists(upl_fname):
                dash_upl = pd.read_excel(upl_fname, sheet_name='Dashboard', dtype=str, header=None)
                upl_tile_value += int(dash_upl.iloc[8, 6])
    except Exception:
        upl_tile_value = "—"

    if "selected_view" not in st.session_state:
        st.session_state.selected_view = "defaulters"

    # TOP CARDS
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card card-purple" id="card_def">
                <div class="card-title">⏰ Defaulter Hours</div>
                <div class="card-value">{len(defaulters)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("⏰ View Defaulters ➔", key="btn_def", use_container_width=True):
            st.session_state.selected_view = "defaulters"

    with c2:
        st.markdown(
            f"""
            <div class="metric-card card-orange" id="card_mis">
                <div class="card-title">⚠️ Mispunches</div>
                <div class="card-value">{len(mispunches)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("⚠️ View Mispunches ➔", key="btn_mis", use_container_width=True):
            st.session_state.selected_view = "mispunches"

    with c3:
        st.markdown(
            f"""
            <div class="metric-card card-red" id="card_rep_mis">
                <div class="card-title">🔄 Repeated Mispunches</div>
                <div class="card-value">{len(repeated_mispunches)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🔄 View Rep. Mispunches ➔", key="btn_rep_mis", use_container_width=True):
            st.session_state.selected_view = "rep_mispunches"

    with c4:
        st.markdown(
            f"""
            <div class="metric-card card-blue" id="card_upl">
                <div class="card-title">📋 UPL Report</div>
                <div class="card-value">{upl_tile_value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("📋 View UPL Summary ➔", key="btn_upl", use_container_width=True):
            st.session_state.selected_view = "upl"

    # CARD CLICK JS
    components.html(
        """
        <script>
        const doc = window.parent.document;
        function bindCardClick(cardId, buttonTextMatch) {
            const card = doc.getElementById(cardId);
            if (card) {
                card.onclick = function() {
                    const buttons = Array.from(doc.querySelectorAll("button"));
                    const targetBtn = buttons.find(b => b.innerText.includes(buttonTextMatch));
                    if (targetBtn) { targetBtn.click(); }
                };
            }
        }
        setTimeout(() => {
            bindCardClick("card_def", "⏰ View Defaulters");
            bindCardClick("card_mis", "⚠️ View Mispunches");
            bindCardClick("card_rep_mis", "🔄 View Rep. Mispunches");
            bindCardClick("card_upl", "📋 View UPL Summary");
        }, 100);
        </script>
        """,
        height=0,
        width=0,
    )

    # UPL VIEW
    if st.session_state.selected_view == "upl":
        st.markdown("<div class='upl-section'>", unsafe_allow_html=True)
        st.markdown("<div class='upl-heading'>📋 UPL Report</div>", unsafe_allow_html=True)

        # Find UPL files for selected date range
        upl_files_found = []
        upl_missing_dates = []
        start_d, end_d = selected_dates_range
        upl_date_list = [start_d + timedelta(days=i) for i in range((end_d - start_d).days + 1)]

        for d in upl_date_list:
            fname_base = f"UPL-{selected_warehouse}-{d.strftime('%d%m%Y')}.xlsx"
            fname_folder = os.path.join(selected_warehouse, fname_base)
            if os.path.exists(fname_folder):
                upl_files_found.append((d, fname_folder))
            elif os.path.exists(fname_base):
                upl_files_found.append((d, fname_base))
            else:
                upl_missing_dates.append(d.strftime("%d-%b-%y"))

        if not upl_files_found:
            st.warning("⚠️ No UPL files found for selected dates. Expected format: UPL-AUH1-DDMMYYYY.xlsx")
        else:
            # Process Day wise from Dashboard sheet
            day_wise_data = []
            all_roster_scheduled = []
            target_fallback_used = False

            # Same exclusion list used everywhere else in the app, applied here too
            upl_exclude_list = (
                [clean_id(x) for x in exclude_ids_input.split(",") if str(x).strip()]
                if exclude_ids_input
                else []
            )

            for d, fname in upl_files_found:
                try:
                    dash = pd.read_excel(fname, sheet_name='Dashboard', dtype=str, header=None)
                    hc_ds = int(dash.iloc[5, 3])
                    hc_ns = int(dash.iloc[7, 3])
                    total_hc = int(dash.iloc[8, 3])
                    sl = int(dash.iloc[27, 7])
                    ab_abwi = int(dash.iloc[27, 8])
                    upl_total = int(dash.iloc[8, 6])
                    pl_total = int(dash.iloc[8, 4])

                    # Weekly target, read from the Dashboard sheet: put "UPL Target"
                    # and "PL Target" labels in cells N2/O2 (row idx 1, col idx 13/14)
                    # and the numeric % values right below in N3/O3 (row idx 2, col idx 13/14).
                    # (Cols H:M on rows 2-3 are already merged for the existing header
                    # block, so N/O — the next free unmerged columns — are used instead.)
                    # Falls back to 3.50% / 9.67% if those cells are blank/missing,
                    # so older files without the new column still work.
                    upl_target_val, upl_target_found = parse_target_pct(safe_cell(dash, 2, 13), 3.50)
                    pl_target_val, pl_target_found = parse_target_pct(safe_cell(dash, 2, 14), 9.67)
                    if not upl_target_found or not pl_target_found:
                        target_fallback_used = True

                    # Roster sheet: mirror the SAME filters the Dashboard tab applies,
                    # so the Agency-wise table (built from this "scheduled" frame)
                    # always reconciles with the Day-wise table above.
                    #   1) Building must match the selected site (Roster mixes AUH1/AUH3/DAD1 etc.)
                    #   2) Drop IDs on the sidebar "IDs to Ignore" list
                    #   3) Type == 'Direct' only (Dashboard excludes 'Support' staff)
                    #   4) Normalize agency name casing (e.g. 'QuessCorp' -> 'Quesscorp')
                    rdf = pd.read_excel(fname, sheet_name='Roster', dtype=str, header=None)
                    roster = rdf.iloc[6:].copy()
                    roster.columns = [str(c).strip() for c in rdf.iloc[5].tolist()]

                    roster['_Clean_ID'] = roster['Psoft No'].apply(clean_id)

                    if 'Building' in roster.columns:
                        roster = roster[roster['Building'] == selected_warehouse]

                    if upl_exclude_list:
                        roster = roster[~roster['_Clean_ID'].isin(upl_exclude_list)]

                    if 'Type' in roster.columns:
                        roster = roster[roster['Type'] == 'Direct']

                    if '3P' in roster.columns:
                        roster['3P'] = roster['3P'].replace('QuessCorp', 'Quesscorp')

                    scheduled = roster[
                        (roster['Attendance'] != 'OFF')
                        & (roster['Attendance'].notna())
                        & (roster['Attendance'].astype(str).str.strip() != '')
                    ].copy()

                    abwi_count = len(scheduled[scheduled['Attendance'] == 'ABWI'])
                    ab_count = len(scheduled[scheduled['Attendance'] == 'AB'])
                    sl_from_roster = len(scheduled[scheduled['Attendance'] == 'SL'])
                    pl_from_roster = len(scheduled[scheduled['Attendance'] == 'PL'])
                    upl_from_roster = sl_from_roster + ab_count + abwi_count
                    hc_from_roster = len(scheduled)

                    # Sanity check: flag any day where the filtered Roster still
                    # doesn't reconcile with the Dashboard tab, instead of silently
                    # showing mismatched totals downstream.
                    if hc_from_roster != total_hc or upl_from_roster != upl_total or pl_from_roster != pl_total:
                        upl_missing_dates.append(
                            f"{d.strftime('%d-%b-%y')} (Roster/Dashboard mismatch after filtering — "
                            f"HC {hc_from_roster} vs {total_hc}, UPL {upl_from_roster} vs {upl_total}, "
                            f"PL {pl_from_roster} vs {pl_total} — check Roster sheet for that date)"
                        )

                    # Collect roster for agency report
                    scheduled['_date'] = d.strftime('%d-%b-%y')
                    all_roster_scheduled.append(scheduled)

                    upl_trend = round((upl_total / total_hc) * 100, 2) if total_hc > 0 else 0
                    pl_trend = round((pl_total / total_hc) * 100, 2) if total_hc > 0 else 0

                    day_wise_data.append({
                        'Date': d.strftime('%d-%b-%y'),
                        'HC DS': hc_ds,
                        'HC NS': hc_ns,
                        'Total HC': total_hc,
                        'SL': sl,
                        'AB': ab_count,
                        'ABWI': abwi_count,
                        'Total UPLs': upl_total,
                        'Target': f'{upl_target_val:.2f}%',
                        'Trend': f'{upl_trend:.2f}%',
                        'Total PLs': pl_total,
                        'Target ': f'{pl_target_val:.2f}%',
                        'Trend ': f'{pl_trend:.2f}%',
                        '_UPLTargetNum': upl_target_val,
                        '_PLTargetNum': pl_target_val,
                    })
                except Exception:
                    upl_missing_dates.append(d.strftime('%d-%b-%y') + " (error)")

            if day_wise_data:
                day_df = pd.DataFrame(day_wise_data)

                # Calculate totals
                t_hc_ds = day_df['HC DS'].sum()
                t_hc_ns = day_df['HC NS'].sum()
                t_hc = day_df['Total HC'].sum()
                t_sl = day_df['SL'].sum()
                t_ab = day_df['AB'].sum()
                t_abwi = day_df['ABWI'].sum()
                t_upl = day_df['Total UPLs'].sum()
                t_pl = day_df['Total PLs'].sum()
                t_upl_trend = round((t_upl / t_hc) * 100, 2) if t_hc > 0 else 0
                t_pl_trend = round((t_pl / t_hc) * 100, 2) if t_hc > 0 else 0

                # HC-weighted average target across the selected days (handles a
                # date range that spans more than one week with different targets).
                t_upl_target = round((day_df['_UPLTargetNum'] * day_df['Total HC']).sum() / t_hc, 2) if t_hc > 0 else 3.50
                t_pl_target = round((day_df['_PLTargetNum'] * day_df['Total HC']).sum() / t_hc, 2) if t_hc > 0 else 9.67

                # Week number from selected dates (ISO week + 1 to match your system)
                week_no = get_week(upl_files_found[0][0])

                # ===== BOX 1: DAY WISE (full width, colored HTML table) =====
                st.markdown("**Day wise:-**")

                display_day = day_df[['Date','HC DS','HC NS','Total HC','SL','AB','ABWI','Total UPLs','Target','Trend','Total PLs','Target ','Trend ']].copy()
                total_row_df = pd.DataFrame([{
                    'Date': 'Total',
                    'HC DS': t_hc_ds,
                    'HC NS': t_hc_ns,
                    'Total HC': t_hc,
                    'SL': t_sl,
                    'AB': t_ab,
                    'ABWI': t_abwi,
                    'Total UPLs': t_upl,
                    'Target': f'{t_upl_target:.2f}%',
                    'Trend': f'{t_upl_trend:.2f}%',
                    'Total PLs': t_pl,
                    'Target ': f'{t_pl_target:.2f}%',
                    'Trend ': f'{t_pl_trend:.2f}%',
                }])
                display_day = pd.concat([display_day, total_row_df], ignore_index=True)

                # Per-row numeric targets, in the same row order as display_day,
                # used below to color Trend cells relative to each row's own target
                # instead of a single hardcoded threshold.
                row_upl_targets = list(day_df['_UPLTargetNum']) + [t_upl_target]
                row_pl_targets = list(day_df['_PLTargetNum']) + [t_pl_target]

                # Build colored HTML table for Day wise
                day_html = '<table style="border-collapse:collapse; width:100%; font-size:11px; font-family:sans-serif;">'
                # Header
                day_html += '<tr>'
                hdr_colors = ['#1a237e','#1a237e','#1a237e','#0d47a1','#e65100','#e65100','#e65100','#b71c1c','#4a148c','#2e7d32','#1565c0','#4a148c','#2e7d32']
                for idx_h, col in enumerate(display_day.columns):
                    day_html += f'<td style="padding:5px 8px; background:{hdr_colors[idx_h]}; color:white; font-weight:700; text-align:center; border:1px solid #ddd; white-space:nowrap;">{col}</td>'
                day_html += '</tr>'
                # Rows
                for row_idx in range(len(display_day)):
                    is_total = display_day.iloc[row_idx]['Date'] == 'Total'
                    bg = '#fff9c4' if is_total else ('#f8f9fa' if row_idx % 2 == 0 else '#ffffff')
                    fw = '700' if is_total else '500'
                    day_html += f'<tr style="background:{bg};">'
                    for col in display_day.columns:
                        val = display_day.iloc[row_idx][col]
                        cell_bg = ''
                        cell_color = '#000'
                        if col == 'Trend' and not is_total:
                            try:
                                trend_val = float(str(val).replace('%',''))
                                row_target = row_upl_targets[row_idx]
                                if trend_val <= row_target - 1.00:
                                    cell_bg = 'background:#c8e6c9;'
                                elif trend_val <= row_target:
                                    cell_bg = 'background:#fff9c4;'
                                else:
                                    cell_bg = 'background:#ffcdd2;'
                            except: pass
                        if col == 'Trend ' and not is_total:
                            try:
                                trend_val = float(str(val).replace('%',''))
                                row_target = row_pl_targets[row_idx]
                                if trend_val <= row_target:
                                    cell_bg = 'background:#c8e6c9;'
                                elif trend_val <= row_target + 0.83:
                                    cell_bg = 'background:#fff9c4;'
                                else:
                                    cell_bg = 'background:#ffcdd2;'
                            except: pass
                        day_html += f'<td style="padding:4px 8px; text-align:center; border:1px solid #ddd; font-weight:{fw}; {cell_bg} color:{cell_color}; white-space:nowrap;">{val}</td>'
                    day_html += '</tr>'
                day_html += '</table>'
                st.markdown(day_html, unsafe_allow_html=True)

                st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)

                # ===== BOX 2: AGENCY WISE + BAR CHART =====
                if all_roster_scheduled:
                    combined_roster = pd.concat(all_roster_scheduled, ignore_index=True)
                    combined_roster['3P'] = combined_roster['3P'].replace('QuessCorp', 'Quesscorp')

                    agency_data = []
                    for agency in sorted(combined_roster['3P'].dropna().unique()):
                        ag = combined_roster[combined_roster['3P'] == agency]
                        ag_hc = len(ag)
                        ag_sl = len(ag[ag['Attendance'] == 'SL'])
                        ag_abwi = len(ag[ag['Attendance'] == 'ABWI'])
                        ag_ab = len(ag[ag['Attendance'] == 'AB'])
                        ag_upl = ag_sl + ag_abwi + ag_ab
                        ag_pl = len(ag[ag['Attendance'] == 'PL'])
                        ag_upl_trend = round((ag_upl / ag_hc) * 100, 2) if ag_hc > 0 else 0
                        ag_pl_trend = round((ag_pl / ag_hc) * 100, 2) if ag_hc > 0 else 0

                        agency_data.append({
                            'Agency': agency,
                            'Week No': week_no,
                            'Total HC': ag_hc,
                            'SL': ag_sl,
                            'ABWI': ag_abwi,
                            'NCNS': ag_ab,
                            'Total UPLs': ag_upl,
                            'Trend': f'{ag_upl_trend:.2f}%',
                            'Total PLs': ag_pl,
                            'PL Trend': f'{ag_pl_trend:.2f}%',
                        })

                    agency_df_display = pd.DataFrame(agency_data)

                    ag_t_hc = agency_df_display['Total HC'].sum()
                    ag_t_sl = agency_df_display['SL'].sum()
                    ag_t_abwi = agency_df_display['ABWI'].sum()
                    ag_t_ncns = agency_df_display['NCNS'].sum()
                    ag_t_upl = agency_df_display['Total UPLs'].sum()
                    ag_t_pl = agency_df_display['Total PLs'].sum()
                    ag_t_upl_trend = round((ag_t_upl / ag_t_hc) * 100, 2) if ag_t_hc > 0 else 0
                    ag_t_pl_trend = round((ag_t_pl / ag_t_hc) * 100, 2) if ag_t_hc > 0 else 0

                    ag_total_row = pd.DataFrame([{
                        'Agency': 'Total',
                        'Week No': week_no,
                        'Total HC': ag_t_hc,
                        'SL': ag_t_sl,
                        'ABWI': ag_t_abwi,
                        'NCNS': ag_t_ncns,
                        'Total UPLs': ag_t_upl,
                        'Trend': f'{ag_t_upl_trend:.2f}%',
                        'Total PLs': ag_t_pl,
                        'PL Trend': f'{ag_t_pl_trend:.2f}%',
                    }])
                    agency_df_display = pd.concat([agency_df_display, ag_total_row], ignore_index=True)

                    ag_left, ag_right = st.columns([6, 4])

                    with ag_left:
                        st.markdown("**Agency wise:-**")
                        # Colored HTML table for agency
                        ag_html = '<table style="border-collapse:collapse; width:100%; font-size:11px; font-family:sans-serif;">'
                        ag_cols = ['Agency','Week No','Total HC','SL','ABWI','NCNS','Total UPLs','Trend','Total PLs','PL Trend']
                        ag_hdr_colors = ['#00695c','#00695c','#0d47a1','#e65100','#e65100','#e65100','#b71c1c','#2e7d32','#1565c0','#2e7d32']
                        ag_html += '<tr>'
                        for idx_h, col in enumerate(ag_cols):
                            ag_html += f'<td style="padding:5px 6px; background:{ag_hdr_colors[idx_h]}; color:white; font-weight:700; text-align:center; border:1px solid #ddd; white-space:nowrap;">{col}</td>'
                        ag_html += '</tr>'
                        for row_idx in range(len(agency_df_display)):
                            is_total = agency_df_display.iloc[row_idx]['Agency'] == 'Total'
                            bg = '#fff9c4' if is_total else ('#f1f8e9' if row_idx % 2 == 0 else '#ffffff')
                            fw = '700' if is_total else '500'
                            ag_html += f'<tr style="background:{bg};">'
                            for col in ag_cols:
                                val = agency_df_display.iloc[row_idx][col]
                                cell_bg = ''
                                if col == 'Trend' and not is_total:
                                    try:
                                        tv = float(str(val).replace('%',''))
                                        if tv <= 3.00: cell_bg = 'background:#c8e6c9;'
                                        elif tv <= 5.00: cell_bg = 'background:#fff9c4;'
                                        else: cell_bg = 'background:#ffcdd2;'
                                    except: pass
                                if col == 'PL Trend' and not is_total:
                                    try:
                                        tv = float(str(val).replace('%',''))
                                        if tv <= 9.67: cell_bg = 'background:#c8e6c9;'
                                        elif tv <= 11.00: cell_bg = 'background:#fff9c4;'
                                        else: cell_bg = 'background:#ffcdd2;'
                                    except: pass
                                ag_html += f'<td style="padding:4px 6px; text-align:center; border:1px solid #ddd; font-weight:{fw}; {cell_bg} white-space:nowrap;">{val}</td>'
                            ag_html += '</tr>'
                        ag_html += '</table>'
                        st.markdown(ag_html, unsafe_allow_html=True)

                    with ag_right:
                        st.markdown("#### 📊 Agency UPL Share")
                        chart_data = agency_df_display[agency_df_display['Agency'] != 'Total'][['Agency', 'Total UPLs']].copy()
                        chart_data = chart_data.sort_values('Total UPLs', ascending=False).reset_index(drop=True)

                        # Color gradient: dark red (highest) -> light red -> orange -> yellow -> light green -> green (lowest)
                        gradient_colors = ['#b71c1c', '#e53935', '#f57c00', '#fdd835', '#81c784', '#2e7d32']
                        num_bars = len(chart_data)
                        bar_colors = gradient_colors[:num_bars] if num_bars <= len(gradient_colors) else gradient_colors

                        chart_data['Color'] = bar_colors[:num_bars]
                        agency_order = chart_data['Agency'].tolist()

                        bar_chart = alt.Chart(chart_data).mark_bar(
                            cornerRadiusTopLeft=6,
                            cornerRadiusTopRight=6,
                            size=28,
                        ).encode(
                            x=alt.X('Agency:N', sort=agency_order, axis=alt.Axis(labelAngle=-45, labelFontSize=10)),
                            y=alt.Y('Total UPLs:Q', title='Total UPL Count'),
                            color=alt.Color('Agency:N', legend=None, scale=alt.Scale(
                                domain=agency_order,
                                range=bar_colors[:num_bars]
                            )),
                            tooltip=['Agency', 'Total UPLs']
                        ).properties(height=320)
                        st.altair_chart(bar_chart, use_container_width=True)

                # ===== BOX 3: SUMMARY + PIE CHART side by side =====
                st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
                st.markdown("**Summary:-**")

                # Build per-week summary from day_wise_data
                weeks_summary = {}
                for d, fname in upl_files_found:
                    wk = get_week(d)
                    if wk not in weeks_summary:
                        weeks_summary[wk] = {'hc': 0, 'upl': 0, 'pl': 0, 'upl_target_wsum': 0.0, 'pl_target_wsum': 0.0}
                for row in day_wise_data:
                    row_date_str = row['Date']
                    row_date = None
                    for d, fname in upl_files_found:
                        if d.strftime('%d-%b-%y') == row_date_str:
                            row_date = d
                            break
                    if row_date:
                        wk = get_week(row_date)
                        weeks_summary[wk]['hc'] += row['Total HC']
                        weeks_summary[wk]['upl'] += row['Total UPLs']
                        weeks_summary[wk]['pl'] += row['Total PLs']
                        # HC-weighted target, in case a week ever mixes two target values
                        weeks_summary[wk]['upl_target_wsum'] += row['_UPLTargetNum'] * row['Total HC']
                        weeks_summary[wk]['pl_target_wsum'] += row['_PLTargetNum'] * row['Total HC']

                sum_left, sum_right = st.columns([6, 4])

                with sum_left:
                    sorted_weeks = sorted(weeks_summary.keys())
                    num_weeks = len(sorted_weeks)

                    # Build table with weeks as COLUMNS
                    tbl = '<table style="border-collapse:collapse; width:100%; font-size:13px; font-weight:600; border:2px solid #000;">'

                    # Title row
                    tbl += '<tr style="background:#b0c4de; text-align:center;"><td colspan="' + str(num_weeks + 2) + '" style="padding:8px; border:2px solid #000; font-size:15px; font-weight:800;">UPL Trend</td></tr>'

                    # ---- UNPLANNED LEAVE SECTION ----
                    tbl += '<tr style="background:#fde0d0; text-align:center;"><td colspan="' + str(num_weeks + 2) + '" style="padding:6px; border:2px solid #000; font-weight:700; font-size:14px;">Unplanned Leave</td></tr>'

                    # Week header row
                    tbl += '<tr style="text-align:center;"><td style="padding:8px; border:2px solid #000; background:#c8e6c9; font-weight:700; font-size:14px;" rowspan="3">' + selected_warehouse + '</td>'
                    tbl += '<td style="padding:6px; border:2px solid #000;"></td>'
                    for wk in sorted_weeks:
                        tbl += '<td style="padding:6px 10px; border:2px solid #000; background:#9b59b6; color:white; font-weight:700;">Week ' + str(wk) + '</td>'
                    tbl += '</tr>'

                    # Target row
                    tbl += '<tr style="text-align:center;"><td style="padding:7px; border:2px solid #000; font-weight:700;">Target</td>'
                    for wk in sorted_weeks:
                        wk_hc_t = weeks_summary[wk]['hc']
                        wk_upl_target = round(weeks_summary[wk]['upl_target_wsum'] / wk_hc_t, 2) if wk_hc_t > 0 else 3.50
                        tbl += '<td style="padding:7px; border:2px solid #000; background:#2e7d32; color:white; font-weight:700;">' + f'{wk_upl_target:.2f}' + '%</td>'
                    tbl += '</tr>'

                    # Actual UPL row
                    tbl += '<tr style="text-align:center;"><td style="padding:7px; border:2px solid #000; font-weight:700;">Actual</td>'
                    for wk in sorted_weeks:
                        wk_hc = weeks_summary[wk]['hc']
                        wk_upl = weeks_summary[wk]['upl']
                        wk_upl_trend = round((wk_upl / wk_hc) * 100, 2) if wk_hc > 0 else 0
                        tbl += '<td style="padding:7px; border:2px solid #000; background:#f1c40f; color:#000; font-weight:700;">' + str(wk_upl_trend) + '%</td>'
                    tbl += '</tr>'

                    # ---- PLANNED LEAVE SECTION ----
                    tbl += '<tr style="background:#fde0d0; text-align:center;"><td colspan="' + str(num_weeks + 2) + '" style="padding:6px; border:2px solid #000; font-weight:700; font-size:14px;">Planned Leave</td></tr>'

                    # Week header row
                    tbl += '<tr style="text-align:center;"><td style="padding:8px; border:2px solid #000; background:#c8e6c9; font-weight:700; font-size:14px;" rowspan="3">' + selected_warehouse + '</td>'
                    tbl += '<td style="padding:6px; border:2px solid #000;"></td>'
                    for wk in sorted_weeks:
                        tbl += '<td style="padding:6px 10px; border:2px solid #000; background:#9b59b6; color:white; font-weight:700;">Week ' + str(wk) + '</td>'
                    tbl += '</tr>'

                    # Target row
                    tbl += '<tr style="text-align:center;"><td style="padding:7px; border:2px solid #000; font-weight:700;">Target</td>'
                    for wk in sorted_weeks:
                        wk_hc_t = weeks_summary[wk]['hc']
                        wk_pl_target = round(weeks_summary[wk]['pl_target_wsum'] / wk_hc_t, 2) if wk_hc_t > 0 else 9.67
                        tbl += '<td style="padding:7px; border:2px solid #000; background:#2e7d32; color:white; font-weight:700;">' + f'{wk_pl_target:.2f}' + '%</td>'
                    tbl += '</tr>'

                    # Actual PL row
                    tbl += '<tr style="text-align:center;"><td style="padding:7px; border:2px solid #000; font-weight:700;">Actual</td>'
                    for wk in sorted_weeks:
                        wk_hc = weeks_summary[wk]['hc']
                        wk_pl = weeks_summary[wk]['pl']
                        wk_pl_trend = round((wk_pl / wk_hc) * 100, 2) if wk_hc > 0 else 0
                        tbl += '<td style="padding:7px; border:2px solid #000; background:#f1c40f; color:#000; font-weight:700;">' + str(wk_pl_trend) + '%</td>'
                    tbl += '</tr>'

                    tbl += '</table>'
                    st.markdown(tbl, unsafe_allow_html=True)
                with sum_right:
                    # Weekly bar + line combo — one bar per week per metric, with a
                    # connected line + circle markers on top showing the same value,
                    # labeled with the number above each marker (Week 32, Week 33, ...).
                    chart_rows = []
                    for wk in sorted_weeks:
                        wk_hc = weeks_summary[wk]['hc']
                        wk_upl_trend = round((weeks_summary[wk]['upl'] / wk_hc) * 100, 2) if wk_hc > 0 else 0
                        wk_pl_trend = round((weeks_summary[wk]['pl'] / wk_hc) * 100, 2) if wk_hc > 0 else 0
                        wk_label = f'Week {wk}'
                        chart_rows.append({'Week': wk_label, 'Metric': 'Unplanned Leave', 'Actual %': wk_upl_trend})
                        chart_rows.append({'Week': wk_label, 'Metric': 'Planned Leave', 'Actual %': wk_pl_trend})

                    trend_df = pd.DataFrame(chart_rows)
                    week_order = [f'Week {wk}' for wk in sorted_weeks]
                    metric_colors = alt.Scale(
                        domain=['Planned Leave', 'Unplanned Leave'],
                        range=['#3b82f6', '#f97316']
                    )

                    base = alt.Chart(trend_df).encode(
                        x=alt.X('Week:N', sort=week_order, title=None),
                        xOffset=alt.XOffset('Metric:N'),
                    )

                    trend_bars = base.mark_bar(size=22, opacity=0.55).encode(
                        y=alt.Y('Actual %:Q', title='Actual %'),
                        color=alt.Color('Metric:N', scale=metric_colors, legend=alt.Legend(
                            orient='bottom',
                            labelFontSize=11,
                            labelFontWeight='bold',
                            title=None
                        )),
                        tooltip=['Week', 'Metric', 'Actual %']
                    )

                    trend_line = base.mark_line(
                        point=alt.OverlayMarkDef(filled=True, size=70, stroke='white', strokeWidth=1.5),
                        strokeWidth=2.5,
                    ).encode(
                        y=alt.Y('Actual %:Q'),
                        color=alt.Color('Metric:N', scale=metric_colors, legend=None),
                        detail='Metric:N',
                    )

                    trend_labels = base.mark_text(
                        dy=-12, fontSize=10, fontWeight='bold'
                    ).encode(
                        y=alt.Y('Actual %:Q'),
                        text=alt.Text('Actual %:Q', format='.2f'),
                        color=alt.Color('Metric:N', scale=metric_colors, legend=None),
                    )

                    st.altair_chart(
                        (trend_bars + trend_line + trend_labels).properties(height=280),
                        use_container_width=True,
                    )

            if target_fallback_used:
                st.info(
                    "ℹ️ Target column not found in one or more UPL files for the selected "
                    "dates — used the default (3.50% UPL / 9.67% PL) for those days. "
                    "Add the Target values to the Dashboard sheet (cell N3 for UPL Target, "
                    "O3 for PL Target — with 'UPL Target' / 'PL Target' as labels in N2/O2) "
                    "to show this week's actual target instead."
                )

            if upl_missing_dates:
                st.warning(f"⚠️ Missing UPL files for: {', '.join(upl_missing_dates)}")

        st.markdown("</div>", unsafe_allow_html=True)

    # EXISTING MIS VIEWS
    else:
        if not final_df.empty:
            display_df = final_df.copy()

            if st.session_state.selected_view == "rep_mispunches":
                display_df = repeated_mispunches.copy()
            elif st.session_state.selected_view == "mispunches":
                display_df = mispunches.copy()
            elif st.session_state.selected_view == "defaulters":
                display_df = defaulters.copy()

            display_df.sort_values(by=["P.Soft ID", "Date"], inplace=True)

            st.subheader(f"📊 Results View ({len(display_df)} Records)")

            col_search, col_download = st.columns([7, 3])

            with col_search:
                search = st.text_input("🔍 Search Employee by Name or ID...")

            with col_download:
                st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
                csv_data = display_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download File",
                    data=csv_data,
                    file_name=f"compliance_report_{st.session_state.selected_view}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            if search and not display_df.empty and "Employee Name" in display_df.columns:
                display_df = display_df[
                    display_df["Employee Name"].astype(str).str.contains(search, case=False, na=False)
                    | display_df["P.Soft ID"].astype(str).str.contains(search, case=False, na=False)
                ]

            cols_to_drop = ["Issue Type"]
            if st.session_state.selected_view in ["defaulters", "rep_defaulters"]:
                cols_to_drop.append("Total Punches")
                cols_to_drop.extend([c for c in display_df.columns if "IN" in c or "OUT" in c])

            final_display_df = display_df.drop(
                columns=[c for c in cols_to_drop if c in display_df.columns]
            )

            try:
                selection_event = st.dataframe(
                    final_display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=380,
                    on_select="rerun",
                    selection_mode="single-row",
                )

                if (
                    selection_event
                    and len(selection_event.selection.rows) > 0
                    and "P.Soft ID" in final_display_df.columns
                ):
                    selected_idx = selection_event.selection.rows[0]
                    selected_id = final_display_df.iloc[selected_idx]["P.Soft ID"]
                    selected_name = final_display_df.iloc[selected_idx]["Employee Name"]
                    total_offenses = len(
                        final_display_df[final_display_df["P.Soft ID"] == selected_id]
                    )
                    st.info(
                        f"📌 **{selected_name}** (ID: {selected_id}) "
                        f"ki is list mein total **{total_offenses}** entries hain."
                    )

            except Exception:
                st.dataframe(
                    final_display_df,
                    use_container_width=True,
                    hide_index=True,
                    height=380,
                )
        else:
            st.info(
                f"📂 **No data reflected:** No valid attendance records "
                f"found for {selected_warehouse} in the selected date range."
            )

    # MISSING FILE WARNING
    all_missing = sorted(set(missing_files + upl_missing))
    if all_missing:
        st.warning(
            f"⚠️ Following dates have no data file for {selected_warehouse}: "
            + ", ".join(all_missing)
        )

else:
    # DEFAULT FEATURE CARDS
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            """
            <div class="feature-card fc-blue">
                <div style="font-size:20px;">📊</div>
                <div class="fc-title">Accurate Attendance</div>
                <div class="fc-text">Detect mispunches & anomalies</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="feature-card fc-orange">
                <div style="font-size:20px;">🛡️</div>
                <div class="fc-title">Policy Compliance</div>
                <div class="fc-text">Ensure workforce discipline</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            """
            <div class="feature-card fc-green">
                <div style="font-size:20px;">📈</div>
                <div class="fc-title">Smart Analytics</div>
                <div class="fc-text">Actionable intelligence</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            """
            <div class="feature-card fc-purple">
                <div style="font-size:20px;">👥</div>
                <div class="fc-title">Reliable Team</div>
                <div class="fc-text">Boost productivity</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ==========================================================
# FOOTER
# ==========================================================
st.markdown(
    "<hr style='border:none; border-top:1px solid #e2e8f0; margin:10px 0 6px 0;'>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center; color:#64748b; font-size:11px; font-weight:600; margin:0;'>"
    "Built for a smarter, stronger and compliant workplace"
    "</p>",
    unsafe_allow_html=True,
)
