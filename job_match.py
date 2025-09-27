# job_match_streamlit.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Page Config
st.set_page_config(page_title="Job Recommendation System", page_icon="💼", layout="wide")

# Header
st.title("💼 Job Recommendation System")
st.markdown("#### 🚀 Find the best jobs that match your skills")

# Load CSV
jobs_df = pd.read_csv("dummy_csv_jobs.csv")

# User input
st.markdown("### ✍️ Enter Your Skills")
user_input = st.text_input("Example: Python, Excel, Finance")

if user_input:
    user_skills = [skill.strip().lower() for skill in user_input.split(",")]

    # Matching function
    def calculate_match(job_skills, user_skills):
        job_skills_set = set([s.strip().lower() for s in job_skills.split(",")])
        user_skills_set = set(user_skills)
        matched = job_skills_set.intersection(user_skills_set)
        match_percent = (len(matched) / len(job_skills_set)) * 100 if job_skills_set else 0
        return matched, match_percent

    matched_skills_list = []
    match_percent_list = []

    for idx, row in jobs_df.iterrows():
        matched, percent = calculate_match(row["Required Skills"], user_skills)
        matched_skills_list.append(", ".join(matched) if matched else "None")
        match_percent_list.append(percent)

    jobs_df["Matched Skills"] = matched_skills_list
    jobs_df["Match %"] = match_percent_list

    # Results section
    st.subheader("🔎 Top Recommended Jobs")
    top_jobs = jobs_df.sort_values(by="Match %", ascending=False)

    for idx, row in top_jobs.iterrows():
        st.write(f"**{row['Job Title']}** at {row['Company']} — 📊 Match: {row['Match %']:.0f}%")
        st.write(f"📍 Location: {row['Location']}")
        st.write(f"✅ Matched Skills: {row['Matched Skills']}")
        st.write("---")

    # 📊 VISUALIZATIONS 

    st.subheader("📊 Visual Insights")

    # 1️⃣ Horizontal Bar Chart (Jobs vs % Match)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(top_jobs["Job Title"], top_jobs["Match %"], color="#3498DB")
    ax.set_xlabel("Match Percentage")
    ax.set_ylabel("Job Title")
    ax.set_title("Job Match Percentage")
    st.pyplot(fig)

    # 2️⃣ Pie Chart (for best job matched vs unmatched skills)
    best_job = top_jobs.iloc[0]
    matched_count = len(best_job["Matched Skills"].split(", ")) if best_job["Matched Skills"] != "None" else 0
    total_required = len(best_job["Required Skills"].split(","))
    unmatched_count = total_required - matched_count

    fig2, ax2 = plt.subplots()
    ax2.pie(
        [matched_count, unmatched_count],
        labels=["Matched Skills", "Unmatched Skills"],
        autopct="%1.1f%%",
        colors=["#2ECC71", "#E74C3C"]
    )
    ax2.set_title(f"Skill Match for {best_job['Job Title']}")
    st.pyplot(fig2)

    # 3️⃣ Bar Chart (Top matched skills frequency across jobs)
    all_matched_skills = []
    for skills in jobs_df["Matched Skills"]:
        if skills != "None":
            all_matched_skills.extend(skills.split(", "))

    if all_matched_skills:
        skill_counts = Counter(all_matched_skills)
        fig3, ax3 = plt.subplots()
        ax3.bar(skill_counts.keys(), skill_counts.values(), color="#9B59B6")
        ax3.set_xlabel("Skills")
        ax3.set_ylabel("Frequency")
        ax3.set_title("Top Matched Skills Across Jobs")
        st.pyplot(fig3)

else:
    st.info("👉 Please enter your skills to see job recommendations.")






