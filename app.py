import streamlit as st
import pandas as pd
import numpy as np
import os

# -----------------------------------------------------------------------------
# CORE ROSTER CONFIGURATION LINK
# -----------------------------------------------------------------------------
ROSTER_FILE = "Name KEy Football APP.csv"

# -----------------------------------------------------------------------------
# LIGHTWEIGHT AGGIE ONYX STYLE (NO BLOCKED COMPONENT ASSETS)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Texas A&M Football Performance Portal", layout="wide")

st.markdown("""
    <style>
        .stApp {
            background-color: #111111;
            color: #EEEEEE;
        }
        h1 {
            color: #FFFFFF !important; font-family: 'Arial Black', Gadget, sans-serif;
            border-bottom: 4px solid #500000; padding-bottom: 12px; text-transform: uppercase; letter-spacing: 2px;
        }
        h2, h3, h4 { color: #FFFFFF !important; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 700; }
        [data-testid="stSidebar"] { background-color: #500000 !important; border-right: 3px solid #800000; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: #FFFFFF !important; font-weight: bold;
        }
        div.stMetric, div[data-testid="stMetricBlock"] {
            background-color: #1A1A1A !important; border: 2px solid #500000 !important;
            border-radius: 8px !important; padding: 18px !important;
        }
        div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 900 !important; font-size: 2.3rem !important; }
        div[data-testid="stMarkdownContainer"] p { color: #FFFFFF !important; }
        .stDataFrame, .dataframe { background-color: #1A1A1A !important; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MASTER ROSTER ENGINE INITIALIZATION
# -----------------------------------------------------------------------------
@st.cache_data
def load_base_roster():
    if not os.path.exists(ROSTER_FILE):
        return None
    try:
        df = pd.read_csv(ROSTER_FILE)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.rename(columns={'Name': 'Player', 'POS': 'Position', 'Skill': 'Position Group'})
        return df[['Player', 'Position', 'Position Group']]
    except:
        return None

def process_uploaded_metrics(file_source):
    try:
        if file_source.name.endswith('.csv'):
            df_raw = pd.read_csv(file_source, header=None, nrows=25)
        else:
            df_raw = pd.read_excel(file_source, header=None, nrows=25)
            
        header_idx = 0
        for idx, row in df_raw.iterrows():
            row_vals = [str(x).lower().strip() for x in row.dropna().values]
            if 'player name' in row_vals or 'player' in row_vals:
                header_idx = idx
                break
                
        file_source.seek(0)
        if file_source.name.endswith('.csv'):
            df = pd.read_csv(file_source, skiprows=header_idx)
        else:
            df = pd.read_excel(file_source, skiprows=header_idx)
            
        df.columns = [str(c).strip() for c in df.columns]
        
        if 'Period Name' in df.columns:
            df = df[df['Period Name'].str.lower().str.strip() == 'session']
            
        rename_map = {}
        for col in df.columns:
            c_low = col.lower()
            if c_low in ['player name', 'name', 'athlete', 'player']: rename_map[col] = 'Player'
            elif 'total distance' in c_low or (c_low == 'distance' and 'band' not in c_low): rename_map[col] = 'Total Distance'
            elif 'explosive yardage' in c_low or 'explosive yardage (fsu)' in c_low: rename_map[col] = 'Explosive Yardage'
            elif 'total player load' in c_low or c_low == 'player load': rename_map[col] = 'Player Load'
            elif 'max speed' in c_low: rename_map[col] = 'Max Speed'
            
        df = df.rename(columns=rename_map)
        
        numeric_cols = ['Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed']
        for nc in numeric_cols:
            if nc in df.columns:
                df[nc] = pd.to_numeric(df[nc], errors='coerce').fillna(0.0)
            else:
                df[nc] = 0.0
                
        if df['Total Distance'].mean() < 2500 and df['Total Distance'].mean() > 0:
            df['Total Distance'] = (df['Total Distance'] * 1.09361).round(1)
            df['Explosive Yardage'] = (df['Explosive Yardage'] * 1.09361).round(1)
            
        return df[['Player', 'Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed']]
    except:
        return None

# -----------------------------------------------------------------------------
# CORE PIPELINE PIPELINE EXECUTION
# -----------------------------------------------------------------------------
st.sidebar.title("Aggie System Control")

master_roster = load_base_roster()

if master_roster is None:
    st.sidebar.error(f"⚠️ Master roster file '{ROSTER_FILE}' not detected.")
    st.stop()

gps_df = master_roster.copy()
for col in ['Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed']:
    gps_df[col] = 0.0

uploaded_session = st.sidebar.file_uploader("Upload Daily Session Report:", type=["csv", "xlsx"])

if uploaded_session is not None:
    session_metrics = process_uploaded_metrics(uploaded_session)
    if session_metrics is not None and len(session_metrics) > 0:
        gps_df['Match_Key'] = gps_df['Player'].astype(str).str.strip().str.upper()
        session_metrics['Match_Key'] = session_metrics['Player'].astype(str).str.strip().str.upper()
        
        # CRITICAL REWRITE FIX: Reference join variables explicitly by string parameters instead of raw dataframe tracking vectors
        merged_df = gps_df.merge(session_metrics[['Match_Key', 'Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed']], on='Match_Key', how='left', suffixes=('', '_new'))
        
        gps_df['Total Distance'] = merged_df['Total Distance_new'].fillna(0.0)
        gps_df['Explosive Yardage'] = merged_df['Explosive Yardage_new'].fillna(0.0)
        gps_df['Player Load'] = merged_df['Player Load_new'].fillna(0.0)
        gps_df['Max Speed'] = merged_df['Max Speed'].fillna(0.0)
        
        st.sidebar.success(f"⚡ Session Applied: {len(session_metrics)} Athletes Synced")
    else:
        st.sidebar.error("⚠️ Formatting Warning: File alignment mismatch.")

# Clean metric baselines
gps_df['Total Distance'] = gps_df['Total Distance'].fillna(0.0)
gps_df['Explosive Yardage'] = gps_df['Explosive Yardage'].fillna(0.0)
gps_df['Player Load'] = gps_df['Player Load'].fillna(0.0)
gps_df['Max Speed'] = gps_df['Max Speed'].fillna(0.0)
gps_df['Jump Height'] = 15.4
gps_df['mRSI'] = 0.61

# Page Navigation Layout Component
page = st.sidebar.radio("Select Portal Dashboard Module View:", [
    "Page 1: Daily Team Monitor",
    "Page 2: Positional Breakdowns"
])

# --- PAGE 1: DAILY TEAM MONITOR ---
if page == "Page 1: Daily Team Monitor":
    st.title("👍 Texas A&M Football Performance Hub")
    st.markdown("### Master Roster Workload Panel | Active Volume Tracking")
    st.divider()
    
    pos_opts = list(gps_df['Position Group'].unique())
    selected_groups = st.multiselect("Filter Roster Segmentations:", pos_opts, default=pos_opts)
    display_df = gps_df[gps_df['Position Group'].isin(selected_groups)]
    
    st.dataframe(display_df[['Player', 'Position', 'Position Group', 'Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed', 'Jump Height', 'mRSI']], use_container_width=True, hide_index=True)

# --- PAGE 2: POSITIONAL BREAKDOWNS ---
elif page == "Page 2: Positional Breakdowns":
    st.title("🎯 Positional Architecture Performance Tiers")
    st.divider()
    
    for group in ['Skill', 'Mid', 'Big']:
        st.markdown(f"## **{group.upper()} UNIT LEADERBOARD**")
        g_df = gps_df[gps_df['Position Group'] == group]
        st.dataframe(g_df[['Player', 'Position', 'Total Distance', 'Explosive Yardage', 'Max Speed']].sort_values(by='Explosive Yardage', ascending=False), use_container_width=True, hide_index=True)
