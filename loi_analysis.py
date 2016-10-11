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
#getting the data
"""
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
"""
#plotting
f, ax = plt.subplots()
f.set_tight_layout(True)
sns.set(style="white", color_codes=True)
#ax.set(xlim=(0., 1.), ylim=(0., 1.))
"""
g=sns.jointplot(df['loi'], df['loiHg'], kind="hex", 
            stat_func=kendalltau, 
            color="#4CB391")
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

"""
writer = pd.ExcelWriter('statistics_161010_description of Hg by region_lumi.xlsx', engine='xlsxwriter')
data=RUN_df('MATCH p=(n:Observation)-[r:OF]->(s:Sample)-[:FROM]->(i:Site) where n.type="Hg" AND NOT r.Hg_="None" AND s.type="Sediment" return n.group as group, r.Hg_ as hg, s.code as code, r.sampleWg as weight, i.regionSed as region, 1-(r.boatANDashWg-r.boatWg)/r.sampleWg as loi, i.code as site, s.depth as depth, i.letter+": "+i.code as letter')


"""
df = data.groupby('code').agg(
    {'hg':{'sum':'sum','mean':'mean', 'std':'std','median':'median'}})
re=df.loc[df['hg']['std']/df['hg']['mean']>0.01]
re.to_excel('hgDMA_161010_samples with high std.xlsx','description')
dfarea=data.groupby(['code','region'], as_index=False).mean().groupby('region').agg({'hg':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count'},'loi':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count'}})


dfarea['hg']['cov']=dfarea['hg']['std']/dfarea['hg']['mean']
dfarea['loi']['cov']=dfarea['loi']['std']/dfarea['loi']['mean']


dfhg=data.groupby(['code','region']).agg({'hg':{'mean':'mean','median':'median', 'std':'std','max':'max','min':'min','count':'count'},'loi':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count'}})
dfhg['hg']['cov']=dfhg['hg']['std']/dfhg['hg']['mean']
dfhg['loi']['cov']=dfhg['loi']['std']/dfhg['loi']['mean']
dfarea.to_excel(writer,'by region')
dfhg.to_excel(writer,'by code')

"""
def depth_sep(depth):
    if depth=="01+02" or depth=="00+03" or depth <4:
        return "top"
    elif depth>3 and depth <100:
        return "bottom"
    else:
        return "not working"

depthcat=[]
for datum in data['depth']:
    depthcat.append(depth_sep(datum))

data['depthCat']=depthcat
        

df = data.groupby(['code', 'site', 'depth']).aggregate({'hg':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count','cov':np.cov},'loi':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count','cov':np.cov}})
df.to_excel(writer,'all samples')
dfregions=data.groupby(['site']).aggregate({'hg':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count','cov':np.cov},'loi':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count','cov':np.cov}})
dfregions.to_excel(writer,'by site')
dfdepthsite = data.groupby(['site','depthCat']).aggregate({'hg':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count','cov':np.cov},'loi':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count','cov':np.cov}})
dfdepthsite.to_excel(writer,"by site-depth")
dfdepthsite = data.groupby(['depthCat','region']).aggregate({'hg':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count','cov':np.cov},'loi':{'mean':'mean','std':'std','median':'median','max':'max','min':'min','count':'count','cov':np.cov}})
dfdepthsite.to_excel(writer,"by region-depth")

dfds=data.groupby(['letter','depthCat']).aggregate({'hg':{'mean':'mean'}})

colors = {'Mälaren':"#66c2a5", 'Baltic Sea':"#fc8d62", 'Stockholm':"#8da0cb"}

regioncolors=[colors[d] for d in data['region']]

g=(sns.jointplot('loi', 'hg', data=data, label='region', c=regioncolors)
            .plot_joint(sns.kdeplot, zorder=0, n_levels=10))
plt.savefig('loiHg_comparison_plot_kde.pdf')

data.boxplot(['hg'], by=['depth'])

dfpivot= data.pivot_table(values=["hg"], index=["site","depth"], aggfunc=np.mean).unstack()
dfds.unstack().plot(kind="bar",color=["#66c2a5","#fc8d62","#8da0cb","#e78ac3"], width=1, logy=True,legend=True)
plt.savefig('bardept1h.pdf')
writer.save()
writer.close()

