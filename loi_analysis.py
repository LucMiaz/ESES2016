import cairocffi as cairo
import matplotlib as mpl
mpl.use("Cairo")
import matplotlib.pyplot as plt
from classes import RUN
import pandas as pd
import numpy as np
from scipy.stats import kendalltau
from scipy import stats
import seaborn as sns
from icc import icc
#getting the data
data=list(RUN('MATCH (s:Site)<-[:TAKEN_IN]-(n:Sample{type:"Sediment"})<-[:MEASURE_OF]-(m)-[:MEASURED_ON]->(o) return n.code as code,n.loi as loi, m.code as mcode,m.W_boatANDash as boatashWg, m.W_boat as boatWg, o.group as group, m.W_sample as sampleWg, s.region as region'))
datafr={"code":[],"loi":[],"loiHg":[],"region":[], "group":[]}

for el in data:
    boatashWg=el['boatashWg']
    boatWg=el['boatWg']
    sampleWg=el['sampleWg']
    loiHg=1-(boatashWg-boatWg)/sampleWg
    if loiHg<0 or loiHg>1 or el['code']!=el['mcode']:
        print(el['code']+":    "+str(boatWg)+",    "+str(boatashWg)+",    "+str(sampleWg)+",    "+str(loiHg)+",    "+str(el['loi']))
    else:
        datafr['code'].append(el["code"])
        datafr['loi'].append(el['loi'])
        datafr['loiHg'].append(loiHg)
        datafr['region'].append(el['region'])
        datafr['group'].append(el['group'])
df = pd.DataFrame()
df['code']=datafr['code']
df['loi']=datafr['loi']
df['loiHg']=datafr['loiHg']
df['region']=datafr['region']
df['group']=datafr['group']

#plotting
f, ax = plt.subplots()
f.set_tight_layout(True)
sns.set(style="white", color_codes=True)
#ax.set(xlim=(0., 1.), ylim=(0., 1.))
g=sns.jointplot(df['loi'], df['loiHg'], kind="hex", 
            stat_func=kendalltau, 
            color="#4CB391",
            size=7)
plt.savefig('loi_comparison_plot_kendeltau.png')

g=(sns.jointplot('loi', 'loiHg', data=df, color="k")
            .plot_joint(sns.kdeplot, zorder=0, n_levels=6))
plt.savefig('loi_comparison_plot_kde.pdf')

f, ax = plt.subplots()
sns.boxplot(df["loi"], df["loiHg"])
plt.savefig('loi-by-region.pdf')

f, ax = plt.subplots()
h = sns.FacetGrid(df, col="region", hue="code")
h.map(plt.scatter, "loi", "loiHg", alpha=.7)
h.add_legend();
plt.savefig('loi-by-region-scatter.pdf')

f, ax = plt.subplots()
sns.violinplot(data=df)
sns.despine(offset=10, trim=True);
plt.savefig('violinplots-loi-loiHg.png')

f, ax = plt.subplots()
sns.violinplot('region', 'loi', data=df)
sns.despine(offset=10, trim=True);
plt.savefig('violinplots-region-loi.png')
iccloi=icc(df['loi'],df['loiHg'])

sns.violinplot('region', 'loi', data=df)
sns.despine(offset=10, trim=True);
plt.savefig('violinplots-region-loi.png')

print("icc : "+str(iccloi))
ttestloi=stats.ttest_ind(df['loi'],df['loiHg'])
print("t-test : "+str(ttestloi))
loidesc=stats.describe(df['loi'])
print("loi : "+str(loidesc))
loihgdesc=stats.describe(df['loiHg'])
print("loiHg: "+str(loihgdesc))

groupSum=(df.groupby('code')).sum()
groupSum.plot.scatter('loi','loiHg')
plt.savefig('scatter-loi-loiHg.pdf')
k=(sns.jointplot('loi', 'loiHg', data=groupSum, color="k")
            .plot_joint(sns.kdeplot, zorder=0, n_levels=6))
plt.savefig('joinplot-loi-loiHg_grouped.pdf')

data2=RUN_df('MATCH p=(n:Observation)-[r:OF]->(s:Sample) where n.type="Hg" return n.group as group, 1-(r.boatANDashWg-r.boatWg)/r.sampleWg as loiStar, s.loi as loi, s.code as code')


