'''
Created on 03.08.2018

@author: dcirovic
'''
import folium
import branca
import branca.colormap as cm
from branca.element import *


def plot_grid(overloaded_grid,reinforced_grid):
    
    # Latitude and longitude to which to center the map around
    lat = reinforced_grid.buses.y.mean()
    lon = reinforced_grid.buses.x.mean()
    zoom_start = 15
    #===========================================================================
    # loading = check_lines.loading(network)
    #===========================================================================
    
    f = branca.element.Figure()
    d1 = f.add_subplot(1, 2, 1)
    d2 = f.add_subplot(1, 2, 2)
    # Initialize folium map object
    overloaded_map = folium.Map(location=[lat, lon], 
                         zoom_start=zoom_start)
    
    reinforced_map = folium.Map(location=[lat, lon], 
                         zoom_start=zoom_start)
    
    d1.html.add_child(Element("<h1>Overloaded Grid</h1>"))   # Currently only way to create title is with HTML code
        
    d2.html.add_child(Element("<h1>Reinforced Grid</h1>"))
        
    #Create continuous linear colormaps for line overloading and bus overvoltage
    linear = cm.LinearColormap(['green','yellow','red'], 
                               vmin=20 ,vmax=100)
    linear.caption = 'Line Overloading in %'
    linear2 = cm.LinearColormap(['blue','green','red'], 
                               vmin=0.975 ,vmax=1.03)
    linear2.caption = 'bus voltage pu'
    
    #Add bus voltages to dataframe of bus coordinates
    bus_coords = reinforced_grid.buses[['x','y']].copy()
    overloaded_bus_coords = bus_coords.assign(voltage_pu=overloaded_grid.buses_t.v_mag_pu.T.values)
    reinforced_bus_coords = bus_coords.assign(voltage_pu=reinforced_grid.buses_t.v_mag_pu.T.values)
    
    #Plot buses and corresponding pu voltage with colormap
    for bus_name, row in overloaded_bus_coords.iterrows():
        folium.RegularPolygonMarker([row.y,row.x],popup=bus_name+' : '+ str(round(row.voltage_pu,3)),
                                    fill_color=linear2(row.voltage_pu),number_of_sides=8,radius=8).add_to(overloaded_map)
                        
    #Plot buses and corresponding pu voltage with colormap
    for bus_name, row in reinforced_bus_coords.iterrows():
        folium.RegularPolygonMarker([row.y,row.x],popup=bus_name+' : '+ str(round(row.voltage_pu,3)),
                                    fill_color=linear2(row.voltage_pu),number_of_sides=8,radius=8).add_to(reinforced_map)
                                    
                                    
    # Plot lines and corresponding overloading with colormap
    #[::-1] to reverse coordinates to be in accordance with folium 
    overloaded_lines = overloaded_grid.lines[['bus0','bus1']].copy()
    bus_coords = overloaded_grid.buses[['x','y']].copy()   # reset to be without pu voltages
    for name,row in overloaded_lines.iterrows():
        overloaded_lines.at[name,'bus0'] = bus_coords.loc[row.loc['bus0']].tolist()[::-1]
        overloaded_lines.at[name,'bus1'] = bus_coords.loc[row.loc['bus1']].tolist()[::-1]
    overloaded_lines = overloaded_lines.assign(loading=overloaded_grid.line_loading.values)
    
    os_lines = overloaded_grid.os_lines[['bus0','bus1']].copy()
    for name,row in os_lines.iterrows():
        os_lines.at[name,'bus0'] = bus_coords.loc[row.loc['bus0']].tolist()[::-1]
        os_lines.at[name,'bus1'] = bus_coords.loc[row.loc['bus1']].tolist()[::-1]

    
    reinforced_lines = reinforced_grid.lines[['bus0','bus1']].copy()
    bus_coords = reinforced_grid.buses[['x','y']].copy()   # reset to be without pu voltages
    for name,row in reinforced_lines.iterrows():
        reinforced_lines.at[name,'bus0'] = bus_coords.loc[row.loc['bus0']].tolist()[::-1]
        reinforced_lines.at[name,'bus1'] = bus_coords.loc[row.loc['bus1']].tolist()[::-1]
    reinforced_lines = reinforced_lines.assign(loading=reinforced_grid.line_loading.values)
    
    for name,row in overloaded_lines.iterrows():
        folium.PolyLine([row.bus0,row.bus1],popup=name+ ', loading: ' + str(round(row.loading,3)),
                        color=linear(row.loading),weight=2).add_to(overloaded_map)
        
    for name,row in os_lines.iterrows():
        folium.PolyLine([row.bus0,row.bus1],popup = 'out of service line: ' + name,opacity = 0.3).add_to(overloaded_map)
                    
    for name,row in reinforced_lines.iterrows():
        folium.PolyLine([row.bus0,row.bus1],popup=name+ ', loading: ' + str(round(row.loading,3)),
                        color=linear(row.loading),weight=5).add_to(reinforced_map)
    
    
    # Plot transformers as lines connecting mv and lv buses
    # [::-1] to reverse coordinates to be in accordance with folium 
    transformers = reinforced_grid.transformers.copy()
    for name,row in transformers.iterrows():
        transformers.at[name,'bus0'] = bus_coords.loc[row.loc['bus0']].tolist()[::-1]
        transformers.at[name,'bus1'] = bus_coords.loc[row.loc['bus1']].tolist()[::-1]
    for name,row in transformers.iterrows():
        folium.PolyLine([row.bus0,row.bus1],popup=name,color='blue').add_to(overloaded_map)
    for name,row in transformers.iterrows():
        folium.PolyLine([row.bus0,row.bus1],popup=name,color='blue').add_to(reinforced_map)    
        
    d1.add_child(overloaded_map)
    d2.add_child(reinforced_map)
    reinforced_map.add_child(linear)
    overloaded_map.add_child(linear2)
    
    f.add_child(d1)
    f.add_child(d2)
    
    return f
        

                                   
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    
                                    