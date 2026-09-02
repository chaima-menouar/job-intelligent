import json
from datetime import datetime, timezone
from pathlib import Path

import requests


API_URL = "https://remotive.com/api/remote-jobs"
PARAMS = {
    "search": "data",
    "limit": 100,
}

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_PATH = BASE_DIR / "data_lake" / "raw" / "jobs_remotive.json"


def fetch_jobs():
    response = requests.get(
        API_URL,
        params=PARAMS,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    jobs = data.get("jobs")

    if not isinstance(jobs, list):
        raise ValueError("Invalid response: jobs list is missing")

    return {
        "source": "Remotive",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "job_count": len(jobs),
        "jobs": jobs,
    }


def save_jobs(data):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def main():
    data = fetch_jobs()
    save_jobs(data)
    print(f"Saved {data['job_count']} jobs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
