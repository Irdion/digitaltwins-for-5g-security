"""
    Load latency samples from files matching the given glob pattern,
    and compute p50 and p95 percentiles (in milliseconds) for each.
    Returns:
        scenarios (list[str]): Labels for each file (e.g. "A", "B", …).
        p50_vals   (list[float])
        p95_vals   (list[float])
    """

import numpy as np
import matplotlib.pyplot as plt
import glob, os, re

files = sorted(glob.glob("latencies_*.txt"))
if not files:
    raise SystemExit("No files named latencies_*.txt found.")

scenarios, p50_vals, p95_vals = [], [], []

for f in files:
    label = re.search(r"latencies_([A-Za-z])\.txt", os.path.basename(f))[1]
    scenarios.append(f"{label}")
    samples = np.loadtxt(f)                 # seconds
    p50_vals.append(np.percentile(samples, 50) * 1000)   # → ms
    p95_vals.append(np.percentile(samples, 95) * 1000)

"""
    Plot p50 and p95 latency values across scenarios.
    """
x = np.arange(len(scenarios))

plt.figure(figsize=(8, 4))
plt.plot(x, p50_vals, marker='o', linestyle='-', label='p50')
plt.plot(x, p95_vals, marker='s', linestyle='--', label='p95')

plt.xticks(x, [f"{lbl} – Scenario" for lbl in scenarios], rotation=15)
plt.ylabel("Latency [ms]")
plt.title("Verdict latency across load scenarios")
plt.ylim(0, max(p95_vals) * 1.2)
plt.legend()
plt.tight_layout()
plt.savefig("verdict_latency_line.png")

