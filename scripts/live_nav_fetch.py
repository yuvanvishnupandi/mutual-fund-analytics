import requests
import pandas as pd
import os

def fetch_live_nav():
    url = "https://api.mfapi.in/mf/125497"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        meta = data.get("meta", {})
        nav_data = data.get("data", [])
        
        if nav_data:
            df = pd.DataFrame(nav_data)
            df['fund_house'] = meta.get('fund_house')
            df['scheme_type'] = meta.get('scheme_type')
            df['scheme_category'] = meta.get('scheme_category')
            df['scheme_code'] = meta.get('scheme_code')
            df['scheme_name'] = meta.get('scheme_name')
            
            os.makedirs("data/raw", exist_ok=True)
            df.to_csv("data/raw/live_nav.csv", index=False)
            print("Successfully saved live NAV data to data/raw/live_nav.csv")
        else:
            print("No NAV data found in the response.")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")

if __name__ == "__main__":
    fetch_live_nav()
