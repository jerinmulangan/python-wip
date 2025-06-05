# analyze_runs.py
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CSV_PATH = Path(__file__).with_name("runs.csv")

if not CSV_PATH.exists():
    raise FileNotFoundError("runs.csv not found – run the visualizer first!")

df = pd.read_csv(
    CSV_PATH,
    header=None,
    names=["path_length", "visited_nodes", "elapsed_ms"],
    sep=r"[\t,]",           
    engine="python",
)

print("\nSummary statistics:")
print(df.describe())

plt.figure(figsize=(8, 4))
plt.plot(df.index + 1, df["elapsed_ms"], marker="o")
plt.title("Dijkstra elapsed time per run")
plt.xlabel("Run number")
plt.ylabel("Milliseconds")
plt.grid(True)
plt.tight_layout()
plt.show()
