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
DATABASE_FILE = "Aggie Database.xlsx"

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
# HIGH-SPEED MEMORY STREAM LOADING ENGINE
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

# High-TTL cache prevents Streamlit from reopening Excel on page changes
@st.cache_data(ttl=300)
def load_entire_database_cache(file_path, gps_cols, force_cols, perch_cols, sprint_cols, nord_cols):
    data_bundles = {
        'df_gps': pd.DataFrame(), 'df_force': pd.DataFrame(), 'df_perch': pd.DataFrame(),
        'df_sprint': pd.DataFrame(), 'df_nord': pd.DataFrame(), 'unique_dates': []
    }
    if not os.path.exists(file_path):
        return data_bundles
        
    try:
        xl_file = pd.ExcelFile(file_path)
        sheet_configs = [
            ('Catapult Data Dump', gps_cols, 'df_gps'),
            ('Hawkins Data Dump', force_cols, 'df_force'),
            ('Perch Data Dump', perch_cols, 'df_perch'),
            ('Sprint 1080 Data Dump', sprint_cols, 'df_sprint'),
            ('NordBord Data Dump', nord_cols, 'df_nord')
        ]
        
        all_dates = []
        for sheet_name, target_cols, dict_key in sheet_configs:
            if sheet_name in xl_file.sheet_names:
                df = pd.read_excel(xl_file, sheet_name=sheet_name)
                df.columns = [str(c).strip() for c in df.columns]
                
                rename_map = {}
                for col in df.columns:
                    c_low = col.lower().strip()
                    if c_low in ['name', 'player', 'athlete', 'player name']: rename_map[col] = 'Player'
                    elif c_low == 'date': rename_map[col] = 'Date'
                    else:
                        for tc in target_cols:
                            if c_low == tc.lower().strip():
                                rename_map[col] = tc
                                
                df = df.rename(columns=rename_map)
                if 'Player' in df.columns:
                    df['Match_Key'] = df['Player'].astype(str).str.strip().str.upper()
                    df['Date'] = df['Date'].astype(str).str.strip() if 'Date' in df.columns else "Manual Entry"
                    
                    for tc in target_cols:
                        if tc in df.columns:
                            df[tc] = pd.to_numeric(df[tc], errors='coerce').fillna(0.0)
                        else:
                            df[tc] = 0.0
                            
                    pull_cols = ['Match_Key', 'Date'] + [tc for tc in target_cols if tc in df.columns]
                    data_bundles[dict_key] = df[pull_cols]
                    if 'Date' in df.columns:
                        all_dates.extend(df['Date'].dropna().unique().tolist())
                        
        unique_dates = list(set([str(d).strip() for d in all_dates if str(d).strip() != "Manual Entry"]))
        data_bundles['unique_dates'] = sorted(unique_dates, reverse=True)
        return data_bundles
    except:
        return data_bundles

# -----------------------------------------------------------------------------
# COORDINATE PROGRAM PIPELINE
# -----------------------------------------------------------------------------
st.sidebar.title("Aggie Portal Control")

master_roster = load_base_roster()
if master_roster is None:
    st.sidebar.error(f"⚠️ Base file '{ROSTER_FILE}' missing.")
    st.stop()

gps_cols = ['Total Distance (y)', 'Total Player Load', 'Player Load Per Minute', 'IMA Total', 'Explosive Yardage', 'Max Speed (mph)', 'Max Vel (% Max)']
perch_cols = ['Mean Velocity (m/s)', 'Peak Velocity (m/s)', 'Peak Power (W)']
nord_cols = ['Max Left Force (N)', 'Max Right Force (N)', 'Total Force (N)', 'Imbalance (%)']
sprint_cols = ['Distance (m)', 'Peak Speed (mph)', 'Peak Power (W)', 'Avg Force (N)']
force_cols = ['Jump Height', 'mRSI']

# Load the single-scan memory layout object
cache_bundle = load_entire_database_cache(DATABASE_FILE, gps_cols, force_cols, perch_cols, sprint_cols, nord_cols)

df_gps = cache_bundle['df_gps']
df_force = cache_bundle['df_force']
df_perch = cache_bundle['df_perch']
df_sprint = cache_bundle['df_sprint']
df_nord = cache_bundle['df_nord']
unique_dates = cache_bundle['unique_dates']

selected_date = "Manual Entry"
if len(unique_dates) > 0:
    selected_date = st.sidebar.selectbox("🎯 Select Practice Date:", unique_dates)
    st.sidebar.success("📊 High-Speed Optimization Active")
else:
    st.sidebar.warning("⚠️ Reading master sheets...")

# High-speed data slice mapping
working_df = master_roster.copy()

def slice_and_merge(base_df, source_df, cols, date_val):
    if source_df.empty:
        for c in cols: base_df[c] = 0.0
        return base_df
    filtered = source_df[source_df['Date'] == date_val]
    if filtered.empty:
        for c in cols: base_df[c] = 0.0
        return base_df
    sub_df = filtered[['Match_Key'] + [c for c in cols if c in filtered.columns]].drop_duplicates(subset=['Match_Key'])
    return base_df.merge(sub_df, on='Match_Key', how='left')

working_df = slice_and_merge(working_df, df_gps, gps_cols, selected_date)
working_df = slice_and_merge(working_df, df_perch, perch_cols, selected_date)
working_df = slice_and_merge(working_df, df_nord, nord_cols, selected_date)
working_df = slice_and_merge(working_df, df_sprint, sprint_cols, selected_date)
working_df = slice_and_merge(working_df, df_force, force_cols, selected_date)

