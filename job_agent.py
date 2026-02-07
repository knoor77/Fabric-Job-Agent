import os
import json
import requests
import pandas as pd
from datetime import datetime

# 1. Load your search terms from the settings file you just made
with open('settings.json', 'r') as f:
    settings = json.load(f)

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MY_EMAIL = os.getenv("MY_EMAIL")

def send_email_summary(new_jobs):
    if not new_jobs:
        print("No new jobs to email.")
        return

    job_list_html = "".join([
        f"<li><b>{j.get('title')}</b> at {j.get('company_name')} ({j.get('location')})<br><a href='{j.get('related_links', [{}])[0].get('link', '#')}'>View Job</a></li><br>"
        for j in new_jobs
    ])

    email_data = {
        "personalizations": [{"to": [{"email": MY_EMAIL}]}],
        "from": {"email": MY_EMAIL}, 
        "subject": f"🎯 {len(new_jobs)} New Fabric R&D/GTM Roles Found - {datetime.now().strftime('%Y-%m-%d')}",
        "content": [{"type": "text/html", "value": f"<h3>New opportunities found today:</h3><ul>{job_list_html}</ul>"}]
    }
    
    requests.post("https://api.sendgrid.com/v3/mail/send", 
                  headers={"Authorization": f"Bearer {SENDGRID_API_KEY}"}, 
                  json=email_data)

def fetch_jobs():
    query = f"{settings['search_query']} {' OR '.join(settings['companies'])}"
    params = {"engine": "google_jobs", "q": query, "hl": "en", "api_key": SERPAPI_KEY}
    response = requests.get("https://serpapi.com/search", params=params)
    return response.json().get('jobs_results', [])

if __name__ == "__main__":
    all_found_jobs = fetch_jobs()
    file_name = 'daily_jobs.csv'
    
    # Check what we already have in our list
    if os.path.exists(file_name):
        df_old = pd.read_csv(file_name)
        old_links = df_old['Link'].tolist()
    else:
        df_old = pd.DataFrame(columns=["Date Found", "Title", "Company", "Location", "Link", "Status"])
        old_links = []

    # Identify only the truly NEW jobs
    new_entries = []
    new_to_report = []
    
    for j in all_found_jobs:
        link = j.get("related_links", [{}])[0].get("link")
        if link not in old_links:
            job_data = {
                "Date Found": datetime.now().strftime("%Y-%m-%d"),
                "Title": j.get("title"),
                "Company": j.get("company_name"),
                "Location": j.get("location"),
                "Link": link,
                "Status": "Active"
            }
            new_entries.append(job_data)
            new_to_report.append(j)

    # If new jobs found, send email and update the file
    if new_entries:
        send_email_summary(new_to_report)
        df_updated = pd.concat([df_old, pd.DataFrame(new_entries)], ignore_index=True)
        df_updated.to_csv(file_name, index=False)
        print(f"Success: {len(new_entries)} new jobs found and emailed.")
    else:
        print("Scanned, but no new jobs found today.")
