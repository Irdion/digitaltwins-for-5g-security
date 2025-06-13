import pandas as pd

df = pd.read_csv("verdicts_scenarioC.csv")

df["pred"] = (df.verdict == "CRITICAL").astype(int)

tp = ((df["malicious"] == 1) & (df["pred"] == 1)).sum()
fp = ((df["malicious"] == 0) & (df["pred"] == 1)).sum()
fn = ((df["malicious"] == 1) & (df["pred"] == 0)).sum()

precision = tp / (tp + fp) if (tp + fp) else float("nan")
recall    = tp / (tp + fn) if (tp + fn) else float("nan")

print(f"TP = {tp}")
print(f"FP = {fp}")
print(f"FN = {fn}")
print(f"Precision = {precision:.3f}")
print(f"Recall    = {recall:.3f}")
