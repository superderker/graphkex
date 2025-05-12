import os
import pandas as pd
import matplotlib.pyplot as plt

# ---- File paths ----
sim_file = "csvFiles/clusterSimLBMx10-25_cache.csv"
real_file = "csvFiles/realResults.csv"
output_dir = "comparisonGraphs_percentages"
os.makedirs(output_dir, exist_ok=True)

# ---- Load real data ----
real_df = pd.read_csv(real_file)
real_df.set_index("Size", inplace=True)

# ---- Load simulation data ----
sim_df = pd.read_csv(sim_file)
sim_df = sim_df[pd.to_numeric(sim_df["Value"], errors="coerce").notnull()]
sim_df["Value"] = sim_df["Value"].astype(float)

# ---- Split simulation data into size blocks ----
sim_blocks = []
current_block = []

for _, row in sim_df.iterrows():
    if row["Statistic"] == "simSeconds" and current_block:
        sim_blocks.append(pd.DataFrame(current_block))
        current_block = []
    current_block.append(row)
if current_block:
    sim_blocks.append(pd.DataFrame(current_block))

# ---- Use only selected grid sizes and correct order ----
size_order = ["25x25x25", "15x15x15", "10x10x10"]
sim_blocks = sim_blocks[:len(size_order)]
for i, block in enumerate(sim_blocks):
    block["Size"] = size_order[i]

# ---- Combine and pivot ----
sim_combined = pd.concat(sim_blocks, ignore_index=True)
sim_pivot = sim_combined.pivot(index="Size", columns="Statistic", values="Value")

# ---- Compute missing rates if needed ----
if "system.cpu_cluster.cpus.mmu.dtb.missRate" not in sim_pivot.columns:
    try:
        sim_pivot["system.cpu_cluster.cpus.mmu.dtb.missRate"] = (
            sim_pivot["system.cpu_cluster.cpus.mmu.dtb.misses"] /
            sim_pivot["system.cpu_cluster.cpus.mmu.dtb.accesses"]
        ) * 100
        print("[Info] Computed dtb.missRate as percentage.")
    except KeyError:
        print("[Warning] Could not compute dtb.missRate.")

if "system.cpu_cluster.cpus.mmu.itb.missRate" not in sim_pivot.columns:
    try:
        sim_pivot["system.cpu_cluster.cpus.mmu.itb.missRate"] = (
            sim_pivot["system.cpu_cluster.cpus.mmu.itb.misses"] /
            sim_pivot["system.cpu_cluster.cpus.mmu.itb.accesses"]
        ) * 100
        print("[Info] Computed itb.missRate as percentage.")
    except KeyError:
        print("[Warning] Could not compute itb.missRate.")

if "system.cpu_cluster.cpus.dcache.missRate" not in sim_pivot.columns:
    try:
        sim_pivot["system.cpu_cluster.cpus.dcache.missRate"] = (
            sim_pivot["system.cpu_cluster.cpus.dcache.overallMisses::total"] /
            sim_pivot["system.cpu_cluster.cpus.dcache.overallAccesses::total"]
        ) * 100
        print("[Info] Computed dcache.missRate as percentage.")
    except KeyError:
        print("[Warning] Could not compute dcache.missRate.")

# ---- Percentage-based metrics ----
metrics = {
    "dTLB-miss-rate (%)": "system.cpu_cluster.cpus.mmu.dtb.missRate",
    "iTLB-miss-rate (%)": "system.cpu_cluster.cpus.mmu.itb.missRate",
    "L1-miss-rate (%)": "system.cpu_cluster.cpus.dcache.missRate"
}

# ---- Plot comparisons ----
for real_key, sim_key in metrics.items():
    if sim_key not in sim_pivot.columns:
        print(f"[Missing] {sim_key} not in simulation data.")
        continue
    if real_key not in real_df.columns:
        print(f"[Missing] {real_key} not in real results.")
        continue

    plt.figure(figsize=(8, 5))

    sim_vals = sim_pivot.loc[size_order, sim_key]
    real_vals = real_df.loc[size_order, real_key]
    print("\n[Comparison Table]")
    comparison_df = pd.DataFrame({
    "Simulated": sim_vals.values,
    "Real": real_vals.values
    }, index=size_order)
    print(comparison_df)
    
    plt.bar(
        [i - 0.2 for i in range(len(size_order))],
        sim_vals,
        width=0.4,
        label="Simulation"
    )
    plt.bar(
        [i + 0.2 for i in range(len(size_order))],
        real_vals,
        width=0.4,
        label="Real Hardware"
    )

    plt.xticks(range(len(size_order)), size_order)
    plt.title(f"Comparison of {real_key}")
    plt.ylabel("Miss Rate (%)")
    plt.legend()
    plt.tight_layout()

    safe_name = real_key.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
    out_path = os.path.join(output_dir, f"{safe_name}_comparison.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[Saved] {out_path}")
