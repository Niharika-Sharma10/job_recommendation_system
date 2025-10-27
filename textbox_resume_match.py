import streamlit as st
import pandas as pd
import PyPDF2
import docx
import io
import matplotlib.pyplot as plt
from collections import Counter
import spacy
import nltk
from nltk.corpus import stopwords

# ----------------------------
# Libraries Setup
# ----------------------------
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Load spacy English model
nlp = spacy.load("en_core_web_sm")

# ----------------------------
# Streamlit Page Config
# ----------------------------
st.set_page_config(page_title="Job Recommendation", page_icon="💼", layout="wide")

# ----------------------------
# Load Dataset
# ----------------------------
jobs_df = pd.read_csv("jobs_cleaned.csv").fillna("")

# ----------------------------
# Predefined Skills List
# ----------------------------
skills_list = [
    "python", "java", "sql", "excel", "finance",
    "accounting", "machine learning", "statistics",
    "problem solving", "tally", "communication",
    "data analysis", "marketing", "sales"
]

# ----------------------------
# Resume / Skill Extraction
# ----------------------------
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + " "
    return text

def extract_text_from_docx(file):
    file_bytes = io.BytesIO(file.read())
    doc = docx.Document(file_bytes)
    return " ".join([para.text for para in doc.paragraphs])

def nlp_extract_skills(text):
    text = text.lower()
    doc = nlp(text)
    tokens = [token.lemma_ for token in doc if token.is_alpha and token.text not in stop_words]
    extracted_skills = []
    for skill in skills_list:
        for token in tokens:
            if skill in token or token in skill:
                extracted_skills.append(skill)
                break
    return list(set(extracted_skills))

# ----------------------------
# Streamlit UI
# ----------------------------
st.markdown("<h1 style='text-align:center;color:#2C3E50;'>💼 Job Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#16A085;'>Choose an input method and get job recommendations 🚀</p>", unsafe_allow_html=True)

option = st.radio("Select Input Method", ["✍️ Enter Skills", "📂 Upload Resume"])
user_skills = []

# ----------------------------
# User Input: Skills / Resume
# ----------------------------
if option == "✍️ Enter Skills":
    skill_input = st.text_area("Enter your skills (comma separated)", "")
    if skill_input:
        text = skill_input.lower()
        user_skills = [s.strip().lower() for s in text.split(",") if s.strip()]

