#bokeh serve --show crossfilter

import pandas as pd

from bokeh.charts import Chart, color, marker
from classes import RUN
import ast
#getting the data
data=RUN('MATCH (ctd:Instrument)<-[r:TAKEN_WITH]-(s:Sample)-[:TAKEN_IN]->(i:Site) where s.number < 4 return s.code as code, s.site as site, s.number as number, s.pressure as depth, s.runs as runs, s.temperature as temperature, s.salinity as salinity, s.conductivity as conductivity, i.region as region')
dd={}
dcodes={}
bins=list(range(0,101,1))
for row in data:
    df=pd.DataFrame()
    code=row['code']
    df['temperature']=ast.literal_eval(row['temperature'])
    df['salinity']=ast.literal_eval(row['salinity'])
    df['conductivity']=ast.literal_eval(row['conductivity'])
    df['depth']=ast.literal_eval(row['depth'])
    df=df.loc[df['depth']>=0]
    df['depthCat'] = pd.cut(df['depth'], bins, labels=bins[1:])
    dd[code]=df
    dcodes[code]={"site":row['site'],"region":row['region'],"runs":row['runs'],"number":row['number']}
colors=[["#2ca25f","#99d8c9","#e5f5f9"],["#8856a7","#9ebcda","#e0ecf4"],["#43a2ca","#a8ddb5","#e0f3db"],["#e34a33","#fdbb84","#fee8c8"],["#2b8cbe","#a6bddb","#ece7f2"],["#dd1c77","#c994c7","#e7e1ef"],["#636363","#bdbdbd","#f0f0f0"]]

for key in dd.keys():
    df=dd[key]
    Chart(df, color=colors[int(dcodes[key]['site'])%7][int(dcodes[key]['number'])])
