import sys
from itertools import chain
from random import random

import plotly.plotly as py
import plotly.offline
from plotly.graph_objs import *

from parser import parse_files

def nodes(neurite):
    yield neurite

    for child in neurite.children:
        for item in nodes(child):
            yield item

def edges(neurite):
    for child in neurite.children:
        yield (neurite, child)

        for item in edges(child):
            yield item

def neuron2trace(neuron):
    nodelist = list(nodes(neuron))
    edgelist = list(edges(neuron))

    Xn, Yn, Zn = zip(*[n.coords for n in nodelist])

    groups = [n.type for n in nodelist]
    sizes = [n.r if n.r > 2 else 2 for n in nodelist]

    Xe = []
    Ye = []
    Ze = []
    for n, nn in edgelist:
        Xe += [n[0], nn[0], None]# x-coordinates of edge ends
        Ye += [n[1], nn[1], None]# y-coordinates
        Ze += [n[2], nn[2], None]# z-coordinates


    lines=Scatter3d(x=Xe, y=Ye, z=Ze,
        mode='lines',
        hoverinfo='none',
        line=Line(color='rgb(125,125,125)', width=1),
    )
    markers=Scatter3d(x=Xn, y=Yn, z=Zn,
        mode='markers',
        name='neurites',
        hoverinfo='text',
        marker=Marker(symbol='dot',
            size=sizes,
            color=groups,
            colorscale='Viridis',
            line=Line(color='rgb(50,50,50)', width=0.5)
        ),
    )

    return lines, markers

if __name__ == '__main__':
    neurons = parse_files(sys.argv[1:])[:10]
    size = 100 * len(neurons)
    for n in neurons:
        x, y, z = [ random() * size - size for _ in range(3) ]
        for nn in n.neurites(): nn.translate(x, y, z)

    traces = list(chain(*[ neuron2trace(n) for n in neurons ]))

    axis=dict(showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title=''
    )

    layout = Layout(
        width=1000,
        height=1000,
        showlegend=False,
        scene=Scene(
                xaxis=XAxis(axis),
                yaxis=YAxis(axis),
                zaxis=ZAxis(axis),
            ),
        margin=Margin(t=100),
        hovermode='closest',
        annotations=Annotations([
                Annotation(
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=0.1,
                    xanchor='left',
                    yanchor='bottom',
                    font=Font(size=14)
                )
            ]),
    )

    fig=Figure(data=Data(traces), layout=layout)
    plotly.offline.plot(fig, filename='graphs/' + neurons[0].filename)

