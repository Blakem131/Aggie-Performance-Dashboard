import streamlit as st
import pandas as pd
import numpy as np
import base64
import os

# -----------------------------------------------------------------------------
# CORE ROSTER CONFIGURATION BLOCK
# -----------------------------------------------------------------------------
ROSTER_FILE = "Name KEy Football APP.csv"

# -----------------------------------------------------------------------------
# PREMIUM AGGIE ONYX DARK MODE STYLING & IMAGE RENDERING
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Texas A&M Football Performance Portal", layout="wide")

def get_base64_img(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

bg_base64 = get_base64_img("Indoor.jpg")      
logo_base64 = get_base64_img("A&M alt.png")    

st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(rgba(17, 17, 17, 0.90), rgba(17, 17, 17, 0.90)), 
                        url("data:image/jpeg;base64,{bg_base64}") no-repeat center center fixed;
            background-size: cover;
            color: #EEEEEE;
        }}
        .aggie-floating-logo {{
            position: fixed; top: 20px; right: 40px; width: 140px; opacity: 0.25; z-index: 999; pointer-events: none;
        }}
        h1 {{
            color: #FFFFFF !important; font-family: 'Arial Black', Gadget, sans-serif;
            border-bottom: 4px solid #500000; padding-bottom: 12px; text-transform: uppercase; letter-spacing: 2px;
        }}
        h2, h3, h4 {{ color: #FFFFFF !important; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 700; }}
        [data-testid="stSidebar"] {{ background-color: rgba(80, 0, 0, 0.95) !important; border-right: 3px solid #800000; }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
            color: #FFFFFF !important; font-weight: bold;
        }}
        div.stMetric, div[data-testid="stMetricBlock"] {{
            background-color: rgba(20, 20, 20, 0.80) !important; border: 2px solid #500000 !important;
            border-radius: 8px !important; padding: 18px !important; backdrop-filter: blur(5px);
        }}
        div[data-testid="stMetricValue"] {{ color: #FFFFFF !important; font-weight: 900 !important; font-size: 2.3rem !important; }}
        div[data-testid="stMarkdownContainer"] p {{ color: #FFFFFF !important; }}
        .stDataFrame, .dataframe {{ background-color: rgba(20, 20, 20, 0.85) !important; border-radius: 6px; backdrop-filter: blur(5px); }}
    </style>
""", unsafe_allow_html=True)

if logo_base64:
    st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="aggie-floating-logo">', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MASTER INTEGRATION LOADER
# -----------------------------------------------------------------------------
@st.cache_data
def load_baseline_roster():
    if not os.path.exists(ROSTER_FILE):
        return None
    try:
        df = pd.read_csv(ROSTER_FILE)
        # Ensure naming structures map perfectly to what you provided
        df.columns = [str(c).strip() for c in df.columns]
        df = df.rename(columns={'Name': 'Player', 'POS': 'Position', 'Skill': 'Position Group'})
        
        # Add baseline metric columns so the tables load cleanly right out of the box
        df['Total Distance'] = 0.0
        df['Explosive Yardage'] = 0.0
        df['Player Load'] = 0.0
        df['Max Speed'] = 0.0
        df['Jump Height'] = 15.0
        df['mRSI'] = 0.60
        df['ACWR'] = 1.00
        df['Jump_Delta_%'] = 0.0
        return df
    except:
        return None

# -----------------------------------------------------------------------------
# INTERFACE MAIN COMPONENT CONTROL
# -----------------------------------------------------------------------------
st.sidebar.title("Aggie System Control")

gps_df = load_baseline_roster()

if gps_df is not None:
    st.sidebar.success(f"📋 Roster Master Framework Loaded\n({len(gps_df)} Athletes Active)")
else:
    st.sidebar.error(f"⚠️ Error: Could not find '{ROSTER_FILE}' in your repository repository paths.")
    st.stop()

# Generate dummy progression values so Page 3 graphs don't crash
dates_5w = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
history_records = []
for idx, row in gps_df.iterrows():
    for w_name in dates_5w:
        history_records.append({
            'Player': row['Player'], 'Week': w_name,
            'Jump Height History': 15.0, 'Total Distance History': 0.0, 'mRSI History': 0.60
        })
history_df = pd.DataFrame(history_records)

# Navigation Menu Options
page = st.sidebar.radio("Select Portal Dashboard Module View:", [
    "Page 1: Daily Team Monitor",
    "Page 2: Positional Breakdowns",
    "Page 3: Individual Athlete Diagnostic"
])

# --- PAGE 1: DAILY TEAM MONITOR ---
if page == "Page 1: Daily Team Monitor":
    st.title("👍 Texas A&M Football Performance Hub")
    st.markdown("### Team Roster Master Verification Grid")
    st.divider()
    
    pos_opts = list(gps_df['Position Group'].unique())
    selected_groups = st.multiselect("Filter Roster Segmentations:", pos_opts, default=pos_opts)
    display_df = gps_df[gps_df['Position Group'].isin(selected_groups)]
    
    st.dataframe(display_df[['Player', 'Position', 'Position Group', 'Total Distance', 'Explosive Yardage', 'Player Load', 'Jump Height', 'mRSI']], use_container_width=True, hide_index=True)

# --- PAGE 2: POSITIONAL BREAKDOWNS ---
elif page == "Page 2: Positional Breakdowns":
    st.title("🎯 Positional Architecture Performance Tiers")
    st.divider()
    
    for group in ['Skill', 'Mid', 'Big']:
        st.markdown(f"## **{group.upper()} UNIT LEADERBOARD**")
        g_df = gps_df[gps_df['Position Group'] == group]
        st.dataframe(g_df[['Player', 'Position', 'Total Distance', 'Explosive Yardage', 'Max Speed']], use_container_width=True, hide_index=True)

# --- PAGE 3: INDIVIDUAL ATHLETE DIAGNOSTIC ---
elif page == "Page 3: Individual Athlete Diagnostic":
    st.title("👤 Individual Athlete Profile Diagnostics")
    st.divider()
    selected_p = st.selectbox("Select Target Athlete Profile Panel:", gps_df['Player'].tolist())
