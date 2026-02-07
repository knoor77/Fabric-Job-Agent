
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
    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    jobs = data.get('jobs_results', [])
    
    # DEBUG: Print the titles of found jobs to the GitHub Log
    print(f"Total jobs found by API: {len(jobs)}")
    for j in jobs:
        print(f"Found: {j.get('title')} at {j.get('company_name')}")
        
    return jobs

if __name__ == "__main__":
    all_found_jobs = fetch_jobs()
    file_name = 'daily_jobs.csv'
    
    # Prepare new data
    new_rows = []
    for j in all_found_jobs:
        new_rows.append({
            "Date Found": datetime.now().strftime("%Y-%m-%d"),
            "Title": j.get("title"),
            "Company": j.get("company_name"),
            "Location": j.get("location"),
            "Link": j.get("related_links", [{}])[0].get("link")
        })

    if new_rows:
        df_final = pd.DataFrame(new_rows)
        # We are overwriting the file this time to force a refresh
        df_final.to_csv(file_name, index=False)
        print(f"Successfully wrote {len(new_rows)} jobs to {file_name}")
    else:
        print("API returned zero jobs for this query.")
