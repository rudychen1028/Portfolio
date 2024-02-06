#!/root/anaconda3/bin/python3

import json
import pdb
import datetime
import pandas as pd
import numpy as np
from prometheus_api_client import PrometheusConnect
import argparse
import time
import multiprocessing as mp
import os

def load(args, metric, prom):
    data = prom.get_metric_range_data(
        metric,
        start_time=args.stime,
        end_time=args.etime,
    )
    return data
   # interactive
   # name = input('please enter matric name : ')
   # sy = int(input('Enter a start year : '))
   # sy = eval(sy)
   # sm = int(input('Enter a start month : ')).eval(sm)
   # sd = int(input('Enter a start day : ')).eval(sd)
   # shr = int(input('Enter a start hour : ')).eval(shr)
   # smin = int(input('Enter a start minutes : ')).eval(smin)
   # ssec = int(input('Enter a start second : ')).eval(ssec)
   # date1 = datetime.datetime(sy, sm, sd, shr, smin, ssec)
   # ey = int(input('Enter a end year : ')).eval(ey)
   # em = int(input('Enter a end month : ')).eval(em)
   # ed = int(input('Enter a end day : ')).eval(ed)
   # ehr = int(input('Enter a end hour : ')).eval(ehr)
   # emin = int(input('Enter a end minutes : ')).eval(emin)
   # esec = int(input('Enter a end second : ')).eval(esec)
   # date2 = datetime.datetime(ey, em, ed, ehr, emin, esec)
   # range_data = prom.get_metric_range_data(
   #     name,
   #     date1,
   #     date2,
   # )
   
   # fetching the metric data in a specific time interval
   # range_data = prom.get_metric_range_data(
   #     "ifHCOutOctets{instance='C2-CM-QFX10002-1', interface='ae4.0'}", # this is the metric name and label config
   #     start_time=datetime.datetime(2022, 3, 14, 0, 0, 0),
   #     end_time=datetime.datetime(2022, 3, 14, 1, 0, 0),
   #     #chunk_size=chunk_size,
   # )
    
 
#load local data
#def load():
#    with open('HCOOtest.json',"r") as file:
#        f = json.load(file)
#    return f


def get_metrics(prom):
    return prom.all_metrics()

def get_command():
    parser = argparse.ArgumentParser()

    parser.add_argument("--matric", type=str, help="--matric : ifHCOutOctets{instance='C2-CM-QFX10002-1', interface='ae4.0'}")
    parser.add_argument("--stime", type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S'), help="format: YYYY-mm-dd HH:MM:SS")
    parser.add_argument("--etime", type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S'), help="format: YYYY-mm-dd HH:MM:SS")
    #parser.add_argument("--chunk_size", type=str, default=None, help="--chunk_size")
    return parser

def reformat(data):
    alldata = []
    for t in data:
        metric = t['metric']
        output = []
        for v in t['values']:
            tmp = {"tsp": v[0], 'value':v[1]}
            # z = {**x, **y}
            tmp2 = {**metric, **tmp}
            output.append(tmp2)
        #a = pd.DataFrame(output)
        #alldata.append(a)
        alldata.extend(output)
    #res = pd.concat(alldata,axis=0).reset_index(drop=True)
    #print(res)
    return alldata

#reformat only values
#def reformat(data):
#    for t in data:
#        output = []
#        for v in t['values']:
#            tmp = {'tsp': float(v[0]), 'value':int(v[1])}
#            output.append(tmp)
#    print(np.array(output))


def save(data, filepath):
    try:
        tf = open(filepath, "w")
        for target in data:
            target = json.dumps(target)
            tf.write(f"{target}\n")
        tf.close()
        return True
    except Exception as e:
        print(e)
        return False

def main(target):
    args, metric, prom, filepath = target
    print("start loading ({0})".format(metric))
    data = load(args, metric, prom)
    print("start reformating ({0})".format(metric))
    data = reformat(data)
    print("start saving ({0})".format(metric))
    status = save(data, filepath)

    print("process metric : {0}, status {1}".format(metric, status))

def _if_path_exists(path):
    return os.path.exists(path)

def check_path(path):
    # check path is exist
    if _if_path_exists(path):
        return True
    else:
        try:
            # if path not exist create path
            os.makedirs(path)
            return True
        except:
            print(f"Create : {path} failed!")
            return False

#將metric for迴圈建立檔名，並回傳值成一個file
def gen_mp_input(args, prom, metrics, filepath):
    for metric in metrics:
        filename = f"{filepath}/{metric}_{folder_date}.txt" #{}可傳入變數進去
        yield (args, metric, prom, filename) 
        #yield為了單次輸出內容，一旦我們的程式執行到 yield 後，程式就會把值丟出，並暫時停止。
        
def test_print(target):
    args, metric, prom, filepath = target
    #print(args, metric, prom, filepath)
    return f"{target} success", "werwer" #後方可迭代內容

if __name__ == "__main__":

    parser = get_command()
    args = parser.parse_args() # 解析命令列參數
    prom = PrometheusConnect(url ="http://202.140.190.243:9090", disable_ssl=True)
    folder_date = args.stime.strftime("%Y%m%d")
    filepath= f"./load_reformat_save/{folder_date}"
    if check_path(filepath):
        t1 = datetime.datetime.now()
        t1 = str(t1)
        metrics = get_metrics(prom) # get all metric
        pool = mp.Pool(2) #設定處理程序數量，如無設定，則預設使用系統全部核心
        #result = pool.map(test_print, gen_mp_input(args, prom, metrics, filepath)) #運行多處理程序
        result = pool.map(main, gen_mp_input(args, prom, metrics, filepath)) #運行多處理程序
        #其中gen_mp_input是一個Python的可迭代對象，會把每一個迭代元素輸入進我們定義的test_print函式中進行處理
        pool.close()
        pool.join() 
        #調用join之前，先調用close函数，否則會出錯。執行完close後不會有新的程序加入到pool，join函數等待所有子程序结束
        t2 = datetime.datetime.now()
        t2 = str(t2)
        print("[finished] ", "Start time:"+t1+" ,End time:"+t2)
        

    #for mytuple in gen_mp_input(args, prom, metrics, filepath):
        #print(mytuple)

   #to test the main() is work, pdb can't not use in pool 
   #for metric in metrics[:1]:
   #     filepath = f"{filepath}/{metric}.txt"
   #     t1 = time.time()
   #     main(args, metric, prom, filepath)
   #     t2 = time.time()
   #     print(t2-t1)
