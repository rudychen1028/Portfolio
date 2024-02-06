1. load data from Prometheus "ifHCOutOctets{instance="C2-CM-QFX10002-1", interface="ae4.0"}"

2. reformat data to {key, value} 

3. use shift function to subtract the previous line of data

4. calculate (y2-y1)/(x2-x1) = slope =>network input/output

5. output(.json/.csv)
