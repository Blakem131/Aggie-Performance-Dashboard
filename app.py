import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# -----------------------------------------------------------------------------
# CONFIG & "MIDNIGHT AGGIE" CSS THEME
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
            color: #FFFFFF !important; font-weight: bold;
        }
        .dashboard-tile { background-color: #141923; border: 1px solid #1F2635; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
        .inner-stat-card { background: #1A2232; border-radius: 12px; padding: 12px; margin: 8px 0; display: flex; justify-content: space-between; }
        .stat-label { color: #8F9CAE; font-size: 0.9rem; font-weight: bold; }
        .stat-val { color: #FFD700; font-size: 1.4rem; font-weight: 900; }
        h1, h2, h3 { color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ENGINE FUNCTIONS
# -----------------------------------------------------------------------------
@st.cache_data
def get_weighted_scale():
    return pd.DataFrame([
        ("Jump Height", "Skill", 0.08, "Explosive"), ("mRSI", "Skill", 0.10, "Elastic"),
        ("Max Speed", "Skill", 0.12, "Speed"), ("Squat Set Avg Peak Power (w)", "Big", 0.12, "Strength")
    ], columns=['Metric', 'Group', 'Weight', 'Bucket'])

@st.cache_data
def load_base_roster():
    if not os.path.exists(ROSTER_FILE): return pd.DataFrame()
    df = pd.read_csv(ROSTER_FILE)
    df['Match_Key'] = df['Name'].astype(str).str.strip().str.upper()
    return df

# -----------------------------------------------------------------------------
# MAIN DASHBOARD LOGIC
# -----------------------------------------------------------------------------
master_roster = load_base_roster()
st.sidebar.title("Portal Control")
page = st.sidebar.radio("Navigation:", [
    "📊 Team Monitor", "🎯 Positional Breakdowns", 
    "👤 Athlete Diagnostic", "☀️ Target Tracking", "⏱️ Practice Planner"
])

if page == "📊 Team Monitor":
    st.title("Team Monitor")
    if not master_roster.empty: st.dataframe(master_roster)

elif page == "🎯 Positional Breakdowns":
    st.title("Positional Breakdowns")
    st.write("Unit-level performance analysis dashboard.")

elif page == "👤 Athlete Diagnostic":
    st.title("Athlete Diagnostics")
    name = st.selectbox("Select Athlete:", master_roster['Name'].tolist())
    p_row = master_roster[master_roster['Name'] == name].iloc[0]
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"### {p_row['Name']}")
        st.write(f"**Position:** {p_row['POS']}")
        
        # Deficiency Profiling (Bucketing Engine)
        st.subheader("Deficiency Profiling")
        st.markdown('<div class="dashboard-tile"><div class="inner-stat-card"><span class="stat-label">Speed Index</span><span class="stat-val">84%</span></div><div class="inner-stat-card"><span class="stat-label">Force/RFD</span><span class="stat-val">72%</span></div><div class="inner-stat-card"><span class="stat-label">Strength</span><span class="stat-val">91%</span></div></div>', unsafe_allow_html=True)
        st.warning("Diagnostic: Force Deficient. Prescription: Focus on plyometric RFD and contrast training.")

    with col2:
        # 1. SPIDER CHART (RESTORED)
        st.subheader("Performance Capacity Radar")
        fig_r = go.Figure(go.Scatterpolar(
            r=[80, 70, 90, 60, 75],
            theta=['Speed', 'Strength', 'Explosive', 'Elastic', 'Braking'],
            fill='toself', fillcolor='rgba(80, 0, 0, 0.5)', line_color='#FFD700'
        ))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=350, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_r, use_container_width=True)
        
        # 2. DUAL-AXIS LOAD RESPONSE
        st.subheader("Historical Load Response")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['W1', 'W2', 'W3', 'W4', 'W5', 'W6'], y=[400, 450, 500, 420, 600, 480], name='Load', marker_color='#500000'))
        fig.add_trace(go.Scatter(x=['W1', 'W2', 'W3', 'W4', 'W5', 'W6'], y=[25, 24, 23, 26, 22, 25], name='Jump', yaxis='y2', line=dict(color='#FFD700', width=4)))
        fig.update_layout(yaxis2=dict(overlaying='y', side='right'), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#151515')
        st.plotly_chart(fig, use_container_width=True)

elif page == "☀️ Target Tracking":
    st.title("Summer 2026 Target Tracking")
    # Grid Tiles from Screenshot
    row1 = st.columns(3)
    row1[0].markdown('<div class="dashboard-tile"><h4>🏃 SPEED</h4><div class="inner-stat-card"><span class="stat-label">Max Vel</span><span class="stat-val">22.1</span></div></div>', unsafe_allow_html=True)
    row1[1].markdown('<div class="dashboard-tile"><h4>⚡ EXPLOSIVE</h4><div class="inner-stat-card"><span class="stat-label">Jump Ht</span><span class="stat-val">32.5</span></div></div>', unsafe_allow_html=True)
    row1[2].markdown('<div class="dashboard-tile"><h4>🏋️ STRENGTH</h4><div class="inner-stat-card"><span class="stat-label">Sq Pwr</span><span class="stat-val">850</span></div></div>', unsafe_allow_html=True)

elif page == "⏱️ Practice Planner":
    st.title("Practice Planner")
