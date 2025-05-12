import os
import re
import pandas as pd

# Directory containing your stats files
stats_dir = "tlbtests"

# Directory to save the CSV files
csv_dir = "csvFiles"
os.makedirs(csv_dir, exist_ok=True)  # Ensure the directory exists

# Patterns to extract memory and TLB-related statistics
patterns = [

    r"simSeconds",
    r"simInsts",
    r"hostMemory",
    r"system\.cpu_cluster\.cpus\.cpi",
    r"system\.cpu_cluster\.cpus\.ipc",


    r"system\.cpu_cluster\.cpus\.MemDepUnit__0\.insertedLoads",
    r"system\.cpu_cluster\.cpus\.MemDepUnit__0\.insertedStores",
    r"system\.cpu_cluster\.cpus\.MemDepUnit__0\.conflictingLoads",
    r"system\.cpu_cluster\.cpus\.MemDepUnit__0\.conflictingStores",


    r"system\.cpu_cluster\.cpus\.statFuBusy::MemRead",
    r"system\.cpu_cluster\.cpus\.statFuBusy::MemWrite",
    r"system\.cpu_cluster\.cpus\.statIssuedInstType_0::MemRead",
    r"system\.cpu_cluster\.cpus\.statIssuedInstType_0::MemWrite",
    r"system\.cpu_cluster\.cpus\.fuBusy",
    r"system\.cpu_cluster\.cpus\.fuBusyRate",


    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.readHits",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.readMisses",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.writeHits",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.writeMisses",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.inserts",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.flushTlb",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.flushedEntries",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.readAccesses",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.writeAccesses",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.hits",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.misses",
    r"system\.cpu_cluster\.cpus\.mmu\.dtb\.accesses",

    # TLB (Instruction TLB - itb)
    r"system\.cpu_cluster\.cpus\.mmu\.itb\.hits",
    r"system\.cpu_cluster\.cpus\.mmu\.itb\.misses",
    r"system\.cpu_cluster\.cpus\.mmu\.itb\.accesses",

    # TLB (L2 Shared TLB)
    r"system\.cpu_cluster\.cpus\.mmu\.l2_shared\.hits",
    r"system\.cpu_cluster\.cpus\.mmu\.l2_shared\.misses",
    r"system\.cpu_cluster\.cpus\.mmu\.l2_shared\.accesses",
]


# Loop through all .txt files in the directory
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

        # Create DataFrame
        df_stats = pd.DataFrame(stats_data, columns=["Statistic", "Value"])

        # Output CSV file with same base name
        output_csv = os.path.join(csv_dir, f"{os.path.splitext(filename)[0]}.csv")
        df_stats.to_csv(output_csv, index=False)
        print(f"Saved: {output_csv}")