all_metrics = gps_cols + perch_cols + nord_cols + sprint_cols + force_cols
for metric in all_metrics:
    if metric in working_df.columns:
        working_df[metric] = pd.to_numeric(working_df[metric], errors='coerce').fillna(0.0).round(1)
    else:
        working_df[metric] = 0.0

# Navigation Switch Hub
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
    st.markdown(f"### Master Technology Matrix | Date: **{selected_date}**")
    st.divider()
    
    tech_tab = st.radio("Toggle Applied Performance Technology View:", ["Catapult GPS Overview", "VBT Room (Perch)", "Hamstring Strength (NordBord)", "Speed Profiling (1080 Sprint)", "Neuromuscular (Force Plates)"], horizontal=True)
    
    pos_opts = list(working_df['Position Group'].unique())
    selected_groups = st.multiselect("Filter Roster Segmentations:", pos_opts, default=pos_opts)
    display_df = working_df[working_df['Position Group'].isin(selected_groups)]
    
    if tech_tab == "Catapult GPS Overview":
        st.dataframe(display_df[['Player', 'Position', 'Position Group', 'Total Distance (y)', 'Explosive Yardage', 'Total Player Load', 'Max Speed (mph)', 'Max Vel (% Max)']].sort_values(by='Total Distance (y)', ascending=False), width='stretch', hide_index=True)
    elif tech_tab == "VBT Room (Perch)":
        st.dataframe(display_df[['Player', 'Position', 'Mean Velocity (m/s)', 'Peak Velocity (m/s)', 'Peak Power (W)']].sort_values(by='Peak Power (W)', ascending=False), width='stretch', hide_index=True)
    elif tech_tab == "Hamstring Strength (NordBord)":
        st.dataframe(display_df[['Player', 'Position', 'Max Left Force (N)', 'Max Right Force (N)', 'Total Force (N)', 'Imbalance (%)']].sort_values(by='Total Force (N)', ascending=False), width='stretch', hide_index=True)
    elif tech_tab == "Speed Profiling (1080 Sprint)":
        st.dataframe(display_df[['Player', 'Position', 'Distance (m)', 'Peak Speed (mph)']].sort_values(by='Peak Speed (mph)', ascending=False), width='stretch', hide_index=True)
    elif tech_tab == "Neuromuscular (Force Plates)":
        st.dataframe(display_df[['Player', 'Position', 'Jump Height', 'mRSI']].sort_values(by='mRSI', ascending=False), width='stretch', hide_index=True)

# --- PAGE 2: POSITIONAL BREAKDOWNS ---
elif page == "Page 2: Positional Breakdowns":
    st.title("🎯 Positional Architecture Performance Tiers")
    st.divider()
    
    for group in ['Skill', 'Mid', 'Big']:
        st.markdown(f"## **{group.upper()} UNIT LEADERBOARD**")
        g_df = working_df[working_df['Position Group'] == group]
        st.dataframe(g_df[['Player', 'Position', 'Total Distance (y)', 'Explosive Yardage', 'Max Speed (mph)', 'mRSI']].sort_values(by='Explosive Yardage', ascending=False), width='stretch', hide_index=True)

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
        
        s_vel = min(100, int((float(p_row['Max Speed (mph)']) / 23.0) * 100)) if float(p_row['Max Speed (mph)']) > 0 else 45
        s_pow = min(100, int((float(p_row['Explosive Yardage']) / 800.0) * 100)) if float(p_row['Explosive Yardage']) > 0 else 45
        s_for = min(100, int((float(p_row['mRSI']) / 0.80) * 100)) if float(p_row['mRSI']) > 0 else 45
        s_cap = min(100, int((float(p_row['Total Player Load']) / 650.0) * 100)) if float(p_row['Total Player Load']) > 0 else 45
        s_vrt = min(100, int((float(p_row['Jump Height']) / 20.0) * 100)) if float(p_row['Jump Height']) > 0 else 45
        
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
        st.divider()
        cx1, cx2 = st.columns(2)
        cx1.metric("Perch VBT Power", f"{p_row['Peak Power (W)']} W")
        cx2.metric("NordBord Imbalance", f"{p_row['Imbalance (%)']}%")
        st.divider()
        cx3, cx4 = st.columns(2)
        cx3.metric("GPS Max Speed", f"{p_row['Max Speed (mph)']} mph")
        cx4.metric("Hawkins mRSI", f"{p_row['mRSI']}")

# --- PAGE 4: SUMMER 2026 TARGET TRACKING ---
elif page == "Page 4: Summer 2026 Target Tracking":
    st.title("☀️ Summer 2026 Macrocycle Target Board")
    st.divider()
    
    s_group = working_df[working_df['Position Group']=='Skill']
    m_group = working_df[working_df['Position Group']=='Mid']
    b_group = working_df[working_df['Position Group']=='Big']
    
    targets = {
        'Skill': {'Dist_Target': 5500, 'Explosive_Target': 650, 'Actual_Dist': int(s_group['Total Distance (y)'].mean()) if not s_group.empty else 0, 'Actual_Explosive': int(s_group['Explosive Yardage'].mean()) if not s_group.empty else 0},
        'Mid': {'Dist_Target': 4200, 'Explosive_Target': 300, 'Actual_Dist': int(m_group['Total Distance (y)'].mean()) if not m_group.empty else 0, 'Actual_Explosive': int(m_group['Explosive Yardage'].mean()) if not m_group.empty else 0},
        'Big': {'Dist_Target': 2600, 'Explosive_Target': 80, 'Actual_Dist': int(b_group['Total Distance (y)'].mean()) if not b_group.empty else 0, 'Actual_Explosive': int(b_group['Explosive Yardage'].mean()) if not b_group.empty else 0}
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
            st.dataframe(plan_df, width='stretch', hide_index=True)
