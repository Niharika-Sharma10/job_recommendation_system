# app.py - Streamlit Job Recommender (Dark Mode + ML + Animation + Visualization)
import streamlit as st
import pandas as pd
import numpy as np
import io, os, pickle
import PyPDF2
import nltk
import spacy
import matplotlib.pyplot as plt
import requests

from docx import Document
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from streamlit_lottie import st_lottie


# --------------------------
# Setup
# --------------------------
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)

stop_words = set(stopwords.words("english"))


try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    from spacy.lang.en import English
    nlp = English()

st.set_page_config(page_title="💼 AI Job Recommender", page_icon="💡", layout="wide")

# --------------------------
# Custom CSS
# --------------------------
st.markdown("""
<style>
.stApp { background-color:#0e1117; color:#e6edf3; font-family:'Segoe UI',Roboto,Arial,sans-serif; }
.header-card {
  background:linear-gradient(90deg,#111418,#1b2228);
  border-radius:14px; padding:22px;
  box-shadow:0 6px 24px rgba(0,0,0,0.6);
  margin-bottom:18px;
}
.header-card h1 { color:#00d6a6; margin:0 0 6px 0; font-size:2.1rem; }
.header-card p { color:#bfc8cf; margin:0; }
.job-card {
  background:#14181c; border-radius:12px;
  padding:14px; margin:12px 0;
  box-shadow:0 4px 18px rgba(0,0,0,0.55);
}
.job-card h4 { color:#5ef3d9; margin:0 0 6px 0; }
.job-card p { color:#c6d0d6; margin:4px 0; }
.pill { display:inline-block; padding:6px 10px; border-radius:999px; background:#20262b;
  color:#9fead3; font-weight:600; margin-right:8px; font-size:12px; }
[role="alert"], .stAlert, .stException { display:none !important; }
</style>
""", unsafe_allow_html=True)

# --------------------------
# Helper Functions
# --------------------------
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

def detect_skill_column(df):
    for col in df.columns:
        if "skill" in col.lower() or "required" in col.lower():
            return col
    for col in ["required_skills","skills","skills_required","skillset"]:
        if col in df.columns: return col
    return None

def load_jobs_df():
    for name in ["jobs_cleaned.csv","jobs_cleaned_small.csv","jobs.csv"]:
        if os.path.exists(name):
            try: return pd.read_csv(name).fillna("")
            except: continue
    return pd.DataFrame(columns=["job_title","company","location","required_skills","description"])

@st.cache_resource
def load_vectorizer_and_job_vectors(df, skill_col):
    vectorizer = None
    if os.path.exists("vectorizer.pkl"):
        with open("vectorizer.pkl","rb") as f:
            vectorizer = pickle.load(f)
    else:
        vectorizer = CountVectorizer(stop_words="english")

    if skill_col:
        texts = df[skill_col].astype(str).fillna("")
        job_vectors = vectorizer.fit_transform(texts)
        with open("vectorizer.pkl","wb") as f:
            pickle.dump(vectorizer,f)
    else:
        job_vectors = None
    return vectorizer, job_vectors

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for p in reader.pages:
        t = p.extract_text()
        if t: text += t + " "
    return text

def extract_text_from_docx(file):
    file_bytes = io.BytesIO(file.read())
    doc = docx.Document(file_bytes)
    return " ".join([p.text for p in doc.paragraphs])

def nlp_extract_skills_from_text(text, skills_list):
    text = text.lower()
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if token.is_alpha and token.text.lower() not in stop_words]
    extracted = []
    for skill in skills_list:
        for tok in tokens:
            if skill in tok or tok in skill:
                extracted.append(skill)
                break
    return list(set(extracted))

def calculate_match(job_skill_text, user_skill_tokens):
    job_tokens = [s.strip().lower() for s in str(job_skill_text).split(",") if s.strip()]
    matched = set(user_skill_tokens).intersection(set(job_tokens))
    match_percent = round((len(matched)/len(user_skill_tokens)*100) if user_skill_tokens else 0, 2)
    return matched, match_percent

# --------------------------
# Load ML Components
# --------------------------
jobs_df = load_jobs_df()
skill_col = detect_skill_column(jobs_df)
vectorizer, job_vectors = load_vectorizer_and_job_vectors(jobs_df, skill_col)

# --------------------------
# Header + Animation + Images
# --------------------------
with st.container():
    st.markdown("""
        <div class="header-card">
            <h1>💼 Job Recommendation System — ML Powered</h1>
            <p>Upload your resume or enter your skills to get AI-powered job suggestions.</p>
        </div>
    """, unsafe_allow_html=True)

    lottie_job = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_3rwasyjy.json")
    st_lottie(lottie_job, height=280, key="job_anim")

col1, col2 = st.columns(2)
with col1:
    st.image("https://www.artech.com/wp-content/uploads/2025/06/thumbnail_Job-Search-Burnout-is-Real-Here-is-How-to-Stay-Strong-and-Focused.jpg",
             caption="Stay Focused on Your Job Hunt", use_container_width=True)
with col2:
    st.image("https://jobsgaar.com/blog/wp-content/uploads/2021/07/bigstock-170353778.jpg",
             caption="Find the Right Opportunity", use_container_width=True)

st.write("")

