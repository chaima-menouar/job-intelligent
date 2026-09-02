import pandas as pd
import os

# قراءة curated data
df = pd.read_csv("data_lake/curated/jobs_with_skills.csv")

# إنشاء folder output
os.makedirs("warehouse/output", exist_ok=True)

# -------------------------
# dim_company
# -------------------------
dim_company = df[["company"]].drop_duplicates().reset_index(drop=True)
dim_company["company_id"] = dim_company.index + 1
dim_company = dim_company[["company_id", "company"]]
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_PATH = BASE_DIR / "data_lake" / "curated" / "jobs_with_skills.csv"
JOB_SKILLS_PATH = BASE_DIR / "data_lake" / "curated" / "job_skills.csv"
OUTPUT_DIR = BASE_DIR / "warehouse" / "output"


def build_dimension(dataframe, column, id_column):
    dimension = dataframe[[column]].copy()
    dimension[column] = dimension[column].fillna("Unknown")
    dimension[column] = dimension[column].replace("", "Unknown")
    dimension = dimension.drop_duplicates().reset_index(drop=True)
    dimension[id_column] = dimension.index + 1

    return dimension[[id_column, column]]


def main():
    jobs = pd.read_csv(JOBS_PATH)
    job_skills = pd.read_csv(JOB_SKILLS_PATH)

    jobs["source_job_id"] = jobs["source_job_id"].astype(str)
    job_skills["source_job_id"] = job_skills["source_job_id"].astype(str)

    jobs = jobs.drop_duplicates(
        subset=["source", "source_job_id"]
    ).reset_index(drop=True)

    jobs["job_id"] = jobs.index + 1

    dim_company = build_dimension(
        jobs,
        "company",
        "company_id",
    )

    dim_location = build_dimension(
        jobs,
        "location",
        "location_id",
    )

    dim_skills = build_dimension(
        job_skills,
        "skill",
        "skill_id",
    )

    fact_jobs = jobs.merge(
        dim_company,
        on="company",
        how="left",
    ).merge(
        dim_location,
        on="location",
        how="left",
    )

    fact_jobs = fact_jobs[
        [
            "job_id",
            "source",
            "source_job_id",
            "job_title",
            "company_id",
            "location_id",
            "category",
            "job_type",
            "publication_date",
            "salary",
            "job_url",
        ]
    ]

    bridge_job_skills = job_skills.merge(
        jobs[["source", "source_job_id", "job_id"]],
        on=["source", "source_job_id"],
        how="inner",
    ).merge(
        dim_skills,
        on="skill",
        how="inner",
    )

    bridge_job_skills = bridge_job_skills[
        ["job_id", "skill_id"]
    ].drop_duplicates()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dim_company.to_csv(
        OUTPUT_DIR / "dim_company.csv",
        index=False,
    )

    dim_location.to_csv(
        OUTPUT_DIR / "dim_location.csv",
        index=False,
    )

    dim_skills.to_csv(
        OUTPUT_DIR / "dim_skills.csv",
        index=False,
    )

    fact_jobs.to_csv(
        OUTPUT_DIR / "fact_jobs.csv",
        index=False,
    )

    bridge_job_skills.to_csv(
        OUTPUT_DIR / "bridge_job_skills.csv",
        index=False,
    )

    print(f"Created warehouse with {len(fact_jobs)} jobs")


if __name__ == "__main__":
    main()
# -------------------------
# dim_location
# -------------------------
dim_location = df[["location"]].drop_duplicates().reset_index(drop=True)
dim_location["location_id"] = dim_location.index + 1
dim_location = dim_location[["location_id", "location"]]

# -------------------------
# dim_skills
# -------------------------
all_skills = (
    df["skills"]
    .fillna("")
    .str.split(",")
    .explode()
    .str.strip()
)
all_skills = all_skills[all_skills != ""].drop_duplicates().reset_index(drop=True)

dim_skills = pd.DataFrame({"skill": all_skills})
dim_skills["skill_id"] = dim_skills.index + 1
dim_skills = dim_skills[["skill_id", "skill"]]

# -------------------------
# fact_jobs
# -------------------------
fact_jobs = df.copy()

# ربط company_id
fact_jobs = fact_jobs.merge(dim_company, on="company", how="left")

# ربط location_id
fact_jobs = fact_jobs.merge(dim_location, on="location", how="left")

# job_id
fact_jobs["job_id"] = range(1, len(fact_jobs) + 1)

# اختيار الأعمدة المهمة
fact_jobs = fact_jobs[
    ["job_id", "job_title", "estimated_salary", "company_id", "location_id", "skills"]
]

# -------------------------
# حفظ الجداول
# -------------------------
dim_company.to_csv("warehouse/output/dim_company.csv", index=False)
dim_location.to_csv("warehouse/output/dim_location.csv", index=False)
dim_skills.to_csv("warehouse/output/dim_skills.csv", index=False)
fact_jobs.to_csv("warehouse/output/fact_jobs.csv", index=False)

print("Data warehouse tables created successfully")
