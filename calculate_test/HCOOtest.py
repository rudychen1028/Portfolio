#!/root/anaconda3/bin/python3

import json
import pdb
import datetime
import pandas as pd
import numpy as np

with open('HCOOtest.json',"r") as file:
    d =json.load(file)

for t in d:
    output = []
    for v in t['values']:
        tmp = {'tsp': int(v[0]), 'value':int(v[1])}
        """
        # case 1 
        tmp = {'tsp': v[0], 'value':int(v[1])}
        """
        output.append(tmp)
    df = pd.DataFrame(output)
    """
    case 2
    df['value'] = df['value'].apply(lambda x: int(x))
    case 3
    df = df.astype({'value': 'int32'}).dtypes
    
    """
#    df["b"] = df["tsp"].diff(1)
#    df["c"] = df["value"].diff(1i)
    tsp_group = df.groupby(['tsp'])['value'].sum()
    df['tsp(x2-x1)'] = df['tsp'].shift(-1) - df['tsp']
    df['tsp(x2-x1)'].fillna(value=0, inplace=True)
    df['tsp(x2-x1)'].astype(int)
    df['value(y2-y1)'] = df['value'].shift(-1) - df['value']
    df['value(y2-y1)'].fillna(value=0, inplace=True)
    df['value(y2-y1)'].astype(int)
    df['slope'] = df['value(y2-y1)']/df['tsp(x2-x1)']
    df['slope'].fillna(value=0, inplace=True)
    df['slope'].astype(int)
print(df)
df.to_csv("HCOOtest.csv")
