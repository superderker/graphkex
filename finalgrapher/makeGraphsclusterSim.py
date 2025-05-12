import os
import pandas as pd
import matplotlib.pyplot as plt

# Input/output paths
input_file = "cacheGraphs/clusterSimLBMx10-25_cache.csv"
output_dir = "cacheGraphs/logGraphs"
os.makedirs(output_dir, exist_ok=True)

# Define categories using substrings to allow loose matching
categories = {
    "General": ["simSeconds", "simInsts", "hostMemory", "cpi", "ipc"],
    "MemDep": ["MemDepUnit__0"],
    "FuncUnit": ["statFuBusy", "statIssuedInstType", "fuBusy", "fuBusyRate"],
    "ICache": ["icache"],
    "DCache": ["dcache"],
    "L2": ["l2."],  # dot prevents matching dtb.writeHits etc.
    "DTB": ["dtb"],
    "ITB": ["itb"],
    "L2_TLB": ["l2_shared"],
}

# Load the file
df = pd.read_csv(input_file)

# Keep only numeric values
df = df[df["Value"].apply(lambda x: str(x).replace('.', '', 1).isdigit())]
df["Value"] = df["Value"].astype(float)

# Optional: print all stats for debugging
print("Available statistics:")
print(df["Statistic"].tolist())

# Process and plot each category
for category, substrings in categories.items():
    # Match if any substring is found in the stat name
    cat_df = df[df["Statistic"].apply(lambda stat: any(sub in stat for sub in substrings))]

    if cat_df.empty:
        print(f"[Skipped] No matching stats for category: {category}")
        continue

    # Optional: shorter labels for plot readability
    cat_df["Label"] = cat_df["Statistic"].apply(lambda s: s.split('.')[-1])

    # Plot
    plt.figure(figsize=(12, max(4, len(cat_df) * 0.4)))
    plt.bar(cat_df["Label"], cat_df["Value"])
    plt.yscale("log")
    plt.title(f"{category} Stats (Log Scale)")
    plt.ylabel("Value (log scale)")
    plt.xticks(rotation=90)
    plt.tight_layout()

    # Save
    output_path = os.path.join(output_dir, f"{category}_log_bars.png")
    plt.savefig(output_path)
    plt.close()
    print(f"[Saved] {output_path}")



source /Users/erik/Desktop/intro-to-high-performance/myenv/bin/activate