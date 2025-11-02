import streamlit as st
import random

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="AI Career Assistant (Offline)", page_icon="💬", layout="centered")

# -----------------------------
# Animated CSS + Theme Styling + Hero Section
# -----------------------------
st.markdown("""
    <style>
    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }
    @keyframes float {
        0% {transform: translateY(0px);}
        50% {transform: translateY(-10px);}
        100% {transform: translateY(0px);}
    }

    body {
        background-color: #0e1117;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        animation: fadeIn 1.5s ease-in;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #0e1117;
        animation: fadeIn 2s ease-in-out;
    }

    /* ---- Hero Section ---- */
    .hero-image {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
        margin-top: 40px;
    }
    .hero-image img {
        width: 48%;
        max-width: 420px;
        border-radius: 20px;
        box-shadow: 0px 0px 20px rgba(177,151,252,0.5);
        transition: transform 0.5s ease;
        animation: float 6s ease-in-out infinite;
    }
    .hero-image img:hover {
        transform: scale(1.05);
    }
    .main-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        color: #b197fc;
        margin-bottom: 0.5rem;
        text-shadow: 0px 0px 15px rgba(177,151,252,0.7);
        animation: fadeIn 1.5s ease-in;
    }
    .subtitle {
        text-align: center;
        color: #ddd;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        animation: fadeIn 2s ease-in;
    }

    /* ---- Buttons ---- */
    .stButton>button {
        background-color: #262730;
        color: #ffffff;
        border-radius: 12px;
        padding: 8px 20px;
        margin: 4px;
        border: 1px solid #5e5ce6;
        box-shadow: 0 0 10px rgba(100, 100, 255, 0.4);
        transition: all 0.3s ease-in-out;
        animation: fadeIn 1s ease-in;
    }
    .stButton>button:hover {
        background-color: #5e5ce6;
        color: white;
        transform: scale(1.1);
        box-shadow: 0 0 20px rgba(120, 120, 255, 0.8);
    }

    /* ---- Input ---- */
    .stTextInput>div>div>input {
        background-color: #1e1e1e;
        color: white;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #5e5ce6;
        box-shadow: 0 0 10px rgba(94, 92, 230, 0.4);
        transition: 0.3s;
    }
    .stTextInput>div>div>input:focus {
        box-shadow: 0 0 20px rgba(120, 120, 255, 0.8);
        border-color: #8a86ff;
    }

    /* ---- Example Box ---- */
    .example-box {
        font-size: 15px;
        color: #d3d3d3;
        background-color: rgba(30,30,30,0.8);
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 0 10px rgba(90,90,255,0.3);
        animation: fadeIn 2s ease-in-out;
    }

    /* ---- Answer Glow ---- */
    .stSuccess {
        background-color: rgba(20, 30, 60, 0.8);
        border-left: 4px solid #5e5ce6;
        box-shadow: 0 0 10px rgba(120, 120, 255, 0.3);
        animation: fadeIn 1.2s ease-in;
    }

    footer, .stMarkdown center {
        color: #a1a1a1;
        text-shadow: 0 0 8px #444;
        animation: fadeIn 2s ease-in;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Hero Section (online image)
# -----------------------------
st.markdown("""
    <div class="hero-image">
        <img src="https://www.almawave.com/wp-content/uploads/2024/10/BLOG-CONVERSATION-STUDIO-3.webp" 
             alt="AI Assistant">
    </div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🤖 AI Career Assistant (Offline)</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Ask about resumes, skills, interviews, or job advice — no internet or API needed!</p>', unsafe_allow_html=True)

# -----------------------------
# Data
# -----------------------------
faq_data = {
    "Resume": {
        "How can I improve my resume?": "Keep it concise (1 page), use bullet points, quantify achievements (e.g., increased efficiency by 30%), and tailor your resume to the job role.",
        "What are common resume mistakes?": "Too long, poor formatting, typos, generic objectives, or listing irrelevant experiences.",
        "Should I include hobbies?": "Include only if relevant to the job or show transferable skills (e.g., leadership in a club)."
    },
    "Skills": {
        "What are top IT skills in demand?": "Cloud Computing, Python, Data Analysis, Machine Learning, and DevOps are highly in demand.",
        "How can I learn new skills quickly?": "Follow project-based learning — apply what you learn instantly through small personal projects.",
        "Which soft skills matter most?": "Communication, teamwork, time management, and adaptability are essential in every job."
    },
    "Interview": {
        "How to prepare for interviews?": "Study the company, revise your resume, practice common questions, and prepare STAR-format answers.",
        "What are common HR questions?": "Tell me about yourself, Why should we hire you?, What are your strengths & weaknesses?",
        "How to handle interview nervousness?": "Practice mock interviews, focus on breathing, and treat it as a conversation, not an interrogation."
    },
    "Jobs": {
        "How can I find my first job?": "Use platforms like LinkedIn, Internshala, or Naukri. Apply for internships first if you lack experience.",
        "What skills do recruiters look for in freshers?": "Good communication, problem-solving, basic technical knowledge, and willingness to learn.",
        "How to get remote jobs?": "Filter remote roles on LinkedIn and build a portfolio on GitHub or personal websites."
    },
    "Projects": {
        "Give me some beginner project ideas": "Portfolio website, weather app, resume analyzer, chatbot, or to-do list app are great starters.",
        "How to choose a project topic?": "Pick something that solves a small real-life problem — it shows initiative.",
        "Do projects matter for jobs?": "Yes! Projects demonstrate applied knowledge and make your resume stand out."
    }
}

# -----------------------------
# Helper Functions
# -----------------------------
def get_random_examples():
    all_questions = [q for cat in faq_data.values() for q in cat.keys()]
    return random.sample(all_questions, min(4, len(all_questions)))

def find_answer(user_question):
    user_question = user_question.lower()
    for category, qa in faq_data.items():
        for question, answer in qa.items():
            if user_question in question.lower() or question.lower() in user_question:
                return f"**{category} Tip:** {answer}"
    return "⚠️ I’m still learning that topic 😅 — but you can ask me about **resumes, skills, interviews, jobs, or projects!**"

# -----------------------------
# Chat UI
# -----------------------------
st.subheader("💡 Try asking about these topics:")
cols = st.columns(5)
categories = list(faq_data.keys())
for i, cat in enumerate(categories):
    if cols[i].button(cat):
        st.session_state["selected_category"] = cat

if "selected_category" in st.session_state:
    category = st.session_state["selected_category"]
    st.markdown(f"### 📘 Example {category} Questions:")
    for q in faq_data[category].keys():
        if st.button(q):
            st.session_state["user_input"] = q
else:
    st.markdown("<div class='example-box'><b>💡 Example questions you can try:</b><br>" + "<br>".join(get_random_examples()) + "</div>", unsafe_allow_html=True)

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

user_input = st.text_input("Ask anything about careers, resumes, skills, or jobs:",
                           value=st.session_state["user_input"],
                           key="user_input_box")

if st.button("Ask"):
    if user_input.strip() != "":
        st.session_state["last_question"] = user_input
        st.session_state["user_input"] = ""
    else:
        st.warning("Please enter a question.")

if "last_question" in st.session_state:
    user_q = st.session_state["last_question"]
    st.markdown("### 🧠 Your Question:")
    st.info(user_q)

    st.markdown("### 🤖 Assistant:")
    response = find_answer(user_q)
    st.success(response)

# -----------------------------
# Footer
# -----------------------------
st.markdown("<br><center>💡 This is an offline chatbot — runs entirely without any API or internet connection.</center>", unsafe_allow_html=True)
