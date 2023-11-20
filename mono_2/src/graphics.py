import json

import plotly.graph_objects as go
import plotly.express as px
import os
import json
import plotly.express as px

direct = "%s"%(os.getcwd())
fig = go.Figure()
 
data = []
for i in range(10):
    f = open(f'../json/output/graphics/graphics-seed-{i+1}-time-900.json')
    data.append(json.load(f))

graph_data = []
best_value = 4125
for i in range(len(data)):
    graph_data.append({
        'times': [],
        'gaps': []
    })
    for item in data[i]:
        if item['value'] != 0:
            gap = ((item['value'] - best_value) / item['value']) * 100
        else:
            gap = 0

        graph_data[i]['times'].append(item['time'])
        graph_data[i]['gaps'].append(gap)

fig.update_layout(title="%s"%('LAHC-mono'),
                   xaxis_title="Tempo (s)",
                   yaxis_title='GAP (%)')

for i in range(10):
    fig.add_trace(go.Scatter(x=graph_data[i]['times'], y=graph_data[i]['gaps'], mode = 'lines', name = f"Seed {i + 1}", line=dict(color=px.colors.qualitative.swatches().data[14].marker.color[i], width=4)))

fig.update_layout(
    # title="Plot Title",
    # xaxis_title="X Axis Title",
    # yaxis_title="Y Axis Title",
    # legend_title="Legend Title",
    font=dict(
        # family="Arial",
        size=30,
        # color="RebeccaPurple"
    )
)

fig.write_html("%s/%s.html"%('../graphics/', 'lahc_mono'))

# print(graph_data)
