import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CORE CONFIGURATION FILE TARGETS
# -----------------------------------------------------------------------------
ROSTER_FILE = "Name KEy Football APP.csv"
DATABASE_FILE = "Aggie_Master_Database.xlsx"

# -----------------------------------------------------------------------------
# EXECUTIVE AGGIE ONYX STYLE DIRECTIVES
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Texas A&M Football Performance Portal", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #111111; color: #EEEEEE; }
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
# MASTER SAFE DATA PARSING LOADER
# -----------------------------------------------------------------------------
@st.cache_data
def load_base_roster():
    if not os.path.exists(ROSTER_FILE):
        return None
    try:
        df = pd.read_csv(ROSTER_FILE)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.rename(columns={'Name': 'Player', 'POS': 'Position', 'Skill': 'Position Group'})
        df['Match_Key'] = df['Player'].astype(str).str.strip().str.upper()
        return df[['Player', 'Position', 'Position Group', 'Match_Key']]
    except:
        return None

@st.cache_data(ttl=30)
def load_central_sheet_tab(xl_file, sheet_name, target_cols):
    try:
        if sheet_name not in xl_file.sheet_names:
            return pd.DataFrame()
            
        df = pd.read_excel(xl_file, sheet_name=sheet_name)
        df.columns = [str(c).strip() for c in df.columns]
        
        rename_map = {}
        for col in df.columns:
            c_low = col.lower().strip()
            if c_low in ['name', 'player', 'athlete', 'player name']: 
                rename_map[col] = 'Player'
            elif c_low in ['date', 'activity date', 'start date', 'day']: 
                rename_map[col] = 'Date'
            else:
                for tc in target_cols:
                    if c_low == tc.lower().strip():
                        rename_map[col] = tc
                        
        df = df.rename(columns=rename_map)
        if 'Player' not in df.columns:
            return pd.DataFrame()
            
        df['Match_Key'] = df['Player'].astype(str).str.strip().str.upper()
        
        if 'Date' in df.columns:
            df['Date'] = df['Date'].astype(str).str.split().str[0].str.strip()
        else:
            df['Date'] = "Manual Entry"
        
        for tc in target_cols:
            if tc in df.columns:
                df[tc] = pd.to_numeric(df[tc], errors='coerce').fillna(0.0)
            else:
                df[tc] = 0.0
                
        pull_cols = ['Match_Key', 'Date'] + [tc for tc in target_cols if tc in df.columns]
        return df[pull_cols]
    except:
        return pd.DataFrame()

# -----------------------------------------------------------------------------
# COORDINATE MASTER ROUTINES PIPELINE
# -----------------------------------------------------------------------------
st.sidebar.title("Aggie Portal Control")

master_roster = load_base_roster()
if master_roster is None:
    st.sidebar.error(f"⚠️ Roster base mapping '{ROSTER_FILE}' not found.")
    st.stop()

# Core Data Vault Column Definitions
gps_cols = ['Total Distance (y)', 'Total Player Load', 'Player Load Per Minute', 'IMA Total', 'Explosive Yardage', 'Max Speed (mph)', 'Max Vel (% Max)']
perch_cols = ['Mean Velocity (m/s)', 'Peak Velocity (m/s)', 'Peak Power (W)']
nord_cols = ['Max Left Force (N)', 'Max Right Force (N)', 'Total Force (N)', 'Imbalance (%)']
sprint_cols = ['Distance (m)', 'Peak Speed (mph)', 'Peak Power (W)', 'Avg Force (N)']
force_cols = ['Jump Height', 'mRSI']

unique_dates = []
selected_date = "System Simulation Mode"

if os.path.exists(DATABASE_FILE):
    try:
        xl = pd.ExcelFile(DATABASE_FILE)
        
        # Exact Hardcoded Sheet Name Locks Matching Desktop Labels Exactly
        df_gps = load_central_sheet_tab(xl, 'Catapult Data Dump', gps_cols)
        df_force = load_central_sheet_tab(xl, 'Hawkins Data Dump', force_cols)
        df_perch = load_central_sheet_tab(xl, 'Perch Data Dump', perch_cols)
        df_sprint = load_central_sheet_tab(xl, 'Sprint 1080 Data Dump', sprint_cols)
        df_nord = load_central_sheet_tab(xl, 'NordBord Data Dump', nord_cols)
        
        # Drive the Master Calendar Selector primarily off field practice dates (GPS)
        if not df_gps.empty and 'Date' in df_gps.columns:
            unique_dates = sorted(list(df_gps['Date'].dropna().unique()), reverse=True)
        else:
            all_logged_dates = []
            for current_df in [df_gps, df_force, df_perch, df_sprint, df_nord]:
                if not current_df.empty and 'Date' in current_df.columns:
                    all_logged_dates.extend(current_df['Date'].unique().tolist())
            unique_dates = sorted(list(set(all_logged_dates)), reverse=True)
            
        if "Manual Entry" in unique_dates: unique_dates.remove("Manual Entry")
    except:
        pass

