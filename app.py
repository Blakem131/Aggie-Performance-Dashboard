import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CONFIG & CSS (UI Theme: Screenshot 2026-05-28 115857.png)
# -----------------------------------------------------------------------------
ROSTER_FILE = "Name KEy Football APP.csv"
DATABASE_FILE = "Aggie Database.xlsx"

st.set_page_config(page_title="Texas A&M Performance Portal", layout="wide")
st.markdown("""
    <style>
        .stApp { background-color: #0B0C10; color: #EEEEEE; }
        [data-testid="stSidebar"] { background-color: #500000 !important; }
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            background-color: #3D0000 !important; border: 1px solid #660000 !important; border-radius: 12px !important;
            padding: 14px 18px !important; margin-bottom: 10px !important; width: 100% !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background-color: #700000 !important; border-color: #FFFFFF !important; }
        .dashboard-tile { background-color: #141923; border: 1px solid #1F2635; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
        .inner-stat-card { background: #1A2232; border-radius: 12px; padding: 12px; margin: 8px 0; display: flex; justify-content: space-between; }
        .stat-label { color: #8F9CAE; font-size: 0.8rem; font-weight: bold; }
        .stat-val { color: #FFFFFF; font-size: 1.1rem; font-weight: 800; }
        .delta-positive { color: #00CC66; font-weight: bold; }
        .delta-negative { color: #FF3333; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA ENGINE
# -----------------------------------------------------------------------------
@st.cache_data
def get_weighted_scale():
    return pd.DataFrame([
        ("Jump Height", "Skill", 0.08, "Explosive"), ("mRSI", "Skill", 0.10, "Elastic"),
        ("Max Speed", "Skill", 0.12, "Speed"), ("Squat Set Avg Peak Power (w)", "Big", 0.12, "Strength")
    ], columns=['Metric', 'Group', 'Weight', 'Bucket'])

@st.cache_data
def load_base_roster():
    if not os.path.exists(ROSTER_FILE): return None
    df = pd.read_csv(ROSTER_FILE)
    df['Match_Key'] = df['Name'].astype(str).str.strip().str.upper()
    return df

@st.cache_data(ttl=300)
def load_excel_data():
    if not os.path.exists(DATABASE_FILE): return {}
    return pd.read_excel(DATABASE_FILE, sheet_name=None)

# -----------------------------------------------------------------------------
# MAIN APP LOGIC
# -----------------------------------------------------------------------------
master_roster = load_base_roster()
data_dict = load_excel_data()

st.sidebar.title("Portal Control")
page = st.sidebar.radio("Navigation:", [
    "📊 Team Monitor", "🎯 Positional Breakdowns", 
    "👤 Athlete Diagnostic", "☀️ Target Tracking", "⏱️ Practice Planner"
])

if page == "📊 Team Monitor":
    st.title("Team Monitor")
    if master_roster is not None: st.dataframe(master_roster)

elif page == "🎯 Positional Breakdowns":
    st.title("Positional Breakdowns")
    st.write("Unit-level performance analysis.")

elif page == "👤 Athlete Diagnostic":
    st.title("Athlete Diagnostics")
    name = st.selectbox("Select Athlete:", master_roster['Name'].tolist())
    p_row = master_roster[master_roster['Name'] == name].iloc[0]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"### {p_row['Name']}")
        st.write(f"**Position:** {p_row['POS']}")
        
    with col2:
        st.subheader("Dual-Axis Longitudinal Tracker")
        # Example dual-axis setup
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['W1', 'W2', 'W3'], y=[400, 500, 420], name='Load', marker_color='#500000'))
        fig.add_trace(go.Scatter(x=['W1', 'W2', 'W3'], y=[25, 24, 26], name='Jump', yaxis='y2', line=dict(color='#FFDD00', width=4)))
        fig.update_layout(yaxis2=dict(overlaying='y', side='right'), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#151515')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Deficiency Profiling")
    cols = st.columns(3)
    cols[0].metric("Speed Index", "84%")
    cols[1].metric("Force/RFD", "72%")
    cols[2].metric("Strength", "91%")
    st.warning("Diagnostic: Force Deficient. Prescription: Focus on plyometric RFD and contrast training.")

elif page == "☀️ Target Tracking":
    st.title("Summer 2026 Target Tracking")
    # Dashboard Tiles
    row1 = st.columns(3)
    row1[0].markdown('<div class="dashboard-tile"><h4>🏃 SPEED</h4><div class="inner-stat-card"><span class="stat-label">Max Vel</span><span class="stat-val">22.1</span></div></div>', unsafe_allow_html=True)
    row1[1].markdown('<div class="dashboard-tile"><h4>⚡ EXPLOSIVE</h4><div class="inner-stat-card"><span class="stat-label">Jump Ht</span><span class="stat-val">32.5</span></div></div>', unsafe_allow_html=True)
    row1[2].markdown('<div class="dashboard-tile"><h4>🏋️ STRENGTH</h4><div class="inner-stat-card"><span class="stat-label">Sq Pwr</span><span class="stat-val">850</span></div></div>', unsafe_allow_html=True)

elif page == "⏱️ Practice Planner":
    st.title("Practice Planner")
