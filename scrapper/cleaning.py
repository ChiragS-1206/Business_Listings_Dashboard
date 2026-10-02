import pandas as pd
import csv

df = pd.read_csv("gmaps_data.csv")

df = df.fillna("")

df.to_csv(
    "full_FINAL_FIXED.csv",
    index=False,
    encoding="utf-8-sig",
    quoting=csv.QUOTE_ALL
)