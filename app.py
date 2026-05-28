import streamlit as st
import pandas as pd
import os

# -----------------------------------------------------------------------------
# GLOBAL CONFIG & CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Athlete OS", layout="wide")
st.markdown("""
    <style>
        .stApp { background-color: #050A14; color: #E0E0E0; font-family: 'Roboto', sans-serif; }
        [data-testid="stSidebar"] { background-color: #0B1220 !important; border-right: 1px solid #1A2840; }
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            background-color: #1A2840 !important; color: #FFFFFF !important; font-weight: 700;
            padding: 12px !important; margin-bottom: 8px !important; border-radius: 6px !important;
        }
        .os-header { font-size: 28px; font-weight: 900; color: #FFFFFF; text-transform: uppercase; border-bottom: 3px solid #00F2FF; padding-bottom: 10px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# NAVIGATION (MUST BE FIRST)
# -----------------------------------------------------------------------------
st.sidebar.title("PORTAL CONTROL")
page = st.sidebar.radio("NAVIGATION:", [
    "📊 TEAM MONITOR", 
    "🎯 POSITIONAL BREAKDOWNS", 
    "👤 ATHLETE DASHBOARD", 
    "☀️ TARGET TRACKING", 
    "⏱️ PRACTICE PLANNER"
])

# -----------------------------------------------------------------------------
# PAGE LOGIC (NOW SAFELY BELOW NAVIGATION)
# -----------------------------------------------------------------------------
if page == "👤 ATHLETE DASHBOARD":
    st.markdown('<div class="os-header">ATHLETE DASHBOARD</div>', unsafe_allow_html=True)
    st.write("Dashboard content will go here.")

elif page == "📊 TEAM MONITOR":
    st.title("TEAM MONITOR")

elif page == "🎯 POSITIONAL BREAKDOWNS":
    st.title("POSITIONAL BREAKDOWNS")

elif page == "☀️ TARGET TRACKING":
    st.title("TARGET TRACKING")

elif page == "⏱️ PRACTICE PLANNER":
    st.title("PRACTICE PLANNER")
