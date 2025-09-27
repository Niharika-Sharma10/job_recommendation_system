import pandas as pd
df = pd.read_csv("jobs_cleaned.csv")
df_small = df.head(200)
df_small.to_csv("jobs_cleaned.csv", index=False)
