from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
WAREHOUSE_DIR = BASE_DIR / "warehouse" / "output"


st.set_page_config(
    page_title="Job Market Intelligence",
    page_icon="",
    layout="wide",
)


@st.cache_data
def load_data():
    jobs = pd.read_csv(WAREHOUSE_DIR / "fact_jobs.csv")
    companies = pd.read_csv(WAREHOUSE_DIR / "dim_company.csv")
    locations = pd.read_csv(WAREHOUSE_DIR / "dim_location.csv")
    skills = pd.read_csv(WAREHOUSE_DIR / "dim_skills.csv")
    job_skills = pd.read_csv(
        WAREHOUSE_DIR / "bridge_job_skills.csv"
    )

    jobs = jobs.merge(
        companies,
        on="company_id",
        how="left",
    ).merge(
        locations,
        on="location_id",
        how="left",
    )

    jobs["publication_date"] = pd.to_datetime(
        jobs["publication_date"],
        errors="coerce",
        utc=True,
    )

    return jobs, skills, job_skills


jobs, skills, job_skills = load_data()


st.title("Job Market Intelligence")
st.caption(
    "Analysis of job market trends, required skills, "
    "companies, locations, and employment types."
)


st.sidebar.header("Filters")

keyword = st.sidebar.text_input("Search by job title")

selected_locations = st.sidebar.multiselect(
    "Locations",
    sorted(jobs["location"].dropna().unique()),
)

selected_job_types = st.sidebar.multiselect(
    "Job types",
    sorted(jobs["job_type"].dropna().unique()),
)

selected_skills = st.sidebar.multiselect(
    "Skills",
    sorted(skills["skill"].dropna().unique()),
)


filtered_jobs = jobs.copy()

if keyword:
    filtered_jobs = filtered_jobs[
        filtered_jobs["job_title"].str.contains(
            keyword,
            case=False,
            na=False,
        )
    ]

if selected_locations:
    filtered_jobs = filtered_jobs[
        filtered_jobs["location"].isin(selected_locations)
    ]

if selected_job_types:
    filtered_jobs = filtered_jobs[
        filtered_jobs["job_type"].isin(selected_job_types)
    ]

if selected_skills:
    selected_skill_ids = skills[
        skills["skill"].isin(selected_skills)
    ]["skill_id"]

    matching_job_ids = job_skills[
        job_skills["skill_id"].isin(selected_skill_ids)
    ]["job_id"].unique()

    filtered_jobs = filtered_jobs[
        filtered_jobs["job_id"].isin(matching_job_ids)
    ]


if filtered_jobs.empty:
    st.warning("No jobs match the selected filters.")
    st.stop()


filtered_job_skills = job_skills[
    job_skills["job_id"].isin(filtered_jobs["job_id"])
].merge(
    skills,
    on="skill_id",
    how="left",
)


metric_1, metric_2, metric_3, metric_4 = st.columns(4)

metric_1.metric(
    "Available jobs",
    f"{len(filtered_jobs):,}",
)

metric_2.metric(
    "Companies",
    f"{filtered_jobs['company'].nunique():,}",
)

metric_3.metric(
    "Locations",
    f"{filtered_jobs['location'].nunique():,}",
)

metric_4.metric(
    "Detected skills",
    f"{filtered_job_skills['skill'].nunique():,}",
)


top_skills = (
    filtered_job_skills["skill"]
    .value_counts()
    .head(15)
    .sort_values()
    .reset_index()
)

top_skills.columns = ["skill", "jobs"]

top_locations = (
    filtered_jobs["location"]
    .value_counts()
    .head(10)
    .sort_values()
    .reset_index()
)

top_locations.columns = ["location", "jobs"]


left_chart, right_chart = st.columns(2)

with left_chart:
    st.subheader("Most requested skills")

    skills_chart = px.bar(
        top_skills,
        x="jobs",
        y="skill",
        orientation="h",
        color="jobs",
        color_continuous_scale="Blues",
    )

    skills_chart.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Number of jobs",
        yaxis_title="",
    )

    st.plotly_chart(
        skills_chart,
        use_container_width=True,
    )


with right_chart:
    st.subheader("Top locations")

    locations_chart = px.bar(
        top_locations,
        x="jobs",
        y="location",
        orientation="h",
        color="jobs",
        color_continuous_scale="Purples",
    )

    locations_chart.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Number of jobs",
        yaxis_title="",
    )

    st.plotly_chart(
        locations_chart,
        use_container_width=True,
    )


chart_1, chart_2 = st.columns(2)

with chart_1:
    st.subheader("Jobs by employment type")

    job_type_data = (
        filtered_jobs["job_type"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    job_type_data.columns = ["job_type", "jobs"]

    job_type_chart = px.pie(
        job_type_data,
        names="job_type",
        values="jobs",
        hole=0.55,
    )

    st.plotly_chart(
        job_type_chart,
        use_container_width=True,
    )


with chart_2:
    st.subheader("Jobs by source")

    source_data = (
        filtered_jobs["source"]
        .value_counts()
        .reset_index()
    )

    source_data.columns = ["source", "jobs"]

    source_chart = px.bar(
        source_data,
        x="source",
        y="jobs",
        color="source",
    )

    source_chart.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Number of jobs",
    )

    st.plotly_chart(
        source_chart,
        use_container_width=True,
    )


st.subheader("Latest job opportunities")

latest_jobs = filtered_jobs.sort_values(
    "publication_date",
    ascending=False,
).head(25)

st.dataframe(
    latest_jobs[
        [
            "job_title",
            "company",
            "location",
            "job_type",
            "salary",
            "publication_date",
            "job_url",
        ]
    ],
    use_container_width=True,
    hide_index=True,
    column_config={
        "job_url": st.column_config.LinkColumn(
            "Job link",
            display_text="Open",
        ),
        "publication_date": st.column_config.DatetimeColumn(
            "Published",
            format="YYYY-MM-DD",
        ),
    },
)
