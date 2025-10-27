import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

df = pd.read_csv("jobs_cleaned.csv")

#Combine important job information into a single text column
df["combined"] = (
    df["job_title"].fillna('') + " " +
    df["required_skills"].fillna('') + " " +
    df["industry"].fillna('')
)

#Initialize TF-IDF Vectorizer
# TF-IDF converts text into numerical features
vectorizer = TfidfVectorizer(stop_words="english")

#Transform the combined text data
tfidf_matrix = vectorizer.fit_transform(df["combined"])

#Compute similarity between jobs
similarity = cosine_similarity(tfidf_matrix)

#Save models
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
pickle.dump(similarity, open("similarity.pkl", "wb"))

print("ML Model training completed successfully!")
print("Files saved: vectorizer.pkl and similarity.pkl")

#Define a function to recommend jobs
def recommend_jobs(job_title):
    if job_title not in df['job_title'].values:
        print("Job not found in dataset.")
        return []

    index = df[df['job_title'] == job_title].index[0]
    distances = similarity[index]
    job_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    print(f"\nTop 5 Job Recommendations for '{job_title}':\n")
    for i in job_list:
        print(df.iloc[i[0]]["job_title"], "–", df.iloc[i[0]]["company"])

