import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

app_id = os.getenv("ADZUNA_APP_ID")
app_key = os.getenv("ADZUNA_APP_KEY")

if not app_id or not app_key:
    raise RuntimeError(
        "ADZUNA_APP_ID and ADZUNA_APP_KEY must be configured."
    )

url = "https://api.adzuna.com/v1/api/jobs/us/search/1"

params = {
    "app_id": app_id,
    "app_key": app_key,
    "what": "data",
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

data = response.json()

project_root = Path(__file__).resolve().parents[2]
output_path = project_root / "data_lake" / "raw" / "jobs_adzuna.json"
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

print("Adzuna jobs data saved successfully.")
