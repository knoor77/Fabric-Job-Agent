import os
import json
import requests
import pandas as pd
from datetime import datetime

# Load Settings
with open('settings.json', 'r') as f:
    settings = json.load(f)

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def fetch_jobs():
    # If companies list is empty, just use the search_query
    query = settings['search_query']
    if settings.get('companies'):
        query += f" {' OR '.join(settings['companies'])}"
    
    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        return response.json().get('jobs_results', [])
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

if __name__ == "__main__":
    all_found_jobs = fetch_jobs()
    file_name = 'daily_jobs.csv'
    
    if os.path.exists(file_name):
        try:
            df_old = pd.read_csv(file_name)
        except:
            df_old = pd.DataFrame(columns=["Date Found", "Title", "Company", "Location", "Link"])
    else:
        df_old = pd.DataFrame(columns=["Date Found", "Title", "Company", "Location", "Link"])

    new_entries = []
    for j in all_found_jobs:
        link = j.get("related_links", [{}])[0].get("link")
        if link and link not in df_old['Link'].values:
            new_entries.append({
                "Date Found": datetime.now().strftime("%Y-%m-%d"),
                "Title": j.get("title"),
                "Company": j.get("company_name"),
                "Location": j.get("location"),
                "Link": link
            })

    if new_entries:
        df_new = pd.DataFrame(new_entries)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
        df_final = df_final.sort_values(by="Date Found", ascending=False)
        df_final.to_csv(file_name, index=False)
        print(f"Success: Added {len(new_entries)} new jobs.")
    else:
        print("No new jobs found today.")
