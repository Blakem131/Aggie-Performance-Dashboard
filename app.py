import streamlit as st
import pandas as pd
import numpy as np
import base64
import os
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CORE ROSTER MASTER POINT OF TRUTH
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
            text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        }}
        h2, h3, h4 {{ 
            color: #FFFFFF !important; font-family: 'Helvetica Neue', Arial, sans-serif; font-weight: 700;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
        }}
        [data-testid="stSidebar"] {{ 
            background-color: rgba(80, 0, 0, 0.95) !important; border-right: 3px solid #800000; 
        }}
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {{
            color: #FFFFFF !important; font-weight: bold;
        }}
        div.stMetric, div[data-testid="stMetricBlock"] {{
            background-color: rgba(20, 20, 20, 0.80) !important; border: 2px solid #500000 !important;
            border-radius: 8px !important; padding: 18px !important; backdrop-filter: blur(5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.6);
        }}
        div[data-testid="stMetricValue"] {{ color: #FFFFFF !important; font-weight: 900 !important; font-size: 2.3rem !important; }}
        div[data-testid="stMarkdownContainer"] p {{ color: #FFFFFF !important; }}
        .stDataFrame, .dataframe {{ background-color: rgba(20, 20, 20, 0.85) !important; border-radius: 6px; backdrop-filter: blur(5px); }}
    </style>
""", unsafe_allow_html=True)

if logo_base64:
    st.markdown(f'<img src="data:image/png;base64,{logo_base64}" class="aggie-floating-logo">', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA IMPORT & PARSING ENGINE
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
# DATA PIPELINE CONTROL FRAMEWORK
# -----------------------------------------------------------------------------
st.sidebar.title("Aggie System Control")

master_roster = load_base_roster()

if master_roster is None:
    st.sidebar.error(f"⚠️ Master file '{ROSTER_FILE}' not detected inside your core repository.")
    st.stop()

master_roster['Match_Key'] = master_roster['Player'].astype(str).str.strip().str.upper()

uploaded_session = st.sidebar.file_uploader("Upload Daily Session Report:", type=["csv", "xlsx"])

# Build or merge data mapping channels safely
if uploaded_session is not None:
    session_metrics = process_uploaded_metrics(uploaded_session)
    if session_metrics is not None and len(session_metrics) > 0:
        session_metrics['Match_Key'] = session_metrics['Player'].astype(str).str.strip().str.upper()
        gps_df = master_roster.merge(session_metrics[['Match_Key', 'Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed']], on='Match_Key', how='left')
        st.sidebar.success(f"⚡ Session Applied: {len(session_metrics)} Athletes Synced")
    else:
        st.sidebar.error("⚠️ Formatting Warning: Check column alignments below.")
        gps_df = master_roster.copy()
        for col in ['Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed']: gps_df[col] = 0.0
else:
    gps_df = master_roster.copy()
    for col in ['Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed']: gps_df[col] = 0.0

# Guarantee zero-value fills across missing columns to block NameErrors entirely
for col in ['Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed']:
    gps_df[col] = pd.to_numeric(gps_df[col], errors='coerce').fillna(0.0)

# Apply simulated sports science columns for fields not inside the standard Catapult sheet
np.random.seed(42)
gps_df['Jump Height'] = np.random.uniform(14.0, 19.5, len(gps_df)).round(2)
gps_df['mRSI'] = np.random.uniform(0.50, 0.78, len(gps_df)).round(2)
gps_df['ACWR'] = np.random.uniform(0.85, 1.60, len(gps_df)).round(2)
gps_df['Jump_Delta_%'] = np.random.uniform(-14.0, 14.0, len(gps_df)).round(1)

# Generate Dynamic Progression Charts Map for Page 3
dates_5w = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
history_records = []
for idx, row in gps_df.iterrows():
    for w_idx, w_name in enumerate(dates_5w):
        factor = 1.0 + (w_idx - 4) * 0.03 + np.random.uniform(-0.04, 0.04)
        history_records.append({
            'Player': row['Player'], 'Week': w_name,
            'Jump Height History': round(row['Jump Height'] * factor, 2),
            'Total Distance History': round(row['Total Distance'] * (factor + 0.05), 1),
            'mRSI History': round(row['mRSI'] * factor, 2)
        })
history_df = pd.DataFrame(history_records)

# 5-Page Dashboard Navigation Layout Module List Selector
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
    st.markdown("### Master Roster Workload Panel | Active Volume Tracking")
    st.divider()
    
    pos_opts = list(gps_df['Position Group'].unique())
    selected_groups = st.multiselect("Filter Roster Segmentations:", pos_opts, default=pos_opts)
    display_df = gps_df[gps_df['Position Group'].isin(selected_groups)]
    
    st.dataframe(display_df[['Player', 'Position', 'Position Group', 'Total Distance', 'Explosive Yardage', 'Player Load', 'Max Speed', 'Jump Height', 'mRSI', 'ACWR']].sort_values(by='Total Distance', ascending=False), use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("📊 Session Fluctuation Trends & Neuromuscular Movement Alerts")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🚀 Top Weekly Improvers (Jump Height)")
        t10 = gps_df.sort_values(by='Jump_Delta_%', ascending=False).head(10)
        st.dataframe(t10[['Player', 'Position', 'Jump Height', 'Jump_Delta_%']].rename(columns={'Jump_Delta_%':'Weekly Change %'}), hide_index=True, use_container_width=True)
    with c2:
        st.markdown("#### 📉 Bottom Weekly Declines (Jump Height)")
        b10 = gps_df.sort_values(by='Jump_Delta_%', ascending=True).head(10)
        st.dataframe(b10[['Player', 'Position', 'Jump Height', 'Jump_Delta_%']].rename(columns={'Jump_Delta_%':'Weekly Change %'}), hide_index=True, use_container_width=True)
    with c3:
        st.markdown("#### 🚨 Acute-to-Chronic Workload Flag Watchlist")
        spikes = gps_df[gps_df['ACWR'] >= 1.3].sort_values(by='ACWR', ascending=False)
        if len(spikes) == 0: st.success("All systems functional. No active workload flags generated.")
        else: st.dataframe(spikes[['Player', 'Position Group', 'Total Distance', 'ACWR']], hide_index=True, use_container_width=True)

# --- PAGE 2: POSITIONAL BREAKDOWNS ---
elif page == "Page 2: Positional Breakdowns":
    st.title("🎯 Positional Architecture Performance Tiers")
    st.divider()
    
    for group in ['Skill', 'Mid', 'Big']:
        st.markdown(f"## **{group.upper()} UNIT LEADERBOARD**")
        g_df = gps_df[gps_df['Position Group'] == group]
        mean_dist = int(g_df['Total Distance'].mean()) if len(g_df) > 0 else 1
        
        leader_view = g_df[['Player', 'Position', 'Total Distance', 'Explosive Yardage', 'Max Speed', 'mRSI']].copy()
        leader_view['Load Variance vs Unit'] = leader_view['Total Distance'].apply(lambda x: f"{x - mean_dist:+.0f} yds")
        
        st.dataframe(leader_view.sort_values(by='Explosive Yardage', ascending=False), use_container_width=True, hide_index=True)

# --- PAGE 3: INDIVIDUAL ATHLETE DIAGNOSTIC ---
elif page == "Page 3: Individual Athlete Diagnostic":
    st.title("👤 Individual Athlete Profile Diagnostics")
    st.markdown("### Comprehensive Capacity Profiles & Historical Progressions")
    st.divider()
    
    selected_p = st.selectbox("Select Target Athlete Profile Panel:", gps_df['Player'].tolist())
    p_row = gps_df[gps_df['Player'] == selected_p].iloc[0]
    p_hist = history_df[history_df['Player'] == selected_p]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🕸️ Performance Capacity Spider Chart")
        categories = ['Velocity (Max Speed)', 'Power (Explosive Yds)', 'Force (mRSI)', 'Capacity (Player Load)', 'Vertical (Jump Height)']
        s_vel = min(100, int((p_row['Max Speed'] / 23.0) * 100)) if p_row['Max Speed'] > 0 else 0
        s_pow = min(100, int((p_row['Explosive Yardage'] / 800.0) * 100)) if p_row['Explosive Yardage'] > 0 else 0
        s_for = min(100, int((p_row['mRSI'] / 0.80) * 100)) if p_row['mRSI'] > 0 else 0
        s_cap = min(100, int((p_row['Player Load'] / 650.0) * 100)) if p_row['Player Load'] > 0 else 0
        s_vrt = min(100, int((p_row['Jump Height'] / 20.0) * 100)) if p_row['Jump Height'] > 0 else 0
        
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
        st.subheader("🏈 NFL Model Comparison & Directives")
        nfl_comp = "Deebo Samuel Archetype" if p_row['Position Group']=='Skill' else "Fred Warner Archetype" if p_row['Position Group']=='Mid' else "Chris Jones Archetype"
        st.metric("🎯 NFL Player Model Matching Profile:", nfl_comp)
        
        if p_row['ACWR'] >= 1.4: st.error(f"❌ **FATIGUE FLAG:** ACWR is elevated at {p_row['ACWR']:.2f}")
        else: st.success("✅ **LOAD RATIO CLEAR:** Workload safely integrated inside recovery limits.")
        st.info("👉 **Coaching Mandate:** Maintain targeted explosive power velocity blocks.")

    st.divider()
    st.subheader("📈 Click Drop-Down Panels Below to Expand Historical Progression Trends")
    
    with st.expander("📊 View 5-Week Jump Height Historical Progression Curve"):
        fig_jh = px.line(p_hist, x='Week', y='Jump Height History', text='Jump Height History', title=f"{selected_p} - Jump Vertical Trends")
        fig_jh.update_traces(line_color='#800000', line_width=4, marker=dict(size=10, color='#FFFFFF'))
        fig_jh.update_layout(paper_bgcolor='#1A1A1A', plot_bgcolor='#1A1A1A', font_color='#FFFFFF', yaxis=dict(gridcolor='#333333'))
        st.plotly_chart(fig_jh, use_container_width=True)
        
    with st.expander("📊 View 5-Week Cumulative Running Volume Trend (Total Distance)"):
        fig_dist = px.bar(p_hist, x='Week', y='Total Distance History', text='Total Distance History', title=f"{selected_p} - Field Running History")
        fig_dist.update_traces(marker_color='#500000', textposition='outside')
        fig_dist.update_layout(paper_bgcolor='#1A1A1A', plot_bgcolor='#1A1A1A', font_color='#FFFFFF', yaxis=dict(gridcolor='#333333'))
        st.plotly_chart(fig_dist, use_container_width=True)

# --- PAGE 4: SUMMER 2026 TARGET TRACKING ---
elif page == "Page 4: Summer 2026 Target Tracking":
    st.title("☀️ Summer 2026 Macrocycle Target Board")
    st.divider()
    
    targets = {
        'Skill': {'Dist_Target': 5500, 'Explosive_Target': 650, 'Actual_Dist': int(gps_df[gps_df['Position Group']=='Skill']['Total Distance'].mean()), 'Actual_Explosive': int(gps_df[gps_df['Position Group']=='Skill']['Explosive Yardage'].mean())},
        'Mid': {'Dist_Target': 4200, 'Explosive_Target': 300, 'Actual_Dist': int(gps_df[gps_df['Position Group']=='Mid']['Total Distance'].mean()), 'Actual_Explosive': int(gps_df[gps_df['Position Group']=='Mid']['Explosive Yardage'].mean())},
        'Big': {'Dist_Target': 2600, 'Explosive_Target': 80, 'Actual_Dist': int(gps_df[gps_df['Position Group']=='Big']['Total Distance'].mean()), 'Actual_Explosive': int(gps_df[gps_df['Position Group']=='Big']['Explosive Yardage'].mean())}
    }
    for group, metrics in targets.items():
        st.markdown(f"#### **{group.upper()} TIER PERFORMANCE PROFILE**")
        cx1, cx2, cx3 = st.columns(3)
        d_pct = (metrics['Actual_Dist'] / metrics['Dist_Target']) * 100 if metrics['Dist_Target'] > 0 else 0
        e_pct = (metrics['Actual_Explosive'] / metrics['Explosive_Target']) * 100 if metrics['Explosive_Target'] > 0 else 0
        cx1.metric(f"Total Distance (Target: {metrics['Dist_Target']} yds)", f"{metrics['Actual_Dist']} yds", f"{d_pct:-.1f}%")
        cx2.metric(f"Explosive Yards (Target: {metrics['Explosive_Target']} yds)", f"{metrics['Actual_Explosive']} yds", f"{e_pct:-.1f}%")
        cx3.metric("Current Unit Rolling ACWR", f"{gps_df[gps_df['Position Group']==group]['ACWR'].mean():.2f}")

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
            is_selected = st.checkbox(f"Include: {d_name}", value=True if d_name in ['Individual Position Warmup Block'] else False)
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