elif option == "📂 Upload Resume":
    uploaded_file = st.file_uploader("Upload your Resume", type=["pdf", "docx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = extract_text_from_docx(uploaded_file)
        user_skills = nlp_extract_skills(resume_text)
        st.subheader("✅ Extracted Skills from Resume")
        st.success(", ".join(user_skills) if user_skills else "No skills found")

# ----------------------------
# Skills Matching & Job Recommendation
# ----------------------------
if user_skills:

    # ----------------------------
    # Matching Function (Matched + Unmatched + Extra)
    # ----------------------------
    def calculate_match(job_skills, user_skills):
        job_tokens = [skill.strip().lower() for skill in job_skills.split(",") if skill.strip()]
        user_tokens = [s.lower() for s in user_skills if s.strip()]

        matched = set(user_tokens).intersection(set(job_tokens))
        unmatched = set(user_tokens) - matched
        extra_job_skills = set(job_tokens) - set(user_tokens)

        match_percent = round((len(matched) / len(user_tokens) * 100) if user_tokens else 0, 2)
        return matched, unmatched, extra_job_skills, match_percent

    matched_skills_list = []
    unmatched_skills_list = []
    extra_job_skills_list = []
    match_percent_list = []

    for idx, row in jobs_df.iterrows():
        matched, unmatched, extra_skills, percent = calculate_match(row["required_skills"], user_skills)
        
        matched_skills_list.append(", ".join(matched) if matched else "None")
        unmatched_skills_list.append(", ".join(unmatched) if unmatched else "None")
        extra_job_skills_list.append(", ".join(extra_skills) if extra_skills else "None")
        match_percent_list.append(percent)

    jobs_df["Matched Skills"] = matched_skills_list
    jobs_df["Unmatched Skills"] = unmatched_skills_list
    jobs_df["Extra Job Skills"] = extra_job_skills_list
    jobs_df["Match %"] = match_percent_list

    # ----------------------------
    # Display Top 10 Recommended Jobs
    # ----------------------------
    top_jobs = jobs_df.sort_values(by="Match %", ascending=False).head(10)

    if not top_jobs.empty:
        st.markdown("## 🔎 Top 10 Recommended Jobs")
        for idx, row in top_jobs.iterrows():
            st.markdown(
                f"""
                <div style="padding:15px;margin:10px 0;border-radius:10px;
                            background-color:#ECF0F1;border-left:6px solid #3498DB;">
                    <h4 style="color:#2C3E50;margin:0;">{row['job_title']} at {row['company']}</h4>
                    <p style="color:#2C3E50;margin:2px 0;"><b>📍 Location:</b> {row['location']}</p>
                    <p style="color:#2C3E50;margin:2px 0;"><b>✅ Matched Skills:</b> {row['Matched Skills']}</p>
                    <p style="color:#2C3E50;margin:2px 0;"><b>❌ Unmatched Skills:</b> {row['Unmatched Skills']}</p>
                    <p style="color:#2C3E50;margin:2px 0;"><b>💡 Extra Job Skills:</b> {row['Extra Job Skills']}</p>
                    <p style="color:#2C3E50;margin:2px 0;"><b>📊 Match Percentage:</b> {row['Match %']:.2f}%</p>
                </div>
                """, unsafe_allow_html=True
            )

        # ----------------------------
        # Visualization 1: Match % Bar Chart
        # ----------------------------
        st.markdown("### 📌 Job-wise Match %")
        fig, ax = plt.subplots(figsize=(10,5))
        top_jobs_sorted = top_jobs.sort_values(by="Match %", ascending=True)
        ax.barh(top_jobs_sorted["job_title"], top_jobs_sorted["Match %"], color="#3498DB")
        ax.set_xlabel("Match Percentage")
        ax.set_ylabel("Job Title")
        ax.set_title("Job Match Percentage")
        st.pyplot(fig)

        # ----------------------------
        # Visualization 2: Pie Chart for Best Job
        # ----------------------------
        st.markdown("### 🥧 Skill Match Breakdown (Best Job)")
        best_job = top_jobs.iloc[0]
        matched_count = len(best_job["Matched Skills"].split(", ")) if best_job["Matched Skills"] != "None" else 0
        unmatched_count = len(best_job["Unmatched Skills"].split(", ")) if best_job["Unmatched Skills"] != "None" else 0

        fig2, ax2 = plt.subplots()
        ax2.pie(
            [matched_count, unmatched_count],
            labels=["Matched Skills", "Unmatched Skills"],
            autopct="%1.1f%%",
            colors=["#2ECC71", "#E74C3C"]
        )
        ax2.set_title(f"Skill Match for {best_job['job_title']}")
        st.pyplot(fig2)

        # ----------------------------
        # Visualization 3: Skill Frequency Across Top 10 Jobs
        # ----------------------------
        st.markdown("### 📊 Most Frequently Matched Skills")
        all_matched_skills=[]
        for skills in top_jobs["Matched Skills"]:
            if skills!="None":
                all_matched_skills.extend(skills.split(", "))
        if all_matched_skills:
            skill_counts=Counter(all_matched_skills)
            fig3,ax3=plt.subplots()
            ax3.bar(skill_counts.keys(),skill_counts.values(),color="#9B59B6")
            ax3.set_xlabel("Skills")
            ax3.set_ylabel("Frequency")
            ax3.set_title("Top Matched Skills Across Top 10 Jobs")
            st.pyplot(fig3)

    else:
        st.warning("⚠️ No matching jobs found.")
else:
    st.info("👉 Enter your skills or upload a resume to get job recommendations.")






