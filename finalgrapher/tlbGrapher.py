import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
        'system.cpu_cluster.cpus.mmu.dtb.accesses'
    ],
    'ITB': [
        'system.cpu_cluster.cpus.mmu.itb.hits',
        'system.cpu_cluster.cpus.mmu.itb.accesses'
    ],
    'L2_TLB': [
        'system.cpu_cluster.cpus.mmu.l2_shared.hits',
        'system.cpu_cluster.cpus.mmu.l2_shared.accesses'
    ]
}


# Initialize summary data structures
summary = {
    'DTB': {'Hit': {}, 'Accesses': {}},
    'ITB': {'Hit': {}, 'Accesses': {}},
    'L2_TLB': {'Hit': {}, 'Accesses': {}},
}


def createLableName(benchmark,entries,type,page4k):
    page="4KiB" if page4k else "64KiB"
    typeStr="Random" if type else "Serial"
    return f"{page}_{entries}_{benchmark}_{typeStr}"



# Process each CSV file individually
for filename in os.listdir(data_dir):
    if not filename.endswith(".csv") or "clusterSim" in filename or "real" in filename:
        continue
    filepath = os.path.join(data_dir, filename)
    if "-4" in filename:
        pages4k=True
    else:
        pages4k=False
    if "R" in filename:
        random=True
    else:
        random=False
    if "64x" in filename:
        size=64
    elif "128x" in filename:
        size=128
    else:
        size=256
    df = pd.read_csv(filepath)
    df=df.sort_values(by=["Benchmark", "Statistic"])
    # Convert key-value format to one row of stats
    for index, row in df.iterrows():
        for tlb in tlb_metrics:
            if row['Statistic'] in tlb_metrics[tlb]:
                    if "accesses" in row["Statistic"]:
                        summary[tlb]['Accesses'][createLableName(row["Benchmark"], size, random, pages4k)]=row["Value"]
                    else:
                        summary[tlb]['Hit'][createLableName(row["Benchmark"], size, random, pages4k)]=row["Value"]

# Plot stacked bar graphs for each TLB type
for tlb, metrics in summary.items():
    data = pd.DataFrame({
        'Hit': metrics['Hit'],
        'Accesses': metrics['Accesses']
    })
    data.index = data.index.str.replace('.csv', '', regex=False)


    if not data.empty:
        for type in ["Random", "Serial"]:
            sizes=["512KiB", "1MiB", "2MiB", "4MiB", "8MiB", "16MiB", "32MiB"]
            arr64KB64=[0]*7
            arr64KB128=[0]*7
            arr64KB256=[0]*7

            arr4KB64=[0]*7
            arr4KB128=[0]*7
            arr4KB256=[0]*7

            for index, row in data.iterrows():
                keys=index.split("_")
                ratio=row['Hit']/row["Accesses"]
                if type in keys:
                    if "64KiB" in keys:
                        match keys[1]:
                            case '64':
                                arr64KB64[sizes.index(keys[2])]=ratio
                            case '128':
                                arr64KB128[sizes.index(keys[2])]=ratio
                            case '256':
                                arr64KB256[sizes.index(keys[2])]=ratio
                    else:
                        match keys[1]:
                            case '64':
                                arr4KB64[sizes.index(keys[2])]=ratio
                            case '128':
                                arr4KB128[sizes.index(keys[2])]=ratio
                            case '256':
                                arr4KB256[sizes.index(keys[2])]=ratio

            fig,axs=plt.subplots(figsize=(12, 6))

            arrList=[arr64KB64, arr64KB128, arr64KB256, arr4KB64, arr4KB128, arr4KB256]
            lineTypes=["r-.","r--","r:","b-.","b--","b:"]
            labels=["64 KiB-64 entries","64 KiB-128 entries","64 KiB-256 entries","4 KiB-64 entries","4 KiB-128 entries","4 KiB-256 entries" ]

            xs=np.arange(0,7)
            for lines, ys, label, in zip(lineTypes, arrList, labels):
                axs.plot(xs,np.array(ys)*100,lines ,label=label)

            axs.set_xticks(xs, labels=sizes)
            axs.set_ylabel('Percentage')
            
            axs.set_title(f"{tlb} - TLB Hit Percentage - {type} Access")
            box = axs.get_position()
            axs.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            axs.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            fig.tight_layout()
            fig.savefig(os.path.join(output_dir, f"{tlb}_{type}_tlb_line.png"), bbox_inches="tight")
    else:
        print(f"No data available for {tlb}, skipping bar graph.")
