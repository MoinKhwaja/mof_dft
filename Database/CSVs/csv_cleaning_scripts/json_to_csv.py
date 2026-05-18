import os
import json
import pandas as pd


qmof_json_path = "qmof.json"


with open(qmof_json_path) as f:
    qmof = json.load(f)
qmof_df = pd.json_normalize(qmof).set_index("qmof_id")


qmof_df.to_csv("qmof.csv")
