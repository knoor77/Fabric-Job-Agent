import os
import json
import requests
import pandas as pd
from datetime import datetime

with open('settings.json', 'r') as f:
    settings = json.load(f)

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def fetch_jobs():
    query = settings['search_query']
    print(f"Executing search for: {query}")
    
    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    return data.get('jobs_results', [])

if __name__ == "__main__":
    found_jobs = fetch_jobs()
    file_name = 'daily_jobs.csv'
    
    if os.path.exists(file_name):
        df_old = pd.read_csv(file_name)
    else:
        df_old = pd.DataFrame(columns=["Date Found", "Title", "Company", "Location", "Link"])

    new_entries = []
    for j in found_jobs:
        link = j.get("related_links", [{}])[0].get("link")
        # Check if this link is already in our CSV
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
        # Add new jobs to the top
        df_final = pd.concat([df_new, df_old], ignore_index=True)
        df_final.to_csv(file_name, index=False)
        print(f"Success: Added {len(new_entries)} new jobs.")
    else:
        print("Search complete. No new unique jobs found today.")
