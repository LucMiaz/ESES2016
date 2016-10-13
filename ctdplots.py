import cairocffi as cairo
import matplotlib as mpl
mpl.use("Cairo")
import matplotlib.pyplot as plt
from classes import RUN, RUN_df
import pandas as pd
import numpy as np
from scipy.stats import kendalltau
from scipy import stats
import seaborn as sns
from icc import icc
import xlsxwriter
import datetime as dtm
import ast
from bokeh import mpl
from bokeh.plotting import output_file, show



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
    
dfcode=data.groupby(['code','depth','region','site'],as_index=False).mean()

sns.stripplot('region', 'temperature', data=dfcode,jitter=True, edgecolor='none', alpha=.40)
sns.despine(offset=10, trim=True);
plt.savefig('boxtemp.pdf')
sns.stripplot('region', 'temperature', data=dfcode,jitter=False, edgecolor='none', alpha=.40)
sns.despine(offset=10, trim=True);
plt.savefig('boxctd2.pdf')
sns.violinplot('region', 'pfos', data=dfcode)
sns.despine(offset=10, trim=True);
plt.savefig('boxctd3.pdf')
sns.set_style("whitegrid")

# ax = sns.violinplot(x="size", y="tip", data=tips.sort("size"))
# ax = sns.violinplot(x="size", y="tip", data=tips,
#                     order=np.arange(1, 7), palette="Blues_d")
# ax = sns.violinplot(x="day", y="total_bill", hue="sex",
#                     data=tips, palette="Set2", split=True,
#                     scale="count")
ax = sns.violinplot(x="depth", y="salinity", hue='temperature',
                    data=dfcode, palette="Set2", split=True,
                    scale="count", inner="stick")
# ax = sns.violinplot(x="day", y="total_bill", hue="smoker",
#                     data=tips, palette="muted", split=True)
# ax = sns.violinplot(x="day", y="total_bill", hue="smoker",
#                     data=tips, palette="muted")

# planets = sns.load_dataset("planets")
# ax = sns.violinplot(x="orbital_period", y="method",
#                     data=planets[planets.orbital_period < 1000],
#                     scale="width", palette="Set3")


output_file("violinctd.html")

show(mpl.to_bokeh())