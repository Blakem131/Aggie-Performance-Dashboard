import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# -----------------------------------------------------------------------------
# GLOBAL CONFIG & CSS (Matched to your Mockup Colors)
# -----------------------------------------------------------------------------
ROSTER_FILE = "Name KEy Football APP.csv"

st.set_page_config(page_title="Athlete OS", layout="wide")
st.markdown("""
    <style>
        .stApp { background-color: #f6f7f9; color: #17191c; font-family: 'DejaVu Sans', sans-serif; }
        [data-testid="stSidebar"] { background-color: #14171a !important; }
        
        .os-tile { background-color: #ffffff; border: 1px solid #d9dde3; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .os-header { font-size: 28px; font-weight: bold; color: #17191c; text-transform: uppercase; border-bottom: 3px solid #500000; padding-bottom: 10px; margin-bottom: 20px; }
        
        .metric-card { background: #ffffff; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #d9dde3; }
        .metric-val { font-size: 32px; font-weight: bold; color: #17191c; }
        .metric-label { font-size: 12px; color: #68707a; text-transform: uppercase; font-weight: bold; }
        
        .analysis-box { background: #f6f7f9; border-left: 4px solid #145da0; padding: 15px; margin-top: 15px; color: #17191c; font-style: italic; }
        h4 { color: #68707a !important; font-size: 14px !important; text-transform: uppercase; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

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
    # 1. HEADER
    st.markdown('<div class="os-header">ATHLETE DASHBOARD</div>', unsafe_allow_html=True)
    
    # Selection
    st.selectbox("SELECT ATHLETE:", ["Trovon Baugh"]) # Placeholder
    
    # 2. METRIC CARDS
    row0 = st.columns(4)
    indices = [("SPEED INDEX", "94"), ("FORCE INDEX", "81"), ("STRENGTH INDEX", "77"), ("POWER INDEX", "91")]
    for i, col in enumerate(row0):
        col.markdown(f'<div class="metric-card"><div class="metric-val">{indices[i][1]}</div><div class="metric-label">{indices[i][0]}</div></div>', unsafe_allow_html=True)
            
    # 3. MID-SECTION
    row1 = st.columns([1, 2, 2])
    
    with row1[0]:
        st.markdown('<div class="os-tile"><h4>READINESS ENGINE</h4><p style="font-size:42px; font-weight:bold; color:#2fa84f; text-align:center;">82%</p></div>', unsafe_allow_html=True)
        st.markdown('<h4>Readiness Analysis</h4><div class="analysis-box">Alert: Acute to Chronic workload spike detected (Ratio: 1.5) in Total Distance. Suggesting deload.</div>', unsafe_allow_html=True)
    
    with row1[1]:
        st.markdown('<div class="os-tile"><h4>PERFORMANCE TRENDS</h4></div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=['W1', 'W2', 'W3', 'W4'], y=[25, 27, 28, 34], line=dict(color='#145da0', width=4)))
        fig.update_layout(height=200, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with row1[2]:
        st.markdown('<div class="os-tile"><h4>ATHLETIC PROFILE</h4></div>', unsafe_allow_html=True)
        fig_r = go.Figure(go.Scatterpolar(r=[90, 80, 85, 70, 95], theta=['Speed', 'Strength', 'Power', 'Force', 'Elastic'], fill='toself', fillcolor='rgba(80, 0, 0, 0.2)', line_color='#500000'))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#d9dde3'), bgcolor='#ffffff'), height=200, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_r, use_container_width=True)

# ... (Include other pages below as needed)
