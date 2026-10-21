"""
Live NAV Data Fetcher via AMFI / mfapi.in REST API.

Connects to the public mutual fund API (https://api.mfapi.in/mf/{amfi_code})
to stream real-time Net Asset Values, fund metadata, and historical daily points.
"""

import os
import requests
import pandas as pd


def fetch_live_nav(scheme_code: int = 125497):
    """
    Fetches real-time Net Asset Value (NAV) records and fund house metadata
    from mfapi.in for a specified AMFI scheme code and writes data/raw/live_nav.csv.

    Args:
        scheme_code (int): The AMFI code of the scheme to query. Defaults to 125497.

    Returns:
        bool: True if data was successfully fetched and persisted; False otherwise.
    """
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    print(f"[LiveNAV] Querying mfapi.in endpoint for scheme {scheme_code}...")

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            payload = response.json()
            meta = payload.get("meta", {})
            nav_data = payload.get("data", [])

            if nav_data:
                df = pd.DataFrame(nav_data)
                df['fund_house'] = meta.get('fund_house')
                df['scheme_type'] = meta.get('scheme_type')
                df['scheme_category'] = meta.get('scheme_category')
                df['scheme_code'] = meta.get('scheme_code')
                df['scheme_name'] = meta.get('scheme_name')

                os.makedirs("data/raw", exist_ok=True)
                df.to_csv("data/raw/live_nav.csv", index=False)
                print(f"[LiveNAV] Successfully ingested {len(df)} live NAV records to data/raw/live_nav.csv")
                return True
            else:
                print("[LiveNAV] Warning: Response returned empty NAV data array.")
                return False
        else:
            print(f"[LiveNAV] HTTP request failed with status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as exc:
        print(f"[LiveNAV] Network communication error encountered: {exc}")
        return False


if __name__ == "__main__":
    fetch_live_nav()
