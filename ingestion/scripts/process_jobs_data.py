import html
import json
import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_PATH = BASE_DIR / "data_lake" / "raw" / "jobs_remotive.json"
OUTPUT_PATH = BASE_DIR / "data_lake" / "processed" / "jobs_processed.csv"


def clean_html(value):
    if not value:
        return ""

    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def process_jobs():
    with INPUT_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    records = []

    for job in data.get("jobs", []):
        records.append({
            "source": "Remotive",
            "source_job_id": job.get("id"),
            "job_title": job.get("title", ""),
            "company": job.get("company_name", ""),
            "location": job.get("candidate_required_location", ""),
            "category": job.get("category", ""),
            "job_type": job.get("job_type", ""),
            "publication_date": job.get("publication_date", ""),
            "salary": job.get("salary", ""),
            "description": clean_html(job.get("description")),
            "job_url": job.get("url", ""),
            "tags": ", ".join(job.get("tags") or []),
        })

    dataframe = pd.DataFrame(records)

    if dataframe.empty:
        raise ValueError("No jobs were found in the input file")

    dataframe = dataframe.drop_duplicates(
        subset=["source", "source_job_id"]
    )

    dataframe["publication_date"] = pd.to_datetime(
        dataframe["publication_date"],
        errors="coerce",
        utc=True,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(OUTPUT_PATH, index=False)

    print(f"Processed {len(dataframe)} jobs")
    print(f"Saved data to {OUTPUT_PATH}")


if __name__ == "__main__":
    process_jobs()
