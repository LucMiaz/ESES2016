import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
plt.style.use('ggplot')
def icc(group1,group2):
    if len(group1)!=len(group2):
        print("length of groups do not correspond")
        return False
    N=len(group1)
    xbar=0
    
    for i in range(0,N):
        xbar+=(group1[i]+group2[i])
    xbar=xbar/(2*N)
    sum1=0
    sum2=0
    for i in range(0,N):
        sum1+=(group1[i]-xbar)**2
        sum2+=(group2[i]-xbar)**2
    s2=(sum1+sum2)/(2*N)
    r=0
    for i in range(0,N):
        r+=((group1[i]-xbar)*(group2[i]-xbar))
    r=(r)/(N*s2)
    return r
    
eses2hg=[30.,28.9,28.6,25.4,32.4,49.,48.9,55.3,240.9,57.2,44.5,29.7,36.8,25.9,28.1,29.3,32.]
eses1hg=[33.6,32.1,30.,27.3,35.3,55.4,51.5,67.2,178.8,63.5,47.1,31.,38.1,30.8,32.4,31.4,33.8]
df=pd.DataFrame()
df['hg1']=eses1hg
df['hg2']=eses2hg
df['sites']=["E.Z.02.01","E.Z.03.01","E.Z.04.01","E.Z.06.01","E.Z.07.01","E.Z.08.01","E.Z.09.01","E.Z.10.01","E.Z.11.01","E.Z.12.01","E.Z.13.01","E.Z.16.01","E.Z.17.01","E.Z.18.01","E.Z.20.01","E.Z.20.02","E.Z.21.01"]
xmax=max(max(eses1hg),max(eses2hg))
xmin=min(min(eses1hg),min(eses2hg))
extend=(xmax-xmin)/10
xmin=xmin-extend
xmax=xmax+extend
x=[xmin,xmax]
y=[xmin,xmax]
dx=pd.DataFrame()
dx['x']=x
dx['y']=y
t=stats.ttest_ind(df['hg1'],df['hg2'])
i=icc(df['hg1'],df['hg2'])
stats.describe(df['hg1'])
stats.describe(df['hg2'])
print("t test:" + str(t))
print("icc : "+str(i))

ax=dx.plot(x='x', y='y',label='1-1')
df.plot(kind='scatter',x='hg1',y='hg2',ax=ax)
plt.savefig('hgGroupComparison.pdf')