if len(unique_dates) > 0:
    selected_date = st.sidebar.selectbox("🎯 Select Training/Practice Date:", unique_dates)
    st.sidebar.success("📊 Central Workbook: Connected & Live")
else:
    st.sidebar.warning("⚠️ Syncing data elements... App initializing.")
    df_gps, df_perch, df_nord, df_sprint, df_force = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Combine separate technology sheets using a rolling chronological "As-Of" target window
working_df = master_roster.copy()

def slice_and_merge_as_of(base_df, source_df, cols, date_val, tech_label):
    if source_df.empty:
        for c in cols: base_df[c] = 0.0
        base_df[f'{tech_label} Date'] = "No Record"
        return base_df
    try:
        sourced = source_df.copy()
        sourced['DT_Temp'] = pd.to_datetime(sourced['Date'], errors='coerce')
        sourced = sourced.dropna(subset=['DT_Temp'])
        
        # Filter down to entries that happened on or prior to the selected practice day
        if date_val and date_val != "System Simulation Mode":
            target_dt = pd.to_datetime(date_val, errors='coerce')
            if not pd.isna(target_dt):
                sourced = sourced[sourced['DT_Temp'] <= target_dt]
                
        if sourced.empty:
            for c in cols: base_df[c] = 0.0
            base_df[f'{tech_label} Date'] = "No Record"
            return base_df
            
        # Sort chronologically so the absolute latest logged row is at the bottom
        sourced = sourced.sort_values(by='DT_Temp')
        latest_test_cards = sourced.groupby('Match_Key').last().reset_index()
        
        rename_dict = {'Date': f'{tech_label} Date'}
        latest_test_cards = latest_test_cards.rename(columns=rename_dict)
        
        pull_cols = ['Match_Key', f'{tech_label} Date'] + cols
        return base_df.merge(latest_test_cards[pull_cols], on='Match_Key', how='left')
    except:
        for c in cols: base_df[c] = 0.0
        base_df[f'{tech_label} Date'] = "Error"
        return base_df

working_df = slice_and_merge_as_of(working_df, df_gps, gps_cols, selected_date, 'GPS')
working_df = slice_and_merge_as_of(working_df, df_perch, perch_cols, selected_date, 'Perch')
working_df = slice_and_merge_as_of(working_df, df_nord, nord_cols, selected_date, 'NordBord')
working_df = slice_and_merge_as_of(working_df, df_sprint, sprint_cols, selected_date, 'Sprint')
working_df = slice_and_merge_as_of(working_df, df_force, force_cols, selected_date, 'Hawkins')

# Data Cleanup Loop to eliminate empty blocks
for metric in gps_cols + perch_cols + nord_cols + sprint_cols + force_cols:
    if metric in working_df.columns:
        working_df[metric] = working_df[metric].fillna(0.0).round(1)
    else:
        working_df[metric] = 0.0
        
for tech in ['GPS', 'Perch', 'NordBord', 'Sprint', 'Hawkins']:
    if f'{tech} Date' in working_df.columns:
        working_df[f'{tech} Date'] = working_df[f'{tech} Date'].fillna("No Record")

# 5-Page Dashboard Navigation Selector
page = st.sidebar.radio("Select Portal Dashboard Module View:", [
    "Page 1: Daily Team Monitor",
    "Page 2: Positional Breakdowns",
    "Page 3: Individual Athlete Diagnostic",
    "Page 4: Summer 2026 Target Tracking",
    "Page 5: Tactical Practice Planner"
])

