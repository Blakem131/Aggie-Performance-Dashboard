import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# -----------------------------------------------------------------------------
# CONFIG & "ATHLETE OS" CSS
# -----------------------------------------------------------------------------
ROSTER_FILE = "Name KEy Football APP.csv"

st.set_page_config(page_title="Athlete OS", layout="wide")
st.markdown("""
    <style>
        .stApp { background-color: #050A14; color: #E0E0E0; font-family: 'Roboto', sans-serif; }
        [data-testid="stSidebar"] { background-color: #0B1220 !important; border-right: 1px solid #1A2840; }
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            background-color: #1A2840 !important; color: #FFFFFF !important; font-weight: 700;
            padding: 12px !important; margin-bottom: 8px !important; border-radius: 6px !important;
        }
        .os-tile { background-color: #0B1220; border: 1px solid #1A2840; border-radius: 8px; padding: 20px; margin-bottom: 15px; }
        .os-header { font-size: 28px; font-weight: 900; color: #FFFFFF; text-transform: uppercase; border-bottom: 3px solid #00F2FF; padding-bottom: 10px; margin-bottom: 20px; }
        .metric-card { background: #0F172A; padding: 15px; border-radius: 6px; text-align: center; border: 1px solid #1E293B; }
        .metric-val { font-size: 32px; font-weight: 900; color: #00F2FF; }
        .metric-label { font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: bold; }
        h4 { color: #94A3B8 !important; font-size: 14px !important; text-transform: uppercase; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA LOADING
# -----------------------------------------------------------------------------
@st.cache_data
def load_base_roster():
    if not os.path.exists(ROSTER_FILE): return pd.DataFrame()
    return pd.read_csv(ROSTER_FILE)

master_roster = load_base_roster()

# -----------------------------------------------------------------------------
# NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.title("PORTAL CONTROL")
page = st.sidebar.radio("NAVIGATION:", [
    "📊 TEAM MONITOR", "🎯 POSITIONAL BREAKDOWNS", 
    "👤 ATHLETE DASHBOARD", "☀️ TARGET TRACKING", "⏱️ PRACTICE PLANNER"
])

# -----------------------------------------------------------------------------
# PAGE: ATHLETE DASHBOARD
# -----------------------------------------------------------------------------
if page == "👤 ATHLETE DASHBOARD":
    if not master_roster.empty:
        # Header Selection
        name = st.selectbox("SELECT ATHLETE:", master_roster['Name'].tolist())
        p_row = master_roster[master_roster['Name'] == name].iloc[0]
        
        # 1. HEADER
        st.markdown(f'<div class="os-header">{p_row["Name"]} // {p_row["POS"]} // Texas A&M Football</div>', unsafe_allow_html=True)
        
        # 2. KEY PERFORMANCE INDICES (Top Row)
        row0 = st.columns(4)
        indices = [("SPEED INDEX", "94"), ("FORCE INDEX", "81"), ("STRENGTH INDEX", "77"), ("POWER INDEX", "91")]
        for i, col in enumerate(row0):
            col.markdown(f'<div class="metric-card"><div class="metric-val">{indices[i][1]}</div><div class="metric-label">{indices[i][0]}</div></div>', unsafe_allow_html=True)
            
        # 3. MID-SECTION (Readiness, Trends, Spider)
        row1 = st.columns([1, 2, 2])
        
        with row1[0]:
            st.markdown('<div class="os-tile"><h4>Readiness Engine</h4><p style="font-size:42px; font-weight:900; color:#00FF00; text-align:center;">82%</p></div>', unsafe_allow_html=True)
        
        with row1[1]:
            st.markdown('<div class="os-tile"><h4>Performance Trends</h4></div>', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=['W1', 'W2', 'W3', 'W4'], y=[25, 27, 28, 34], line=dict(color='#00F2FF', width=4)))
            fig.update_layout(height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with row1[2]:
            st.markdown('<div class="os-tile"><h4>Athletic Profile</h4></div>', unsafe_allow_html=True)
            fig_r = go.Figure(go.Scatterpolar(r=[90, 80, 85, 70, 95], theta=['Speed', 'Strength', 'Power', 'Force', 'Elastic'], fill='toself', fillcolor='rgba(0, 242, 255, 0.2)', line_color='#00F2FF'))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#1E293B'), bgcolor='#0B1220'), height=200, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig_r, use_container_width=True)
    else:
        st.error("Roster file missing.")

# -----------------------------------------------------------------------------
# PLACEHOLDER PAGES (To maintain structure)
# -----------------------------------------------------------------------------
elif page == "📊 TEAM MONITOR":
    st.title("TEAM MONITOR")
elif page == "🎯 POSITIONAL BREAKDOWNS":
    st.title("POSITIONAL BREAKDOWNS")
elif page == "☀️ TARGET TRACKING":
    st.title("TARGET TRACKING")
elif page == "⏱️ PRACTICE PLANNER":
    st.title("PRACTICE PLANNER")
