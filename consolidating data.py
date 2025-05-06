import pandas as pd
import os

# Define file paths
DATA_PATH = "/Users/elvin/Desktop/Data"  # Change if needed
PRICE_OUTPUT = os.path.join(DATA_PATH, "merged_price_data.csv")
FUNDAMENTALS_OUTPUT = os.path.join(DATA_PATH, "merged_fundamentals_data.csv")

# Initialize empty DataFrames
all_price_data = pd.DataFrame()
all_fundamentals_data = pd.DataFrame()

# Loop through batches 1 to 20
for batch_num in range(1, 117):
    price_file = os.path.join(DATA_PATH, f"price_batch_{batch_num}.csv")
    fundamentals_file = os.path.join(DATA_PATH, f"fundamentals_batch_{batch_num}.csv")

    # Merge price data
    if os.path.exists(price_file):
        df_price = pd.read_csv(price_file)
        all_price_data = pd.concat([all_price_data, df_price], ignore_index=True)
        print(f"✅ Merged {price_file}")

    # Merge fundamentals data
    if os.path.exists(fundamentals_file):
        df_fundamentals = pd.read_csv(fundamentals_file)
        all_fundamentals_data = pd.concat([all_fundamentals_data, df_fundamentals], ignore_index=True)
        print(f"✅ Merged {fundamentals_file}")

# Save merged datasets
if not all_price_data.empty:
    all_price_data.to_csv(PRICE_OUTPUT, index=False)
    print(f"📂 Merged price data saved to {PRICE_OUTPUT}")

if not all_fundamentals_data.empty:
    all_fundamentals_data.to_csv(FUNDAMENTALS_OUTPUT, index=False)
    print(f"📂 Merged fundamentals data saved to {FUNDAMENTALS_OUTPUT}")

print("🎉 Data merging complete!")
