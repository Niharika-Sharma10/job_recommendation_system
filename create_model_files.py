import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# ----------------------------
# Load dataset
# ----------------------------
jobs = pd.read_csv("jobs.csv")  # or jobs_cleaned.csv
print("✅ Columns found:", jobs.columns.tolist())

# Detect the skills column
col_name = None
for name in jobs.columns:
    if 'skill' in name.lower():
        col_name = name
        break

if not col_name:
    raise ValueError("No column containing 'skill' found!")

# Use only a smaller sample for demo (optional)
if len(jobs) > 1000:
    jobs = jobs.sample(500, random_state=42)  # <-- You can adjust 500 to 1000 safely
    print(f"⚙️ Using random sample of 500 rows out of {len(jobs)} total")

jobs[col_name] = jobs[col_name].fillna("")

# ----------------------------
# Vectorizer (no similarity computation here)
# ----------------------------
vectorizer = CountVectorizer(stop_words='english')
job_vectors = vectorizer.fit_transform(jobs[col_name])

# Save vectorizer and dataset for Flask
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))
jobs.to_csv("jobs_cleaned_small.csv", index=False)

print("✅ vectorizer.pkl and reduced dataset saved successfully!")
print(f"Vectorizer shape: {job_vectors.shape}")

