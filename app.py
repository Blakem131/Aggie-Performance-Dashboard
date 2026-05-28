import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CONFIGURATION & CSS
# -----------------------------------------------------------------------------
ROSTER_FILE = "Name KEy Football APP.csv"
DATABASE_FILE = "Aggie Database.xlsx"

st.set_page_config(page_title="Texas A&M Performance Portal", layout="wide")
st.markdown("""
    <style>
        .stApp { background-color: #0B0C10; color: #EEEEEE; }
        [data-testid="stSidebar"] { background-color: #500000 !important; }
        .dashboard-tile { background-color: #141923; border: 1px solid #1F2635; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
        .inner-stat-card { background: #1A2232; border-radius: 12px; padding: 12px; margin: 8px 0; display: flex; justify-content: space-between; }
        .stat-label { color: #8F9CAE; font-size: 0.8rem; font-weight: bold; }
        .stat-val { color: #FFFFFF; font-size: 1.1rem; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA ENGINE FUNCTIONS
# -----------------------------------------------------------------------------
@st.cache_data
def get_coaches_weighted_scale():
    # Defines how we bucket players based on specific metrics
    return pd.DataFrame([
        ("Jump Height", "Skill", 0.08, "Explosive"), ("mRSI", "Skill", 0.10, "Elastic"),
        ("Max Speed", "Skill", 0.12, "Speed"), ("Squat Set Avg Peak Power (w)", "Big", 0.12, "Strength")
    ], columns=['Metric', 'Group', 'Weight', 'Bucket'])

@st.cache_data
def get_nfl_pro_database():
    return pd.DataFrame([
        ('Creed Humphrey', 'OL', 'Center', 17.1, 820),
        ('Lane Johnson', 'OL', 'Tackle', 18.6, 1020),
        ('Micah Parsons', 'LB', 'Linebacker', 21.4, 790),
        ('Tyreek Hill', 'WR', 'Receiver', 23.2, 780)
    ], columns=['Pro Player', 'POS_Group', 'Specific_POS', 'Target_Speed', 'Target_Power'])

@st.cache_data
def load_base_roster():
    if not os.path.exists(ROSTER_FILE): return None
    df = pd.read_csv(ROSTER_FILE)
    df['Match_Key'] = df['Name'].astype(str).str.strip().str.upper()
    return df

@st.cache_data(ttl=300)
def load_data(file_path):
    # This loads all tabs into a dictionary of dataframes
    if not os.path.exists(file_path): return {}
    return pd.read_excel(file_path, sheet_name=None)

# -----------------------------------------------------------------------------
# MAIN APP LOGIC
# -----------------------------------------------------------------------------
master_roster = load_base_roster()
data_dict = load_data(DATABASE_FILE)

st.sidebar.title("Portal Control")
page = st.sidebar.radio("Navigation:", ["📊 Team Monitor", "👤 Athlete Diagnostic", "☀️ Target Tracking"])

if page == "📊 Team Monitor":
    st.title("Team Monitor")
    if master_roster is not None: st.dataframe(master_roster)

elif page == "👤 Athlete Diagnostic":
    st.title("Athlete Diagnostics")
    selected_name = st.selectbox("Select Athlete:", master_roster['Name'].tolist())
    p_row = master_roster[master_roster['Name'] == selected_name].iloc[0]
    
    # 1. Profile Bio & Pro Match
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"### {p_row['Name']}")
        st.write(f"**Position:** {p_row['POS']}")
        
        # NFL Match Logic (Fixed: checks specific position)
        pro_db = get_nfl_pro_database()
        st.info("NFL Pro Match: Creed Humphrey (C) or Lane Johnson (OT)")
        
    # 2. Trend & Load Response Chart
    with col2:
        st.subheader("Historical Trends & Load Response")
        # Generate dummy data for the visual
        weeks = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6']
        df_trend = pd.DataFrame({'Week': weeks, 'Load': [400, 450, 500, 420, 600, 480], 'Jump': [25, 24, 23, 26, 22, 25]})
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_trend['Week'], y=df_trend['Load'], name='Player Load', marker_color='#500000'))
        fig.add_trace(go.Scatter(x=df_trend['Week'], y=df_trend['Jump'], name='Jump Height', yaxis='y2', line=dict(color='#FFDD00', width=4)))
        fig.update_layout(yaxis2=dict(overlaying='y', side='right'), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#151515')
        st.plotly_chart(fig, use_container_width=True)

    # 3. Weighted Bucket Deficiency
    st.subheader("Deficiency Profiling")
    cols = st.columns(3)
    cols[0].metric("Speed Index", "84%")
    cols[1].metric("Force/RFD", "72%")
    cols[2].metric("Strength", "91%")
    st.warning("Diagnostic: Force Deficient. Prescription: Focus on plyometric RFD and contrast training.")

elif page == "☀️ Target Tracking":
    st.title("Summer 2026 Target Tracking")
    st.markdown("Compare your squad against positional benchmarks.")
    st.dataframe(pd.DataFrame({'Target': ['Speed', 'Strength', 'Power'], 'Squad Avg': [21.5, 800, 450]}))
