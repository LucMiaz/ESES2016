from os.path import dircode, join

import pandas as pd

from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Slider, Button, DataTable, TableColumn, NumberFormatter
from bokeh.io import curdoc
from classes import RUN_df
df =RUN_df('MATCH p=(n:Observation)-[r:OF]->(s:Sample)-[:FROM]->(i:Site) where n.type="PFxx" match q=(m:Observation)-[t:OF]->(s:Sample) where m.type="Hg" return s.code as code, i.regionSed as region, i.code as site, i.letter+": "+i.code as letter, r.PFOS as pfos, s.depth as depth, t.Hg_ as hg, (s.ceramicAndSampleWg - s.ceramicAfterBurnWg)/(s.ceramicAndSampleWg - s.ceramicWg) as loi, 1-(s.drySampleWg/s.wetSampleWg) as wc, 1-(t.boatANDashWg-t.boatWg)/t.sampleWg as loiStar ')
source = ColumnDataSource(data=dict())

def update():
    current = df[df['hg'] <= slider.value].dropna()
    source.data = {
        'code'             : current.code,
        'hg'           : current.hg,
        'site' : current.site,
    }

slider = Slider(title="Max Salary", start=10000, end=250000, value=150000, step=1000)
slider.on_change('value', lambda attr, old, new: update())

button = Button(label="Download", button_type="success")
button.callback = CustomJS(args=dict(source=source),
                           code=open(join(dircode(__file__), "download.js")).read())

columns = [
    TableColumn(field="code", title="Employee Name"),
    TableColumn(field="hg", title="Income", formatter=NumberFormatter(format="$0,0.00")),
    TableColumn(field="site", title="Experience (years)")
]

data_table = DataTable(source=source, columns=columns, width=800)

controls = widgetbox(slider, button)
table = widgetbox(data_table)

curdoc().add_root(row(controls, table))
curdoc().title = "Export CSV"

update()
