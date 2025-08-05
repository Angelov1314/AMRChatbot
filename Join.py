import pandas as pd

# Load the data (you can also use pd.DataFrame() if you create them manually)
Demographics = pd.read_csv("Data/Demographics.csv")
Conversations = pd.read_csv("Data/structured_conversations.csv")

# Perform inner join on Email address
merged_df = pd.merge(Demographics, Conversations, on="Email address", how="inner")

# Save the merged data to a CSV file
merged_df.to_csv("Data/merged_data.csv", index=False)

# Show result summary
print(f"Merged data saved to 'merged_data.csv'")
print(f"Total rows in merged dataset: {len(merged_df)}")
print(f"Columns in merged dataset: {list(merged_df.columns)}")
print("\nFirst few rows of merged data:")
print(merged_df.head())
