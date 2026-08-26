import pandas as pd

data = pd.read_csv("dataset/careers.csv")

print("Dataset loaded successfully!")
print("Number of careers:", len(data))

print("\nFirst 5 careers:")
print(data[["career", "required_skills"]].head())