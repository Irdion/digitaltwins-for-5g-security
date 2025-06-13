import pandas as pd
import sys

csv = sys.argv[1]
df  = pd.read_csv(csv)

row = df.iloc[-1]

med = row['Median Response Time']
p95 = row['95%']  

print(f"{csv} → median = {med:.2f} ms, p95 = {p95:.2f} ms")
