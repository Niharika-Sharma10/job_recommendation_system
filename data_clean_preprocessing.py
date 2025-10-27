
#Data Collection

import pandas as pd
import re

#Load dataset (downloaded CSV from Kaggle or other source)
df = pd.read_csv("jobs.csv")

#Inspect first few rows
print("Sample Data:")
print(df.head())

#Basic dataset info
print("\nDataset Info:")
print(df.info())



#Data Cleaning

# Check for missing values
print("\nMissing values per column (Before Handling):")
print(df.isnull().sum())

# Handle missing values
missing_before = df.isnull().sum().sum()
if missing_before == 0:
    print("No missing values found")
else:
    df.fillna("", inplace=True)
    print("\nMissing values after filling:")
    print(df.isnull().sum())

#Check duplicates
print("\nDataset shape before removing duplicates:", df.shape)

duplicates_count = df.duplicated().sum()
if duplicates_count == 0:
    print("No duplicate rows found")
else:
    print(f"Found {duplicates_count} duplicate rows. Removing duplicates...")
    df.drop_duplicates(inplace=True)
    print("Dataset shape after removing duplicates:", df.shape)

#Standardize column names
print("\nColumn names before standardization:")
print(df.columns)

# Standardize
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
print("\nColumn names after standardization:")
print(df.columns)


print("\nSample of cleaned dataset (top 5 rows):")
print(df.head())



#Data Preprocessing

print(df.columns)

#Clean 'skills' column (lowercase, remove punctuation, extra spaces)
def clean_skills(text):
    text = text.lower()                           # lowercase
    text = re.sub(r'[^\w\s,]', '', text)          # remove punctuation except commas
    text = re.sub(r'\s+', ' ', text)              # remove extra spaces
    return text.strip()

df['required_skills'] = df['required_skills'].apply(clean_skills)

print(df['required_skills'].head(10))


#Save cleaned & preprocessed dataset
df.to_csv("jobs_cleaned.csv", index=False)

print("\nDataset cleaned and saved as jobs_cleaned.csv")



