import numpy as np

import cairocffi as cairo
import matplotlib as mpl
mpl.use("Cairo")
import matplotlib.pyplot as plt
from classes import RUN, RUN_df
import pandas as pd
import numpy as np
from scipy.stats import kendalltau
from scipy import cluster
import seaborn as sns
from icc import icc
import xlsxwriter
writer = pd.ExcelWriter('statistics_161010_description of Hg by region_lumi.xlsx', engine='xlsxwriter')
data=RUN_df('MATCH p=(n:Observation)-[r:OF]->(s:Sample)-[:FROM]->(i:Site) where n.type="Hg" AND NOT r.Hg_="None" return n.group as group, r.Hg_ as hg, s.code as code, r.sampleWg as weight, i.region as region, 1-(r.boatANDashWg-r.boatWg)/r.sampleWg as loi, i.code as site, s.depth as depth')

df=data.groupby('site').mean()


writer.save()

writer.close()