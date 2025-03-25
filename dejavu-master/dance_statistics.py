import pandas as pd
from dejavu import Dejavu
from dejavu.logic.recognizer.file_recognizer import FileRecognizer
import matplotlib.pyplot as plt
import seaborn as sns

results_csv_path = 'results.csv'
df = pd.read_csv(results_csv_path)

# ---------------------- STATISTICS & PLOTS ----------------------
# Accuracy percentage with two attempts
total_queries = df["Query"].nunique()
successful_pairs = df.groupby("Query")["Success"].apply(lambda x: "YES" in x.values).sum()
accuracy_two_attempts = (successful_pairs / total_queries) * 100
print(f"Accuracy with two attempts: {accuracy_two_attempts:.2f}%")

# Accuracy percentage with one attempt
best_match_success = df.loc[df.groupby("Query")["Match Ratio"].idxmax(), "Success"]
accuracy_one_attempt = (best_match_success == "YES").mean() * 100
print(f"Accuracy with one attempt: {accuracy_one_attempt:.2f}%")

#  Relationship between query duration and Partial Success
plt.figure(figsize=(10, 5))
sns.boxplot(x="Partial Success", y="Query Duration", data=df)
plt.title("Query Duration vs Partial Success")
plt.savefig("query_duration_vs_success_2.png")
plt.show()

# Relationship between query duration and Total Success
plt.figure(figsize=(10, 5))
sns.boxplot(x="Total Success", y="Query Duration", data=df)
plt.title("Query Duration vs Total Success")
plt.savefig("query_duration_vs_success.png")
plt.show()
    
# Distribution of query durations
plt.figure(figsize=(10, 5))
sns.histplot(df["Query Duration"], bins=20, kde=True)
plt.title("Distribution of Query Durations")
plt.savefig("query_duration_distribution.png")
plt.show()
    
# Distribution of Match Ratio
plt.figure(figsize=(10, 5))
sns.histplot(df["Match Ratio"], bins=20, kde=True)
plt.title("Distribution of Match Ratio")
plt.savefig("match_ratio_distribution.png")
plt.show()

# Relationship between Match Ratio and Query Duration
plt.figure(figsize=(10, 5))
sns.scatterplot(x="Match Ratio", y="Query Duration", data=df)
plt.title("Match Ratio vs Query Duration")
plt.xlabel("Match Ratio")
plt.ylabel("Query Duration (seconds)")
plt.savefig("match_ratio_vs_duration.png")
plt.show()
