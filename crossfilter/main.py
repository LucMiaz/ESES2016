#bokeh serve --show crossfilter

import pandas as pd

from bokeh.layouts import row, widgetbox
from bokeh.models import Select
from bokeh.palettes import Spectral7
from bokeh.plotting import curdoc, figure
from bokeh.sampledata.autompg import autompg
from classes import RUN_df
df =RUN_df('MATCH p=(n:Observation)-[r:OF]->(s:Sample)-[:FROM]->(i:Site) where n.type="PFxx" match q=(m:Observation)-[t:OF]->(s:Sample) where m.type="Hg" return s.code as code, i.regionSed as region, i.code as site, i.letter+": "+i.code as letter, r.PFOS as pfos, s.depth as depth, t.Hg_ as hg, (s.ceramicAndSampleWg - s.ceramicAfterBurnWg)/(s.ceramicAndSampleWg - s.ceramicWg) as loi, 1-(s.drySampleWg/s.wetSampleWg) as wc, 1-(t.boatANDashWg-t.boatWg)/t.sampleWg as loiStar ')

SIZES = list(range(6, 22, 3))
COLORS = Spectral7
ORIGINS = ['Ref Mälaren', 'Mälaren', 'Stockholm', 'Stockholm 2', 'Baltic Sea','Ref Baltic Sea']
df['region']=[str(ORIGINS.index(d))+". "+d for d in df['region']]
columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]
quantileable = [x for x in continuous if len(df[x].unique()) > 20]
df['hg']=[round(float(d),4) if d and d!="None" else 0 for d in df['hg']]
df['depth']=[int(d) if not isinstance(d,str) else int(d[-1]) for d in df['depth']]
def create_figure():
    xs = df[x.value].values
    ys = df[y.value].values
    x_title = x.value.title()
    y_title = y.value.title()

    kw = dict()
    if x.value in discrete:
        kw['x_range'] = sorted(set(xs))
    if y.value in discrete:
        kw['y_range'] = sorted(set(ys))
    kw['title'] = "%s vs %s" % (x_title, y_title)

    p = figure(plot_height=600, plot_width=800, tools='pan,wheel_zoom, save, box_zoom,reset', **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title

    if x.value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    sz = 9
    if size.value != 'None':
        groups = pd.qcut(df[size.value].values, len(SIZES))
        sz = [SIZES[xx] for xx in groups.codes]

    c = "#31AADE"
    if color.value != 'None':
        groups = pd.qcut(df[color.value].values, len(COLORS))
        c = [COLORS[xx] for xx in groups.codes]
    p.circle(x=xs, y=ys, color=c, size=sz, line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5)

    return p


def update(attr, old, new):
    layout.children[1] = create_figure()


x = Select(title='X-Axis', value='region', options=columns)
x.on_change('value', update)

y = Select(title='Y-Axis', value='pfos', options=columns)
y.on_change('value', update)

size = Select(title='Size', value='None', options=['None'] + quantileable)
size.on_change('value', update)

color = Select(title='Color', value='None', options=['None'] + quantileable)
color.on_change('value', update)

controls = widgetbox([x, y, color, size], width=200)
layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "ESES2016"
