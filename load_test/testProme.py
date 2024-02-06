#!/root/anaconda3/bin/python3

import json
import pdb
import datetime
import pandas as pd

with open('uptest.json',"r") as file:
    d =json.load(file)

#for t in d:
#    #tmp = {"tsp":[], "value":[]}
#    metric = t['metric']
#    tmp = {key:[] for key in metric.keys()}
#    tmp["tsp"] = []
#    tmp["value"] = []
#    #pdb.set_trace()
#    #print(t['metric'])
#    for v in t['values']:
#        tsp, values = v
#        tmp['tsp'].append(tsp)
#        tmp['value'].append(values)
#        for key in metric.keys():
#            tmp[key].append(metric[key])
#    pdb.set_trace()
#df = pd.read_json('uptest.json')
#print(df)

alldata = []
for t in d:
    metric = t['metric']
    output = []
    for v in t['values']:
        tmp = {"tsp": v[0], 'value':v[1]}
        # z = {**x, **y}
        tmp2 = {**metric, **tmp}
        output.append(tmp2)
    #pdb.set_trace()
    a = pd.DataFrame(output)
    alldata.append(a)
res = pd.concat(alldata,axis=0).reset_index(drop=True)
print(res)
res.to_csv("uptest.csv")

#from prometheus_api_client import PrometheusConnect
#prom = PrometheusConnect(url ="http://202.140.190.243:9090", disable_ssl=True)
# Get the list of all the metrics that the Prometheus host scrapes
#pdb.set_trace() 
#current_value = prom.get_current_metric_value(metric_name='up')
#range_data = prom.get_metric_range_data(
#    "up",#{cluster='my_cluster_id'} # this is the metric name and label config
#    start_time=datetime.datetime(2022, 3, 14, 0, 0, 0),
#    end_time=datetime.datetime(2022, 3, 15, 0, 0, 0),
    #chunk_size=chunk_size,
#)
#pdb.set_trace()
#filename="uptest.json" # 指定要把numbers串列存到number.json檔中
#with open(filename,"w") as file: # 以寫入模式開啟檔案才可以將資料儲存進去
#    json.dump(range_data,file) # 將numbers串列存到number.json檔
#print(json.dumps(range_data, indent=4))