# --------------------------
# Input Section
# --------------------------
option = st.radio("Choose Input Method", ["✍️ Enter Skills", "📂 Upload Resume"], horizontal=True)
user_skills = []
skills_list_small = ["python","java","sql","excel","finance","machine learning","nlp","aws","azure",
                     "communication","pandas","numpy","tensorflow","deep learning","problem solving"]

if option == "✍️ Enter Skills":
    skill_input = st.text_area("Enter your skills (comma separated):", placeholder="python, sql, excel, communication")
    if skill_input:
        user_skills = [s.strip().lower() for s in skill_input.split(",") if s.strip()]
elif option == "📂 Upload Resume":
    uploaded_file = st.file_uploader("Upload your resume (pdf/docx)", type=["pdf","docx"])
    if uploaded_file:
        full_text = extract_text_from_pdf(uploaded_file) if uploaded_file.name.endswith(".pdf") else extract_text_from_docx(uploaded_file)
        user_skills = nlp_extract_skills_from_text(full_text, skills_list_small)
        st.success(f"Extracted Skills: {', '.join(user_skills)}")

# --------------------------
# ML Matching Logic
# --------------------------
def rank_jobs(user_skills_tokens):
    df = jobs_df.copy()
    matched_list, match_percent_list = [], []
    for idx, row in df.iterrows():
        matched, percent = calculate_match(row.get(skill_col,""), user_skills_tokens)
        matched_list.append(", ".join(matched))
        match_percent_list.append(percent)
    df["Matched Skills"] = matched_list
    df["Match %"] = match_percent_list

    if job_vectors is not None and vectorizer is not None and len(user_skills_tokens)>0:
        user_text = ", ".join(user_skills_tokens)
        user_vec = vectorizer.transform([user_text])
        sim_scores = cosine_similarity(user_vec, job_vectors).flatten()
        df["ML Score"] = sim_scores
        df["Final Score"] = 0.6*df["ML Score"] + 0.4*(df["Match %"]/100)
    else:
        df["ML Score"] = 0.0
        df["Final Score"] = df["Match %"]/100

    df = df.sort_values(by="Final Score", ascending=False)
    return df

# --------------------------
# Display Results
# --------------------------
if user_skills:
    ranked = rank_jobs(user_skills)
    if ranked.empty:
        st.warning("No jobs matched. Try adding more relevant skills.")
    else:
        st.markdown("## 🔍 Top Job Recommendations")
        top_jobs = ranked.head(10)
        for _, row in top_jobs.iterrows():
            st.markdown(f"""
            <div class="job-card">
                <h4>{row.get('job_title','N/A')}</h4>
                <p>🏢 {row.get('company','Unknown')} | 📍 {row.get('location','Remote')}</p>
                <p><span class="pill">✅ Matched: {row['Matched Skills']}</span>
                <span class="pill">🤖 ML Score: {row['ML Score']:.2f}</span>
                <span class="pill">📊 Final: {row['Final Score']:.2f}</span></p>
            </div>
            """, unsafe_allow_html=True)

        # --------------------------
        # Visualization Section
        # --------------------------
        st.write("")
        if st.button("📊 View Analysis"):
            st.markdown("### 📈 Job Matching Analysis")

            matched_total = sum([len(str(x).split(",")) for x in top_jobs["Matched Skills"]])
            unmatched_total = max(0, len(user_skills)*len(top_jobs) - matched_total)
            fig1, ax1 = plt.subplots(facecolor="#0e1117")
            ax1.set_facecolor("#0e1117")
            ax1.pie(
                [matched_total, unmatched_total],
                labels=["Matched", "Unmatched"],
                autopct="%1.1f%%",
                startangle=90,
                colors=["#00d6a6", "#d946ef"],
                textprops={"color": "white", "fontsize": 12}
            )
            ax1.axis("equal")
            st.pyplot(fig1)

            fig2, ax2 = plt.subplots(facecolor="#0e1117")
            ax2.set_facecolor("#0e1117")
            ax2.bar(top_jobs["job_title"], top_jobs["Match %"], color="#00d6a6", alpha=0.8)
            ax2.set_xlabel("Job Title", color="white")
            ax2.set_ylabel("Match %", color="white")
            ax2.set_title("Skill Match Percentage per Job", color="white")
            ax2.tick_params(axis="x", colors="white", rotation=45)
            ax2.tick_params(axis="y", colors="white")
            st.pyplot(fig2)

            all_matched_skills = [skill.strip() for sublist in top_jobs["Matched Skills"] for skill in str(sublist).split(",") if skill.strip()]
            freq = Counter(all_matched_skills)
            if freq:
                fig3, ax3 = plt.subplots(facecolor="#0e1117")
                ax3.set_facecolor("#0e1117")
                skills, counts = zip(*freq.items())
                ax3.barh(skills, counts, color="#5ef3d9")
                ax3.set_xlabel("Frequency", color="white")
                ax3.set_ylabel("Skills", color="white")
                ax3.set_title("Matched Skill Frequency Across Top Jobs", color="white")
                ax3.tick_params(axis="x", colors="white")
                ax3.tick_params(axis="y", colors="white")
                st.pyplot(fig3)

else:
    st.info("👉 Start by entering your skills or uploading your resume.")

# --------------------------
# --------------------------
