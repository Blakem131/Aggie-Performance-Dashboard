# -----------------------------------------------------------------------------
# PAGE: ATHLETE DASHBOARD (Replicated from your Mockup Design)
# -----------------------------------------------------------------------------
if page == "👤 ATHLETE DASHBOARD":
    if not master_roster.empty:
        # Selection
        name = st.selectbox("SELECT ATHLETE:", master_roster['Name'].tolist())
        p_row = master_roster[master_roster['Name'] == name].iloc[0]
        
        # 1. HEADER (Styled after your mockup)
        st.markdown(f'<div class="os-header">{p_row["Name"]} // {p_row["POS"]} // Texas A&M Football</div>', unsafe_allow_html=True)
        
        # 2. METRIC CARDS (Top Row)
        row0 = st.columns(4)
        indices = [("SPEED INDEX", "94"), ("FORCE INDEX", "81"), ("STRENGTH INDEX", "77"), ("POWER INDEX", "91")]
        for i, col in enumerate(row0):
            col.markdown(f'<div class="metric-card"><div class="metric-val">{indices[i][1]}</div><div class="metric-label">{indices[i][0]}</div></div>', unsafe_allow_html=True)
            
        # 3. DASHBOARD BODY (Readiness, Trends, Radar)
        col_left, col_mid, col_right = st.columns([1, 2, 2])
        
        with col_left:
            st.markdown('<div class="os-tile"><h4>READINESS ENGINE</h4><p style="font-size:42px; font-weight:900; color:#00FF00; text-align:center;">82%</p></div>', unsafe_allow_html=True)
            # Add the comments section you requested
            st.markdown('<h4>Readiness Analysis</h4><div class="analysis-box">Alert: Acute to Chronic workload spike detected (Ratio: 1.5) in Total Distance. Suggesting deload for lower body session.</div>', unsafe_allow_html=True)
        
        with col_mid:
            st.markdown('<div class="os-tile"><h4>PERFORMANCE TRENDS</h4></div>', unsafe_allow_html=True)
            # This is where your trend data will render dynamically
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=['W1', 'W2', 'W3', 'W4'], y=[25, 27, 28, 34], line=dict(color='#00F2FF', width=4)))
            fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.markdown('<div class="os-tile"><h4>ATHLETIC PROFILE</h4></div>', unsafe_allow_html=True)
            # This is your dynamic Spider Chart
            fig_r = go.Figure(go.Scatterpolar(r=[90, 80, 85, 70, 95], theta=['Speed', 'Strength', 'Power', 'Force', 'Elastic'], fill='toself', fillcolor='rgba(0, 242, 255, 0.2)', line_color='#00F2FF'))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='#1E293B'), bgcolor='#0B1220'), height=250, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig_r, use_container_width=True)
