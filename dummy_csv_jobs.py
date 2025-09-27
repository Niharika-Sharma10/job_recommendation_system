# dummy_jobs.py
import pandas as pd

# 1️⃣ Dummy Job Dataset
data = {
    "Job Title": [
        "Data Analyst",
        "Financial Analyst",
        "Software Developer",
        "ML Engineer",
        "Accountant"
    ],
    "Company": [
        "ABC Corp",
        "XYZ Ltd",
        "TechSoft",
        "AI Labs",
        "FinCorp"
    ],
    "Location": [
        "Delhi",
        "Mumbai",
        "Bangalore",
        "Remote",
        "Delhi"
    ],
    "Required Skills": [
        "Excel, SQL, Statistics",
        "Finance, Excel, Accounting",
        "Python, Java, Problem Solving",
        "Python, Machine Learning, SQL",
        "Finance, Tally, Excel"
    ]
}

# 2️⃣ Create DataFrame
jobs_df = pd.DataFrame(data)

# 3️⃣ Save as CSV
jobs_df.to_csv("dummy_csv_jobs.csv", index=False)
print("Dummy CSV file 'dummy_csv_jobs.csv' created successfully!")
