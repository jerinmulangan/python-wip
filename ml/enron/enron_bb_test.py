import pandas as pd

# Load the file
df = pd.read_csv("enron1_bow_train.csv")

# Display some basic info
print(df.head())  # Show the first few rows
print(df.describe())  # Show summary statistics
print(df.iloc[:, :-1].sum(axis=0))  # Check if words appear in any email
