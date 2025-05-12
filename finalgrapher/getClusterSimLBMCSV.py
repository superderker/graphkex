import os
import re
import pandas as pd

# Input and output directories
stats_dir = "/Users/erik/DD1310/finalgrapher"
output_dir = "/Users/erik/DD1310/finalgrapher/cacheGraphs"
os.makedirs(output_dir, exist_ok=True)

# All relevant stat patterns
patterns = [
    # General performance metrics
    r"simSeconds",
    r"simInsts",
    r"hostMemory",
    r"cpi",
    r"ipc",

    # Memory Dependency Unit
    r"MemDepUnit__0\.insertedLoads",
    r"MemDepUnit__0\.insertedStores",
    r"MemDepUnit__0\.conflictingLoads",
    r"MemDepUnit__0\.conflictingStores",

    # Functional Unit Utilization
    r"statFuBusy::MemRead",
    r"statFuBusy::MemWrite",
    r"statIssuedInstType_0::MemRead",
    r"statIssuedInstType_0::MemWrite",
    r"fuBusy",
    r"fuBusyRate",

    # ICache
    r"icache\.overallHits",
    r"icache\.overallMisses",
    r"icache\.demandHits",
    r"icache\.demandMisses",
    r"icache\.overallAccesses",
    r"icache\.demandAccesses",
    r"icache\.replacements",
    r"icache\.missRate",
    r"icache\.tags\.tagsInUse",

    # DCache
    r"dcache\.overallHits",
    r"dcache\.overallMisses",
    r"dcache\.demandHits",
    r"dcache\.demandMisses",
    r"dcache\.overallAccesses",
    r"dcache\.demandAccesses",
    r"dcache\.replacements",
    r"dcache\.missRate",
    r"dcache\.tags\.tagsInUse",

    # L2 Cache
    r"l2\.overallHits",
    r"l2\.overallMisses",
    r"l2\.demandHits",
    r"l2\.demandMisses",
    r"l2\.overallAccesses",
    r"l2\.demandAccesses",
    r"l2\.missRate",
    r"l2\.replacements",
    r"l2\.tags\.tagsInUse",
    r"l2\.demandMissLatency::.*",

    # Data TLB (DTB)
    r"dtb\.readHits",
    r"dtb\.readMisses",
    r"dtb\.writeHits",
    r"dtb\.writeMisses",
    r"dtb\.inserts",
    r"dtb\.flushTlb",
    r"dtb\.flushedEntries",
    r"dtb\.readAccesses",
    r"dtb\.writeAccesses",
    r"dtb\.hits",
    r"dtb\.misses",
    r"dtb\.accesses",

    # Instruction TLB (ITB)
    r"itb\.hits",
    r"itb\.misses",
    r"itb\.accesses",

    # L2 Shared TLB
    r"l2_shared\.hits",
    r"l2_shared\.misses",
    r"l2_shared\.accesses"
]

# Compile regexes for performance
regexes = [re.compile(p) for p in patterns]

# Process each file
for filename in os.listdir(stats_dir):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(stats_dir, filename)
    with open(filepath, "r") as file:
        lines = file.readlines()

    stats_data = []
    for line in lines:
        for regex in regexes:
            if regex.search(line):
                key, *rest = line.strip().split()
                value = rest[0] if rest else ""
                stats_data.append((key, value))
                break

    df_stats = pd.DataFrame(stats_data, columns=["Statistic", "Value"])
    output_csv = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_cache.csv")
    df_stats.to_csv(output_csv, index=False)
    print(f"Saved: {output_csv}")
