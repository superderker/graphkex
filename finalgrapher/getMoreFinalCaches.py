import os
import re
import pandas as pd

# Input and output directories
stats_dir = "tlbtests"
output_dir = "csvFiles"
os.makedirs(output_dir, exist_ok=True)

# Relevant cache-related statistics
patterns = [
    # L1 Instruction Cache (icache)
    r"system\.cpu_cluster\.cpus\.icache\.overallHits",
    r"system\.cpu_cluster\.cpus\.icache\.overallMisses",
    r"system\.cpu_cluster\.cpus\.icache\.demandHits",
    r"system\.cpu_cluster\.cpus\.icache\.demandMisses",
    r"system\.cpu_cluster\.cpus\.icache\.overallAccesses",
    r"system\.cpu_cluster\.cpus\.icache\.demandAccesses",
    r"system\.cpu_cluster\.cpus\.icache\.replacements",
    r"system\.cpu_cluster\.cpus\.icache\.missRate",
    r"system\.cpu_cluster\.cpus\.icache\.tags\.tagsInUse",

    # L1 Data Cache (dcache)
    r"system\.cpu_cluster\.cpus\.dcache\.overallHits",
    r"system\.cpu_cluster\.cpus\.dcache\.overallMisses",
    r"system\.cpu_cluster\.cpus\.dcache\.demandHits",
    r"system\.cpu_cluster\.cpus\.dcache\.demandMisses",
    r"system\.cpu_cluster\.cpus\.dcache\.overallAccesses",
    r"system\.cpu_cluster\.cpus\.dcache\.demandAccesses",
    r"system\.cpu_cluster\.cpus\.dcache\.replacements",
    r"system\.cpu_cluster\.cpus\.dcache\.missRate",
    r"system\.cpu_cluster\.cpus\.dcache\.tags\.tagsInUse",

    # L2 Cache
    r"system\.cpu_cluster\.l2\.overallHits",
    r"system\.cpu_cluster\.l2\.overallMisses",
    r"system\.cpu_cluster\.l2\.demandHits",
    r"system\.cpu_cluster\.l2\.demandMisses",
    r"system\.cpu_cluster\.l2\.overallAccesses",
    r"system\.cpu_cluster\.l2\.demandAccesses",
    r"system\.cpu_cluster\.l2\.missRate",
    r"system\.cpu_cluster\.l2\.replacements",
    r"system\.cpu_cluster\.l2\.tags\.tagsInUse",
    r"system\.cpu_cluster\.l2\.demandMissLatency::.*",
]

# Process all txt files
for filename in os.listdir(stats_dir):
    if filename.endswith(".txt"):
        filepath = os.path.join(stats_dir, filename)
        with open(filepath, "r") as file:
            lines = file.readlines()

        stats_data = []
        for pattern in patterns:
            regex = re.compile(pattern)
            for line in lines:
                if regex.search(line):
                    key, *rest = line.strip().split()
                    value = rest[0] if rest else ""
                    stats_data.append((key, value))
                    break

        # Save to CSV
        df_stats = pd.DataFrame(stats_data, columns=["Statistic", "Value"])
        output_csv = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_cache.csv")
        df_stats.to_csv(output_csv, index=False)
        print(f"Saved: {output_csv}")
