import streamlit as st
import pandas as pd
import PyPDF2
import docx
import io
import matplotlib.pyplot as plt
from collections import Counter
import spacy
import nltk

# NLTK stopwords download
nltk.download('stopwords')
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Page Config
st.set_page_config(page_title=" Job Recommendation", page_icon="💼", layout="wide")

# Load Jobs Dataset
jobs_df = pd.read_csv("dummy_csv_jobs.csv")

# Predefined Skills List
skills_list = [
    "python", "java", "sql", "excel", "finance",
    "accounting", "machine learning", "statistics",
    "problem solving", "tally", "communication",
    "data analysis"
]

# Resume extract functions
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

# NLP-based skill extraction
def nlp_extract_skills(text):
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and token.text not in stop_words]
    extracted_skills = [skill for skill in skills_list if skill in tokens]
    return list(set(extracted_skills))  # unique skills

# Header
st.markdown("<h1 style='text-align:center;color:#2C3E50;'>💼 Job Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#16A085;'>Choose an input method and get  job recommendations 🚀</p>", unsafe_allow_html=True)

# User input method
option = st.radio("Select Input Method", ["✍️ Enter Skills", "📂 Upload Resume"])
user_skills = []

if option == "✍️ Enter Skills":
    skill_input = st.text_area("Enter your skills (comma separated)", "")
    if skill_input:
        text = skill_input.lower()
        user_skills = nlp_extract_skills(text)

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

# Matching logic
if user_skills:
    def calculate_match(job_skills, user_skills):
        job_tokens = [token.strip().lower() for token in job_skills.split(",")]
        matched = set(job_tokens).intersection(set(user_skills))
        match_percent = (len(matched)/len(job_tokens))*100 if job_tokens else 0
        return matched, match_percent

    matched_skills_list, match_percent_list = [], []

    for idx, row in jobs_df.iterrows():
        matched, percent = calculate_match(row["Required Skills"], user_skills)
        matched_skills_list.append(", ".join(matched) if matched else "None")
        match_percent_list.append(percent)

    jobs_df["Matched Skills"] = matched_skills_list
    jobs_df["Match %"] = match_percent_list

    # Display jobs
    st.markdown("## 🔎 Top Recommended Jobs")
    top_jobs = jobs_df.sort_values(by="Match %", ascending=False)
    for idx, row in top_jobs.iterrows():
        st.markdown(
            f"""
            <div style="padding:15px;margin:10px 0;border-radius:10px;
                        background-color:#ECF0F1;border-left:6px solid #3498DB;">
                <h4 style="color:#2C3E50;margin:0;">{row['Job Title']} at {row['Company']}</h4>
                <p style="color:#2C3E50;margin:2px 0;"><b>📍 Location:</b> {row['Location']}</p>
                <p style="color:#2C3E50;margin:2px 0;"><b>✅ Matched Skills:</b> {row['Matched Skills']}</p>
                <p style="color:#2C3E50;margin:2px 0;"><b>📊 Match Percentage:</b> {row['Match %']:.0f}%</p>
            </div>
            """, unsafe_allow_html=True
        )

    # Visualizations
    st.markdown("## 📊 Visual Insights")

    # Horizontal Bar Chart
    st.markdown("### 📌 Job-wise Match %")
    fig, ax = plt.subplots(figsize=(8,4))
    ax.barh(top_jobs["Job Title"], top_jobs["Match %"], color="#3498DB")
    ax.set_xlabel("Match Percentage")
    ax.set_ylabel("Job Title")
    ax.set_title("Job Match Percentage")
    st.pyplot(fig)

    # Pie Chart for best job
    st.markdown("### 🥧 Skill Match Breakdown (Best Job)")
    best_job = top_jobs.iloc[0]
    matched_count = len(best_job["Matched Skills"].split(", ")) if best_job["Matched Skills"] != "None" else 0
    total_required = len(best_job["Required Skills"].split(","))
    unmatched_count = total_required - matched_count
    fig2, ax2 = plt.subplots()
    ax2.pie([matched_count, unmatched_count], labels=["Matched Skills","Unmatched Skills"], autopct="%1.1f%%", colors=["#2ECC71","#E74C3C"])
    ax2.set_title(f"Skill Match for {best_job['Job Title']}")
    st.pyplot(fig2)

    # Bar Chart for top matched skills
    st.markdown("### 📊 Most Frequently Matched Skills")
    all_matched_skills=[]
    for skills in jobs_df["Matched Skills"]:
        if skills!="None":
            all_matched_skills.extend(skills.split(", "))
    if all_matched_skills:
        skill_counts=Counter(all_matched_skills)
        fig3,ax3=plt.subplots()
        ax3.bar(skill_counts.keys(),skill_counts.values(),color="#9B59B6")
        ax3.set_xlabel("Skills")
        ax3.set_ylabel("Frequency")
        ax3.set_title("Top Matched Skills Across Jobs")
        st.pyplot(fig3)

else:
    st.info("👉 Enter your skills or upload a resume to get a job recommendations.")

