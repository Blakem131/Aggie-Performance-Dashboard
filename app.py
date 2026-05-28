@st.cache_data(ttl=900)  # Caches force plate pull data for 15 minutes to save bandwidth
def fetch_hawkins_force_data():
    try:
        # Split your structured token key into Client ID and Secret components
        # Hawkins keys typically format as: ClientID.ClientSecret
        api_key_string = HAWKINS_KEY
        if "." not in api_key_string:
            return None
            
        client_id, client_secret = api_key_string.split(".", 1)
        
        # Standard OAuth2 basic authentication payload exchange configuration
        token_payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        
        token_response = requests.post(
            HAWKINS_TOKEN_URL, 
            json=token_payload, 
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if token_response.status_code != 200:
            return None
            
        access_token = token_response.json().get("access_token", token_response.json().get("token"))
        if not access_token:
            return None
            
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        # Pull fresh daily force metrics down from the cloud sync
        test_response = requests.get(f"{HAWKINS_API_URL}/tests", headers=headers, timeout=10)
        if test_response.status_code != 200:
            return None
            
        raw_tests = test_response.json().get("data", [])
        
        parsed_records = []
        for test in raw_tests:
            athlete_name = test.get("athlete", {}).get("name", "")
            metrics = test.get("metrics", {})
            
            # Map precise force metrics out of the JSON response array
            parsed_records.append({
                'Match_Key': str(athlete_name).strip().upper(),
                'Jump Height': float(metrics.get("jump_height", metrics.get("vertical_jump_in", 0.0))),
                'mRSI': float(metrics.get("mrsi", metrics.get("rsi_modified", 0.0)))
            })
            
        if len(parsed_records) == 0:
            return None
            
        df_hawk = pd.DataFrame(parsed_records)
        df_hawk = df_hawk.groupby('Match_Key').agg({'Jump Height': 'max', 'mRSI': 'max'}).reset_index()
        return df_hawk
    except:
        return None
