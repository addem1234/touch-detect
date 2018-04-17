import sys
import igraph as ig

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


if __name__ == '__main__':
    for neuron in parse_files(sys.argv[1:]):
        nodelist = list(nodes(neuron))

        edtelist = list(edges(neuron))

        Xn = [n.coords[0] for n in nodelist]# x-coordinates of nodelist
        Yn = [n.coords[1] for n in nodelist]# y-coordinates
        Zn = [n.coords[2] for n in nodelist]# z-coordinates

        Xe = []
        Ye = []
        Ze = []
        for n, nn in edtelist:
            Xe += [n[0], nn[0], None]# x-coordinates of edge ends
            Ye += [n[1], nn[1], None]# y-coordinates
            Ze += [n[2], nn[2], None]# z-coordinates


        trace1=Scatter3d(
                x=Xe,
                y=Ye,
                z=Ze,
                mode='lines',
                line=Line(color='rgb(125,125,125)', width=1),
                    hoverinfo='none'
            )
        trace2=Scatter3d(
                x=Xn,
                y=Yn,
                z=Zn,
                mode='markers',
                name='neurites',
                marker=Marker(symbol='dot',
                    size=1,
                    #color=group,
                    colorscale='Viridis',
                    line=Line(color='rgb(50,50,50)', width=0.5)
                ),
                #text=labels,
                hoverinfo='text'
            )

        axis=dict(showbackground=False,
                showline=False,
                zeroline=False,
                showgrid=False,
                showticklabels=False,
                title=''
        )

        layout = Layout(
                title=neuron.filename,
                width=1000,
                height=1000,
                showlegend=False,
                scene=Scene(
                    xaxis=XAxis(axis),
                    yaxis=YAxis(axis),
                    zaxis=ZAxis(axis),
                    ),
                margin=Margin(
                    t=100
                    ),
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
                        font=Font(
                            size=14
                            )
                        )
                    ]),
            )

        data=Data([trace1, trace2])
        fig=Figure(data=data, layout=layout)

        n = plotly.offline.plot(fig, filename='graphs/' + neuron.filename)
        print('done', n)

