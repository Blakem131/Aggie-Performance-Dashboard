import streamlit as st
import pandas as pd
import numpy as np
import requests

# Set Page Config with Team Title
st.set_page_config(page_title="Texas A&M Football Performance Hub", layout="wide")

# Corrected Maroon Custom Branding Layout
st.markdown("""
    <style>
        .stApp {
            background-color: #FAFAFA;
        }
        h1 {
            color: #500000 !important;
            font-family: 'Arial Black', Gadget, sans-serif;
            border-bottom: 3px solid #500000;
            padding-bottom: 10px;
        }
        h3, h4 {
            color: #333333 !important;
            font-family: 'Arial', sans-serif;
        }
        [data-testid="stSidebar"] {
            background-color: #500000;
            color: #FFFFFF;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: #FFFFFF !important;
        }
        div[data-testid="stMetricValue"] {
            color: #500000 !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("👍 Texas A&M Football Performance Hub")
st.markdown("### Sports Science Integration Panel | Catapult, Hawkins & Vald Hub")
st.divider()

# --- SIDEBAR PRODUCTION FILE UPLOADERS ---
st.sidebar.title("Aggie Data Control")
st.sidebar.markdown("Upload your daily session exports to sync the roster views.")

uploaded_catapult = st.sidebar.file_uploader("1. Upload Catapult GPS Export:", type=["csv", "xlsx"])
uploaded_nordbord = st.sidebar.file_uploader("2. Upload NordBord Export (Optional):", type=["csv", "xlsx"])

# --- AUTOMATED BACKGROUND HAWKINS ENGINE ---
@st.cache_data(ttl=300)
def fetch_automated_hawkins():
    API_KEY = "nHp9ZE.RqbeugMoIEysLf8C7z27S8IqxGDi8"
    TOKEN_URL = "https://cloud.hawkindynamics.com/api/token"
    API_URL = "https://cloud.hawkindynamics.com/api/v1/tests"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(TOKEN_URL, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token", token_data.get("token"))
            
            data_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            data_response = requests.get(API_URL, headers=data_headers)
            
            if data_response.status_code == 200:
                raw_tests = data_response.json().get("data", [])
                records = []
                for test in raw_tests:
                    athlete = test.get("athlete", {})
                    metrics = test.get("metrics", {})
                    
                    first = athlete.get("first_name", "").strip()
                    last = athlete.get("last_name", "").strip()
                    player_name = f"{first} {last}".strip()
                    
                    rsi_val = metrics.get("rsi_modified", metrics.get("rsi_mod", metrics.get("rsi", 0.60)))
                    
                    if player_name:
                        records.append({
                            "Player": player_name,
                            "mRSI (Modified)": float(rsi_val)
                        })
                
                if records:
                    df = pd.DataFrame(records)
                    return df.groupby("Player").last().reset_index()
    except Exception:
        pass
    return None

def parse_uploaded_file(file_obj):
    if file_obj is not None:
        if file_obj.name.endswith('.csv'):
            return pd.read_csv(file_obj)
        else:
            return pd.read_excel(file_obj)
    return None

# Load the file objects directly from browser memory
gps_raw = parse_uploaded_file(uploaded_catapult)
nord_raw = parse_uploaded_file(uploaded_nordbord)
force_df = fetch_automated_hawkins()

# Live Connection Dashboard Checks
st.sidebar.divider()
st.sidebar.subheader("System Feeds Status")
st.sidebar.checkbox("Hawkins Cloud Pipeline: LIVE", value=(force_df is not None), disabled=True)
st.sidebar.checkbox("Catapult GPS Stream: Sync'd", value=(gps_raw is not None), disabled=True)
st.sidebar.checkbox("NordBord Asymmetry: Sync'd", value=(nord_raw is not None), disabled=True)

# --- MASTER PROCESSING DATA ENGINE ---
if gps_raw is not None:
    try:
        def find_athlete_col(df):
            for col in df.columns:
                if any(x in str(col).lower() for x in ['player', 'athlete', 'last name', 'name']):
                    return col
            return df.columns[0]

        gps_player_col = find_athlete_col(gps_raw)
        gps_raw['Athlete_Key'] = gps_raw[gps_player_col].astype(str).str.strip().str.upper()
        
        dist_col = [c for c in gps_raw.columns if 'total distance' in str(c).lower() or 'distance' in str(c).lower()][0]
        acwr_col = [c for c in gps_raw.columns if 'acwr' in str(c).lower() or 'acute' in str(c).lower() or 'ratio' in str(c).lower()]
        acwr_col = acwr_col[0] if acwr_col else None

        master_df = pd.DataFrame({
            'Athlete_Key': gps_raw['Athlete_Key'],
            'Player': gps_raw[gps_player_col],
            'Acute Load (7-Day Yds)': gps_raw[dist_col].astype(float)
        })
        master_df['ACWR'] = gps_raw[acwr_col].astype(float) if acwr_col else 1.0

        # Positional Segmentation
        group_col = [c for c in gps_raw.columns if 'group' in str(c).lower() or 'position' in str(c).lower()]
        if group_col:
            master_df['Position Group'] = gps_raw[group_col[0]]
        else:
            def auto_categorize(name):
                name_str = str(name).upper()
                if any(x in name_str for x in ['WR', 'CB', 'RB', 'FS', 'SS', 'SKILL']): return 'Skill'
                elif any(x in name_str for x in ['TE', 'LB', 'QB', 'DE', 'MID']): return 'Mid'
                else: return 'Big'
            master_df['Position Group'] = master_df['Player'].apply(auto_categorize)

        # Merge Automated Hawkins Force Data
        if force_df is not None:
            force_df['Athlete_Key'] = force_df['Player'].astype(str).str.strip().str.upper()
            master_df = master_df.merge(force_df[['Athlete_Key', 'mRSI (Modified)']], on='Athlete_Key', how='left')
        
        if 'mRSI (Modified)' not in master_df.columns:
            master_df['mRSI (Modified)'] = 0.60
        master_df['mRSI (Modified)'] = master_df['mRSI (Modified)'].fillna(0.60)

        # Merge Vald NordBord Asymmetry Data
        if nord_raw is not None:
            n_key = find_athlete_col(nord_raw)
            nord_raw['Athlete_Key'] = nord_raw[n_key].astype(str).str.strip().str.upper()
            asym_cols = [c for c in nord_raw.columns if 'asymmetry' in str(c).lower() or 'delta' in str(c).lower()]
            if asym_cols:
                master_df = master_df.merge(nord_raw[['Athlete_Key', asym_cols[0]]].rename(columns={asym_cols[0]: 'Asymmetry %'}), on='Athlete_Key', how='left')

        if 'Asymmetry %' not in master_df.columns:
            master_df['Asymmetry %'] = 5.0
        master_df['Asymmetry %'] = master_df['Asymmetry %'].fillna(5.0)

        # Readiness Engine Formula
        def derive_freshness(row):
            score = 100
            if row['ACWR'] >= 1.5: score -= 35
            elif row['ACWR'] >= 1.3: score -= 15
            if row['mRSI (Modified)'] < 0.50: score -= 20
            if row['Asymmetry %'] > 15.0: score -= 15
            return max(0, min(100, int(score)))

        master_df['Freshness Score'] = master_df.apply(derive_freshness, axis=1)

        # Selection Filters
        position_filter = st.multiselect("Filter View by Position Group:", options=list(master_df["Position Group"].unique()), default=list(master_df["Position Group"].unique()))
        filtered_df = master_df[master_df["Position Group"].isin(position_filter)]

        high_risk_df = filtered_df[filtered_df["ACWR"] >= 1.5]
        watch_df = filtered_df[(filtered_df["ACWR"] >= 1.3) & (filtered_df["ACWR"] < 1.5)]

        # Render Core KPI Metrics Block
        c1, c2, c3 = st.columns(3)
        c1.metric("🚨 Critical High Load Flags", len(high_risk_df))
        c2.metric("⚠️ Spike Risk Watchlist", len(watch_df))
        c3.metric("📋 Selected Roster Average Freshness", f"{int(filtered_df['Freshness Score'].mean())}/100")

        st.subheader("📋 Integrated Team Roster Monitor")
        st.dataframe(filtered_df[["Player", "Position Group", "Acute Load (7-Day Yds)", "ACWR", "mRSI (Modified)", "Asymmetry %", "Freshness Score"]], use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("📋 Individual Athlete Diagnostic Cards")
        selected_player = st.selectbox("Select Athlete for Maintenance Plan:", options=filtered_df["Player"].tolist())
        
        if selected_player:
            p = filtered_df[filtered_df["Player"] == selected_player].iloc[0]
            cx1, cx2, cx3, cx4 = st.columns(4)
            cx1.metric("Current ACWR", f"{p['ACWR']:.2f}")
            cx2.metric("Freshness Score", f"{p['Freshness Score']}/100")
            cx3.metric("Hawkins mRSI", f"{p['mRSI (Modified)']:.2f}")
            cx4.metric("NordBord Asymmetry", f"{p['Asymmetry %']:.1f}%")
            
            st.markdown("#### **Coaching Intervention Blueprint**")
            if p['ACWR'] >= 1.5 or p['Freshness Score'] < 50:
                st.error("❌ **Status: RED FLAG (High Load Spike / Neural Fatigue)**")
                if p['Position Group'] in ['Skill', 'Wide Receiver', 'Cornerback']: st.info("Pull from team competitive scripts. Cap sprint yardage to **max 200 yards** today.")
                elif p['Position Group'] in ['Mid', 'Linebacker', 'Tight End']: st.info("Modify full-contact periods. Shift volume to walkthrough loops.")
                else: st.info("Remove interior live trench contact. Shift to upper body structural volume and soft tissue flush tracks.")
            elif p['ACWR'] >= 1.3 or p['Freshness Score'] < 75:
                st.warning("⚠️ **Status: AMBER FLAG (Approaching Threshold)**")
                st.write("Reduce total tactical practice load allocations by **25%** for this individual today.")
            else:
                st.success("✅ **Status: GREEN LIGHT**")
                st.write("Cleared for standard training targets and maximum velocity exposure blocks.")

    except Exception as e:
        st.error(f"Error compiling team metrics sheet: {e}")
else:
    st.info("👋 System Live: Hawkins Cloud is automated and streaming! Drag and drop your Catapult GPS report file directly into the sidebar panel link on your browser to load the Texas A&M roster charts.")
