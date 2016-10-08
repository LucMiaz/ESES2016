from classes import *
import string
import numpy as np; np.random.seed(22)
import pandas as pd
import seaborn as sns; sns.set(color_codes=True)
import matplotlib.pyplot as plt
import ast
import csv
from scipy import stats
from icc import icc
def mean_temp(siteCode):
    MATCH=match(type="Sample", sampleType="ctd",siteCode=siteCode)
    data=[]
    xmin=1000.
    xmax=-1000.
    for m in MATCH:
        xmin=min(xmin,min(ast.literal_eval(m.temperature)))
        xmax=max(xmax,max(ast.literal_eval(m.temperature)))
    step=(xmax-xmin)/100000
    df=pd.DataFrame()
    data={}
    x=[xmax-step*t for t in range(0,1000)]
    
    for datum in MATCH:
        ser=pd.DataFrame()
        press=ast.literal_eval(datum.pressure)
        temp=ast.literal_eval(datum.temperature)
        press=[-p for p in press]
        seriename=str(datum.siteCode)+"_"+str(datum.number)
        ser['pressure']=press
        ser['temperature']=temp
        ser['run']=datum.run
        data[seriename]=ser
        #df.merge(ser, on='x',how='left')
    extracted=[]
    between=(-1,-2)
    temps=[]
    for dkey in data.keys():
        d=data[dkey]
        run=d['run'][0]
        if run=="down-up":
            d=d[0:int(len(d)/11*7)]
        extract=d.loc[d['pressure']>=between[1]]
        extract=extract.loc[extract['pressure']<=between[0]]
        mean=extract.mean()
        extracted.append(mean)
        temps.append(mean['temperature'])
    if len(temps)!=0:
        globalMean=sum(temps)/len(temps)
    else:
        globalMean=None

    return extracted, globalMean

steps=1000
data=[]
for i in range(1,23):
    ext, mean= mean_temp(i)
    if False:
        print("site i passed")
    else:
        print("Site "+str(i)+" temp: "+str(mean))
        a={'site':i}
        Matchsite=match(type="Site", code=i)
        try:
            name=Matchsite[0].name
        except:
            pass
        else:
            a['name']=name
            a['mean']=mean
            a['letter']=Matchsite[0].letter
            a['Region']=Matchsite[0].region
            a['temperature']=Matchsite[0].temperature
            a['depth']=Matchsite[0].depth
            for j in range(0,len(ext)):
                a[j]=ext[j]['temperature']
            data.append(a)
with open("temp_export.csv","w",encoding="utf-8") as file:
    spamwriter = csv.writer(file, delimiter=',',
                            quotechar='|',quoting=csv.QUOTE_MINIMAL)
    for i in data:
        row=[i['site'],i['name'],i.setdefault(0),i.setdefault(1),i.setdefault(2),i['mean'],i['Region'],i['letter']]
        spamwriter.writerow(row)
df=pd.DataFrame(data)
icc(df['mean'],df['temperature'])
    


    