# --- PAGE 1: DAILY TEAM MONITOR ---
if page == "Page 1: Daily Team Monitor":
    st.title("👍 Texas A&M Football Performance Hub")
    st.markdown(f"### Master Technology Matrix | Target Baseline: **{selected_date}**")
    st.divider()
    
    tech_tab = st.radio("Toggle Applied Performance Technology View:", ["Catapult GPS Overview", "VBT Room (Perch)", "Hamstring Strength (NordBord)", "Speed Profiling (1080 Sprint)", "Neuromuscular (Force Plates)"], horizontal=True)
    
    pos_opts = list(working_df['Position Group'].unique())
    selected_groups = st.multiselect("Filter Roster Segmentations:", pos_opts, default=pos_opts)
    display_df = working_df[working_df['Position Group'].isin(selected_groups)]
    
    if tech_tab == "Catapult GPS Overview":
        st.dataframe(display_df[['Player', 'Position', 'Position Group', 'Total Distance (y)', 'Explosive Yardage', 'Total Player Load', 'Max Speed (mph)', 'Max Vel (% Max)']].sort_values(by='Total Distance (y)', ascending=False), use_container_width=True, hide_index=True)
    elif tech_tab == "VBT Room (Perch)":
        st.dataframe(display_df[['Player', 'Position', 'Perch Date', 'Mean Velocity (m/s)', 'Peak Velocity (m/s)', 'Peak Power (W)']].sort_values(by='Peak Power (W)', ascending=False), use_container_width=True, hide_index=True)
    elif tech_tab == "Hamstring Strength (NordBord)":
        st.dataframe(display_df[['Player', 'Position', 'NordBord Date', 'Max Left Force (N)', 'Max Right Force (N)', 'Total Force (N)', 'Imbalance (%)']].sort_values(by='Total Force (N)', ascending=False), use_container_width=True, hide_index=True)
    elif tech_tab == "Speed Profiling (1080 Sprint)":
        st.dataframe(display_df[['Player', 'Position', 'Sprint Date', 'Distance (m)', 'Peak Speed (mph)', 'Peak Power (W)', 'Avg Force (N)']].sort_values(by='Peak Speed (mph)', ascending=False), use_container_width=True, hide_index=True)
    elif tech_tab == "Neuromuscular (Force Plates)":
        st.dataframe(display_df[['Player', 'Position', 'Hawkins Date', 'Jump Height', 'mRSI']].sort_values(by='mRSI', ascending=False), use_container_width=True, hide_index=True)

# --- PAGE 2: POSITIONAL BREAKDOWNS ---
elif page == "Page 2: Positional Breakdowns":
    st.title("🎯 Positional Architecture Performance Tiers")
    st.markdown(f"### Positional Group Leaderboards for **{selected_date}**")
    st.divider()
    
    for group in ['Skill', 'Mid', 'Big']:
        st.markdown(f"## **{group.upper()} UNIT LEADERBOARD**")
        g_df = working_df[working_df['Position Group'] == group]
        st.dataframe(g_df[['Player', 'Position', 'Total Distance (y)', 'Explosive Yardage', 'Max Speed (mph)', 'Peak Power (W)', 'mRSI']].sort_values(by='Explosive Yardage', ascending=False), use_container_width=True, hide_index=True)

# --- PAGE 3: INDIVIDUAL ATHLETE DIAGNOSTIC ---
elif page == "Page 3: Individual Athlete Diagnostic":
    st.title("👤 Individual Athlete Profile Diagnostics")
    st.divider()
    
    selected_p = st.selectbox("Select Target Athlete Profile Panel:", working_df['Player'].tolist())
    p_row = working_df[working_df['Player'] == selected_p].iloc[0]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🕸️ Performance Capacity Spider Chart")
        categories = ['Velocity (Max Speed)', 'Power (Explosive Yds)', 'Force (mRSI)', 'Capacity (Player Load)', 'Vertical (Jump Height)']
        s_vel = min(100, int((p_row['Max Speed (mph)'] / 23.0) * 100)) if p_row['Max Speed (mph)'] > 0 else 50
        s_pow = min(100, int((p_row['Explosive Yardage'] / 800.0) * 100)) if p_row['Explosive Yardage'] > 0 else 50
        s_for = min(100, int((p_row['mRSI'] / 0.80) * 100)) if p_row['mRSI'] > 0 else 50
        s_cap = min(100, int((p_row['Total Player Load'] / 650.0) * 100)) if p_row['Total Player Load'] > 0 else 50
        s_vrt = min(100, int((p_row['Jump Height'] / 20.0) * 100)) if p_row['Jump Height'] > 0 else 50
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[s_vel, s_pow, s_for, s_cap, s_vrt], theta=categories, fill='toself',
            fillcolor='rgba(128, 0, 0, 0.4)', line=dict(color='#800000', width=3)
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#444444'), bgcolor='#1A1A1A'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("📊 Multi-Tech Athlete Metrics Capture")
        st.write(f"**Position Group:** {p_row['Position Group']} ({p_row['Position']})")
        st.write(f"ℹ️ *Showing most recent tests relative to selected date.*")
        st.divider()
        cx1, cx2 = st.columns(2)
        cx1.metric(f"Perch VBT Power ({p_row['Perch Date']})", f"{p_row['Peak Power (W)']} W")
        cx2.metric(f"NordBord Imbalance ({p_row['NordBord Date']})", f"{p_row['Imbalance (%)']}%")
        st.divider()
        cx3, cx4 = st.columns(2)
        cx3.metric(f"1080 Peak Speed ({p_row['Sprint Date']})", f"{p_row['Peak Speed (mph)']} mph")
        cx4.metric(f"Hawkins mRSI ({p_row['Hawkins Date']})", f"{p_row['mRSI']}")

