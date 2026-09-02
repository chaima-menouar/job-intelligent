import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_PATH = BASE_DIR / "data_lake" / "processed" / "jobs_processed.csv"
CURATED_DIR = BASE_DIR / "data_lake" / "curated"

JOBS_OUTPUT_PATH = CURATED_DIR / "jobs_with_skills.csv"
SKILLS_OUTPUT_PATH = CURATED_DIR / "job_skills.csv"


SKILL_PATTERNS = {
    "Python": [r"\bpython\b"],
    "SQL": [r"\bsql\b"],
    "AWS": [r"\baws\b", r"amazon web services"],
    "Azure": [r"\bazure\b"],
    "Google Cloud": [r"\bgcp\b", r"google cloud"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "Terraform": [r"\bterraform\b"],
    "Git": [r"\bgit\b"],
    "GitHub Actions": [r"github actions"],
    "Power BI": [r"power\s*bi"],
    "Tableau": [r"\btableau\b"],
    "Excel": [r"\bexcel\b"],
    "Machine Learning": [r"machine learning", r"\bml\b"],
    "Deep Learning": [r"deep learning"],
    "NLP": [r"natural language processing", r"\bnlp\b"],
    "Large Language Models": [r"large language models?", r"\bllms?\b"],
    "TensorFlow": [r"\btensorflow\b"],
    "PyTorch": [r"\bpytorch\b"],
    "Scikit-learn": [r"scikit[- ]learn", r"\bsklearn\b"],
    "Pandas": [r"\bpandas\b"],
    "Apache Spark": [r"apache spark", r"\bspark\b"],
    "Airflow": [r"apache airflow", r"\bairflow\b"],
    "Databricks": [r"\bdatabricks\b"],
    "Snowflake": [r"\bsnowflake\b"],
    "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
    "MySQL": [r"\bmysql\b"],
    "MongoDB": [r"\bmongodb\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "React": [r"\breact\b"],
}


def extract_skills(text):
    detected_skills = []

    for skill, patterns in SKILL_PATTERNS.items():
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
            detected_skills.append(skill)

    return detected_skills


def main():
    dataframe = pd.read_csv(INPUT_PATH)

    text_columns = ["job_title", "description", "tags"]

    for column in text_columns:
        if column not in dataframe.columns:
            dataframe[column] = ""

    dataframe["search_text"] = (
        dataframe[text_columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    )

    dataframe["skills_list"] = dataframe["search_text"].apply(extract_skills)
    dataframe["skills"] = dataframe["skills_list"].apply(", ".join)

    CURATED_DIR.mkdir(parents=True, exist_ok=True)

    dataframe.drop(
        columns=["search_text", "skills_list"]
    ).to_csv(JOBS_OUTPUT_PATH, index=False)

    job_skills = dataframe[
        ["source", "source_job_id", "skills_list"]
    ].explode("skills_list")

    job_skills = job_skills.rename(
        columns={"skills_list": "skill"}
    ).dropna(subset=["skill"])

    job_skills.to_csv(SKILLS_OUTPUT_PATH, index=False)

    print(f"Saved enriched jobs to {JOBS_OUTPUT_PATH}")
    print(f"Saved job-skill relations to {SKILLS_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
