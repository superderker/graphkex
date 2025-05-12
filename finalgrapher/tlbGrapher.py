import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Directory containing CSV files
data_dir = "csvFiles"

# Directory to save the graphs
output_dir = "tlbGraphs"
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

# Relevant TLB metric keys
# Relevant TLB metric keys (fully-qualified names from your CSVs)
tlb_metrics = {
    'DTB': [
        'system.cpu_cluster.cpus.mmu.dtb.hits',
        'system.cpu_cluster.cpus.mmu.dtb.misses',
        'system.cpu_cluster.cpus.mmu.dtb.accesses'
    ],
    'ITB': [
        'system.cpu_cluster.cpus.mmu.itb.hits',
        'system.cpu_cluster.cpus.mmu.itb.misses',
        'system.cpu_cluster.cpus.mmu.itb.accesses'
    ],
    'L2_TLB': [
        'system.cpu_cluster.cpus.mmu.l2_shared.hits',
        'system.cpu_cluster.cpus.mmu.l2_shared.misses',
        'system.cpu_cluster.cpus.mmu.l2_shared.accesses'
    ]
}


# Initialize summary data structures
summary = {
    'DTB': {'Hit %': {}, 'Miss %': {}},
    'ITB': {'Hit %': {}, 'Miss %': {}},
    'L2_TLB': {'Hit %': {}, 'Miss %': {}}
}

# Process each CSV file individually
for filename in os.listdir(data_dir):
    if not filename.endswith(".csv"):
        continue
    filepath = os.path.join(data_dir, filename)
    try:
        df = pd.read_csv(filepath)

        # Convert key-value format to one row of stats
        if 'Statistic' in df.columns and 'Value' in df.columns:
            df = df.set_index('Statistic').transpose()

        for tlb, metrics in tlb_metrics.items():
            if all(metric in df.columns for metric in metrics):
                accesses = float(df[metrics[2]].values[0])
                if accesses > 0:
                    hits = float(df[metrics[0]].values[0])
                    misses = float(df[metrics[1]].values[0])
                    summary[tlb]['Hit %'][filename] = 100 * hits / accesses
                    summary[tlb]['Miss %'][filename] = 100 * misses / accesses

    except Exception as e:
        print(f"Failed to process {filename}: {e}")

# Plot heatmaps for each TLB type
# Plot stacked bar graphs for each TLB type
for tlb, metrics in summary.items():
    data = pd.DataFrame({
        'Hit %': metrics['Hit %'],
        'Miss %': metrics['Miss %']
    })
    data.index = data.index.str.replace('.csv', '', regex=False)

    if not data.empty:
        plt.figure(figsize=(12, 6))
        data.sort_index(inplace=True)  # Optional: sort by filename
        bottom_vals = data['Hit %']
        top_vals = data['Miss %']

        plt.bar(data.index, bottom_vals, label='Hit %')
        plt.bar(data.index, top_vals, bottom=bottom_vals, label='Miss %')

        plt.xticks(rotation=90, ha='right')
        plt.ylabel('Percentage')
        plt.title(f"{tlb} - TLB Hit vs Miss Percentage")
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{tlb}_tlb_bar.png"))
        plt.close()
    else:
        print(f"No data available for {tlb}, skipping bar graph.")