# --- PAGE 4: SUMMER 2026 TARGET TRACKING ---
elif page == "Page 4: Summer 2026 Target Tracking":
    st.title("☀️ Summer 2026 Macrocycle Target Board")
    st.divider()
    
    targets = {
        'Skill': {'Dist_Target': 5500, 'Explosive_Target': 650, 'Actual_Dist': int(working_df[working_df['Position Group']=='Skill']['Total Distance (y)'].mean()), 'Actual_Explosive': int(working_df[working_df['Position Group']=='Skill']['Explosive Yardage'].mean())},
        'Mid': {'Dist_Target': 4200, 'Explosive_Target': 300, 'Actual_Dist': int(working_df[working_df['Position Group']=='Mid']['Total Distance (y)'].mean()), 'Actual_Explosive': int(working_df[working_df['Position Group']=='Mid']['Explosive Yardage'].mean())},
        'Big': {'Dist_Target': 2600, 'Explosive_Target': 80, 'Actual_Dist': int(working_df[working_df['Position Group']=='Big']['Total Distance (y)'].mean()), 'Actual_Explosive': int(working_df[working_df['Position Group']=='Big']['Explosive Yardage'].mean())}
    }
    for group, metrics in targets.items():
        st.markdown(f"#### **{group.upper()} TIER PERFORMANCE PROFILE**")
        cx1, cx2 = st.columns(2)
        cx1.metric(f"Total Distance (Target: {metrics['Dist_Target']} yds)", f"{metrics['Actual_Dist']} yds")
        cx2.metric(f"Explosive Yards (Target: {metrics['Explosive_Target']} yds)", f"{metrics['Actual_Explosive']} yds")

# --- PAGE 5: TACTICAL PRACTICE PLANNER ---
elif page == "Page 5: Tactical Practice Planner":
    st.title("⏱️ Scripted Practice Load Modeler Engine")
    st.divider()
    
    drill_library = {
        'Individual Position Warmup Block': {'Load_Per_Min': 4.5, 'Dist_Per_Min': 45},
        '1-on-1 Competitive Release Scripts': {'Load_Per_Min': 6.8, 'Dist_Per_Min': 75},
        '7-on-7 Perimeter Passing Concept Loop': {'Load_Per_Min': 5.2, 'Dist_Per_Min': 58},
        'Team Blitz Period / Inside Run Track': {'Load_Per_Min': 5.8, 'Dist_Per_Min': 50},
        'Full Team 11-on-11 Live Competitive Scripts': {'Load_Per_Min': 7.2, 'Dist_Per_Min': 82}
    }
    active_drills = []
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("#### **Select Active Period Drills**")
        for d_name, d_metrics in drill_library.items():
            is_selected = st.checkbox(f"Include: {d_name}", value=False)
            if is_selected:
                d_duration = st.number_input(f"Minutes for {d_name}:", min_value=1, max_value=45, value=10, key=f"dur_{d_name}")
                active_drills.append({'Drill': d_name, 'Duration': d_duration, 'Total Load Calc': d_metrics['Load_Per_Min'] * d_duration, 'Total Dist Calc': d_metrics['Dist_Per_Min'] * d_duration})
                
    with col_b:
        st.markdown("#### **Predictive Session Estimation Analytics**")
        if len(active_drills) > 0:
            plan_df = pd.DataFrame(active_drills)
            cx1, cx2, cx3 = st.columns(3)
            cx1.metric("Calculated Duration", f"{plan_df['Duration'].sum()} Mins")
            cx2.metric("Estimated Player Load", int(plan_df['Total Load Calc'].sum()))
            cx3.metric("Estimated Distance", f"{int(plan_df['Total Dist Calc'].sum())} yds")
            st.dataframe(plan_df, use_container_width=True, hide_index=True)
