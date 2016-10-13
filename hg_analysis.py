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

from bokeh import mpl
from bokeh.plotting import output_file, show

today=dtm.datetime.today()
today= str(today.year)+str(today.month)+str(today.day)
FileNameExcel="PFxx_"+today+".xlsx"

#creating excel writer
writer = pd.ExcelWriter(FileNameExcel, engine='xlsxwriter')



#getting the data
data=RUN_df('MATCH p=(n:Observation)-[r:OF]->(s:Sample)-[:FROM]->(i:Site) where n.type="Hg" AND NOT s.code="tom" return s.code as code, i.regionSed as region, i.code as site, i.letter+": "+i.code as letter, r.Hg_ as hg, s.depth as depth')

ORIGINS = ['Ref Mälaren', 'Mälaren', 'Stockholm', 'Stockholm 2', 'Baltic Sea','Ref Baltic Sea']
data['region']=[str(ORIGINS.index(d))+". "+d for d in data['region']]
dfcode = data.groupby(['code','region'],as_index=False).mean()



sns.stripplot('region', 'hg', data=dfcode,jitter=True, edgecolor='none', alpha=.40)
sns.despine(offset=10, trim=True);
plt.savefig('hgboxHg.pdf')
sns.stripplot('region', 'hg', data=dfcode,jitter=False, edgecolor='none', alpha=.40)
sns.despine(offset=10, trim=True);
plt.savefig('hgbox2.pdf')
sns.violinplot('region', 'hg', data=dfcode)
sns.despine(offset=10, trim=True);
plt.savefig('hgbox3.pdf')
sns.set_style("whitegrid")

# ax = sns.violinplot(x="size", y="tip", data=tips.sort("size"))
# ax = sns.violinplot(x="size", y="tip", data=tips,
#                     order=np.arange(1, 7), palette="Blues_d")
# ax = sns.violinplot(x="day", y="total_bill", hue="sex",
#                     data=tips, palette="Set2", split=True,
#                     scale="count")
ax = sns.violinplot(x="region", y="hg", 
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


output_file("hgviolin.html")

show(mpl.to_bokeh())