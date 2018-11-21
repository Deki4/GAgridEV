# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 12:48:00 2018

@author: dcirovic
"""

import plotly.plotly as py
from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd

import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors

mapbox_token = 'pk.eyJ1IjoiZGNpcm92aWMiLCJhIjoiY2ptMXZ4dzZuMmszYTNrbDhsemU1bjQwZiJ9.q-_XupKSBfQhQHg3VElAaA'


def create_bus_trace(grid, buses=None, size=10, patch_type="circle", color="blue",
                     trace_name='buses'):
    """
    Create a plotly trace of PyPSA buses belonging to the grid instance.
    
    Parameters
    ----------
    Grid
    """    
     
    bus_trace = dict(type='scatter', text=[], mode='markers', hoverinfo='text', name=trace_name, 
                     marker=dict(color=color, size=size, symbol=patch_type))


    
    cmap_vals=grid.buses_t.v_mag_pu.values.tolist()[0]
    buses = grid.buses.index.tolist()
    
    bus_trace['x'], bus_trace['y'] = (grid.buses.x.tolist(),grid.buses.y.tolist())
    
    bus_trace['text']=[]
    for bus in buses:
        bus_trace['text'].append(bus+' : voltage_pu = '+str(round(grid.buses_t.v_mag_pu[bus].item(),2)))
  
        
    cmap = 'Jet' 

    if cmap_vals is not None:
        cmap_vals = cmap_vals

    cmap_vals = grid.buses_t.v_mag_pu.values.tolist()[0]
    cmin=0.975
    cmax=1.030
    

    bus_trace['marker'] = go.scattermapbox.Marker(size=size,
                                 color=cmap_vals, cmin=cmin, cmax=cmax,
                                 colorscale=cmap,
                                 colorbar=go.scattermapbox.marker.ColorBar(thickness=10,
                                                   x=1.0,
                                                   titleside='right',title='Bus Voltage(pu)'),
                                 )

    return [bus_trace]
            

    
def create_line_trace(grid, lines=None, width=4.0,color='orange', 
                      trace_name='lines',show_colorbar = True):
    """
    Create a plotly trace of PyPSA lines belonging to the grid instance.
    """
    
    
    cmap_vals = grid.line_loading.values.tolist()
    cmin = 20
    cmax = 100
    bus_coords = grid.buses[['x','y']].copy()
 
    
    lines2plot = grid.lines
#    line_traces = []
#
#    for name, row in lines2plot.iterrows():
#        
#        line_trace = dict(type='scatter', text=[], hoverinfo='text', mode='lines', name=trace_name,
#                              line=dict(width=width, color=color))
#
#        line_trace['x'], line_trace['y'] =  ([bus_coords.loc[row.loc['bus0']].x,bus_coords.loc[row.loc['bus1']].x],
#                      [bus_coords.loc[row.loc['bus0']].y,bus_coords.loc[row.loc['bus1']].y])
#        line_trace['text'] = name
#        line_traces.append(line_trace)
    
    
    cmap = 'coolwarm'
    cmap_lines = get_plotly_cmap(cmap_vals, cmap_name=cmap, cmin=cmin, cmax=cmax)
    
    line_traces = []
    col_i = 0
    for name, row in lines2plot.iterrows():
        line_trace = dict(type='scatter', text=[], hoverinfo='text', mode='lines', name=name,
                          line=dict(width=width, color=color))#can probably get rid of color param

        line_trace['x'], line_trace['y'] =  ([bus_coords.loc[row.loc['bus0']].x,bus_coords.loc[row.loc['bus1']].x],
                      [bus_coords.loc[row.loc['bus0']].y,bus_coords.loc[row.loc['bus1']].y])
            
        line_trace['line']['color'] = cmap_lines[col_i]
        
        line_trace['text'] = name + ' : Loading =' + str(round(grid.line_loading.loc[name],2))

        line_traces.append(line_trace)
        col_i += 1
        
    lines_cbar = dict(type='scatter',x=[grid.buses.x[0]], y=[grid.buses.y[0]], mode='markers',showlegend=False,
                                  marker=go.scattermapbox.Marker(size=0, cmin=cmin, cmax=cmax,
                                                color='rgb(255,255,255)',
                                                colorscale=matplotlib_to_plotly(cmap,255),
                                                colorbar=go.scattermapbox.marker.ColorBar(thickness=10,
                                                                  x=1.1,
                                                                  titleside='right',title='Line Loading %')
                                                ))    
                                                
    line_traces.append(lines_cbar)                                            
    x = []
    y = []
    text = []
    
    #Plotly doesn't have hover for lines, therefore, set up an invisible
    #mid-point on each line to be used for hover.
    for line in line_traces:
        try:
            xs,ys = (sum(line['x'])/2, sum(line['y'])/2)
            lineID = line['text']
             
            x.append(xs)
            y.append(ys)
            text.append(lineID)
        except KeyError:
            pass
       
    mid_trace = dict(type='scatter',x=[],y=[],text=[], mode='markers', hoverinfo='text', 
                     marker=dict(opacity=0),showlegend=False)
    
    mid_trace['x'], mid_trace['y'] = (x,y)
    
    mid_trace['text'] = text    
    return line_traces+[mid_trace]


def create_trafo_trace(grid, color='green', width=5, trace_name='trafos'):
    """
    Create a Plotly trace of PyPSA transformers belonging to the grid instance
    """
    
    trafos = grid.transformers.index.tolist()
    trafo_traces=[]
    
    for trafo in trafos:
        trafo_bus0 = grid.transformers.loc[trafo].bus0
        trafo_bus1 = grid.transformers.loc[trafo].bus1
        trafo_trace = dict(type='scatter', text=[], hoverinfo='text', mode='lines', name=trace_name,
                          line=dict(width=width, color=color))

        trafo_trace['x'], trafo_trace['y'] =  ([grid.buses.loc[trafo_bus0].x,grid.buses.loc[trafo_bus1].x],
                      [grid.buses.loc[trafo_bus0].y,grid.buses.loc[trafo_bus1].y])
        
        
    trafo_traces.append(trafo_trace)
    return trafo_traces


    
def draw_traces(overloaded_grid,reinforced_grid, map_style='basic', figsize=1,
                aspectratio='auto'):
    
    """
    Return the Plotly fig object of all traces for the overloaded grid object
    and for the current, reinforced grid object. Compare the grids side by
    side on a Plotly graph.
    """
    
    ovd_traces = create_trafo_trace(overloaded_grid)+create_line_trace(overloaded_grid)+create_bus_trace(overloaded_grid) #has to be in this order
    reinf_traces = create_trafo_trace(reinforced_grid)+create_line_trace(reinforced_grid)+create_bus_trace(reinforced_grid)
    for trace in ovd_traces:
            trace['lat'] = trace.pop('y')
            trace['lon'] = trace.pop('x')
            trace['type'] = 'scattermapbox'
            trace['subplot']='mapbox'
    for trace in reinf_traces:
            trace['lat'] = trace.pop('y')
            trace['lon'] = trace.pop('x')
            trace['type'] = 'scattermapbox'
            trace['subplot']='mapbox2'        
            
    
    fig = go.Figure(data=ovd_traces+reinf_traces,   # edge_trace
                 layout=go.Layout(
                     titlefont=dict(size=16),
                     showlegend=True,
                     autosize=True,
                     hovermode='closest',
                      legend=dict(x=0, y=1.0)
                 ),)
    fig['layout']['mapbox'] = dict(accesstoken=mapbox_token,
                                       bearing=0,
                                       center=dict(lat= pd.Series(ovd_traces[0]['lat']).dropna().mean(),
                                                   lon= pd.Series(ovd_traces[0]['lon']).dropna().mean()),
                                       style=map_style,
                                       pitch=0,
                                       zoom=15,
                                       domain=dict(x=[0,0.49], y=[0,1]))
                                       
    fig['layout']['mapbox2'] = dict(accesstoken=mapbox_token,
                                       bearing=0,
                                       center=dict(lat= pd.Series(reinf_traces[0]['lat']).dropna().mean(),
                                                   lon= pd.Series(reinf_traces[0]['lon']).dropna().mean()),
                                       style=map_style,
                                       pitch=0,
                                       zoom=15,
                                       domain=dict(x=[0.51,1], y=[0,1]))
    annotations = [dict(text="Overloaded Grid",showarrow=False, x=0.2,y=1, font=dict(size=16)),dict(text="Reinforced Grid",showarrow=False, x=0.8,y=1,font=dict(size=16))]
    fig['layout']['annotations'] = annotations
                                       
    return fig


def get_plotly_cmap(values, cmap_name='jet', cmin=None, cmax=None):
    cmap = cm.get_cmap(cmap_name)
    if cmin is None:
        cmin = values.min()
    if cmax is None:
        cmax = values.max()
    norm = colors.Normalize(vmin=cmin, vmax=cmax)
    bus_fill_colors_rgba = cmap(norm(values).data)[:, 0:3] * 255.
    return ['rgb({0},{1},{2})'.format(r, g, b) for r, g, b in bus_fill_colors_rgba]



def matplotlib_to_plotly(cmap, pl_entries):
    cmap = cm.get_cmap(cmap)
    h = 1.0/(pl_entries-1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = list(map(np.uint8, np.array(cmap(k*h)[:3])*255))
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale



















