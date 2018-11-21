'''
Created on 30.07.2018

@author: dcirovic
'''

import pypsa
import copy
from pypsa.descriptors import Dict
import numpy as np
import pandas as pd
import os
import sys
import math
import networkx as nx


from map_grid import draw_traces
from check_lines import detect_overloading, loading, format_custom_lines
from apply_reinforcement import apply_parallel_reinforcement, bypass_line
from Plot import plot_grid
from cost import Added_lines
from plotly.offline.offline import plot




override_components = pypsa.components.components.copy()
override_components.loc["Switch"] = ["switches","ideal switch",np.nan]

override_component_attrs = Dict({k : v.copy() for k,v in pypsa.components.component_attrs.items()})
override_component_attrs["Switch"] = pd.DataFrame(columns = ["type","unit","default","description","status"])
override_component_attrs["Switch"].loc["name"] = ["string","n/a","n/a","Unique name","Input (required)"]

override_component_attrs["Switch"].loc["bus0"] = ["string","n/a","n/a","Name of first bus on which switch is between","Input (required)"]
override_component_attrs["Switch"].loc["bus1"] = ["string","n/a","n/a","Name of second bus on which switch is between","Input (required)"]

override_component_attrs["Switch"].loc["status"] = ["string","n/a","closed","'open' or 'closed'","Input (required)"]



class Grid(pypsa.components.Network):  
    """ Grid class inherited from PYPSA network.
    
    Attributes
    ----------
    overloaded_grid: :class:`~dist_grid.Grid` 
        Deepcopy of the grid instance when it is overloaded. Contains all the 
        same attributes as a pypsa network. To be used for comparison with the
        reinforced grid.
        
    overloaded_lines: :obj:`list` of :obj:`str`
        List of overloaded line names. See `overloaded_lines` for more information
        
    os_lines: :pandas:`pandas.DataFrame<dataframe>`
        DataFrame containing out of service pypsa.Network().lines objects
        
    
    """
            
    def __init__(self, custom_line_types=None,ignore_standard_types=False, *args,**kwargs):
        """Extend __init__ of pypsa.Network.Run lpf and pf when instantiating 
        to determine any initial overloading.
        """
        self.custom_lines = None
        #initialize os_lines with init_switches method
        self.os_lines = pd.DataFrame() 
        dirpath = os.getcwd()
        kwargs["override_components"]=override_components
        kwargs["override_component_attrs"]=override_component_attrs
        

     
        super().__init__(*args,**kwargs)
        
        #Perform switch initiation to determine network topology. Remove any lines with open switches. 
        #Updates os_lines. See init_switches.
        self.init_switches()
        
        #Extend PyPSA's standard line types
        if custom_line_types is not None:
            self.custom_lines =  pd.read_csv(os.path.join(dirpath,str(custom_line_types)+'.csv'),sep=',', delimiter=',',usecols=['type','R','L','C','max_I','comment','size'])
            self.custom_lines = self.format_custom_lines()
            self.components['LineType']["standard_types"] = self.components['LineType']["standard_types"].append(self.custom_lines)
            self.line_types = self.line_types.append(self.custom_lines)
        
        self.lpf()
        self.pf(use_seed = True)
        self.overloaded_grid = None 
        if not detect_overloading(self).empty:
            self.overloaded_grid = copy.deepcopy(self)
               
    
    def format_custom_lines(self):
 
        df = format_custom_lines(self)
        return df
        
        
            
    @property        
    def line_loading(self):
        """Pandas series of all lines and the loading percentage
        
        Returns
        -------
        :pandas:`pandas.Series<series>` 
        line loading percentage index by line name/id

        """
        self = loading(self)
        return self
    
    @property
    def overloaded_lines(self):
        """ List of overloaded line names
        
        Returns
        -------
        :obj:`list`
            Overloaded line names(IDs)
            
        """
        
        if not detect_overloading(self).empty:
            self = detect_overloading(self)
            return self.index.tolist()
        else:
            self  = None
            return self
     

        
    def reinforce(self):
        """ Adds a parallel line of the same type to the overloaded line.
        Returns a new Grid object
        
        Returns
        -------
        :class:`~dist_grid.Grid` 
        """
        #ToDo can potentially remove this as PFA running on __init__
        if self.lines_t.p0.empty:
            print('Run PFA before applying reinforcement')
        else:
            return apply_parallel_reinforcement(self,self.overloaded_lines)
        
    def bypass_line(self): 
        bypass_line(self)   
        

    def plot(self):
        """Plot an interactive map using Folium. Plots the overloaded grid and
        the reinforced grid side by side.
        """
        fig = plot_grid(self.overloaded_grid,self)
        fig.save('grid_comparison2.html')
    
    def plotly_on_map(self,name='plotly_map'):
        """Plot an interactive map using Plotly. Plots the overloaded grid and
        the reinforced grid side by side. HTML file saved locally. 
        """
        
        fig = draw_traces(self.overloaded_grid,self)
        
        return plot(fig, filename=name+'.html')
        
        
        
    @property
    def added_lines(self):
        return Added_lines(self.overloaded_grid,self).index.tolist()
        
    def switching(self):
        """ 
        Applies switching logic to the Grid object. Lines with open switches 
        are deleted from the Grid.lines DataFrame. Check for looping and 
        isolated nodes using Networkx library.
        """
       # if self.os_lines != open switches lines then something has been changed
        
        
        lines_w_open_switches = []
        lines_w_closed_switches = []

        open_switches = self.switches[self.switches.status=='open']
        closed_switches = self.switches[self.switches.status=='closed']
        
        lines = self.lines.append(self.os_lines)
        
        #find the line names to which the open switches correspond
        for name, row in open_switches.iterrows():
            bus0 = row.bus0
            bus1 = row.bus1
            lines_w_open_switches.append(lines[((lines.bus0 == bus0) & (lines.bus1 == bus1))|
                    ((lines.bus0 == bus1) & (lines.bus1 == bus0))].index.item())
        #find the line names to which the closed switches correspond
        for name, row in closed_switches.iterrows():
            bus0 = row.bus0
            bus1 = row.bus1
            lines_w_closed_switches.append(lines[((lines.bus0 == bus0) & (lines.bus1 == bus1))|
                    ((lines.bus0 == bus1) & (lines.bus1 == bus0))].index.item())
        #updated out of service lines if they have an open switch present
        for line in lines_w_open_switches:
            if line not in self.os_lines.index:
                self.os_lines = self.os_lines.append(lines.loc[line])
                self.lines = self.lines.drop(line)
        #update in service lines (grid.lines) with lines where switches are closed        
        for line in lines_w_closed_switches:
            if line not in self.lines.index:
                self.lines = self.lines.append(lines.loc[line])
                self.os_lines = self.os_lines.drop(line)
                
                
        slack = self.buses[self.buses.control=='Slack'].index.item()
        
        #Bus(node) is isoloated if there is no path from the slack bus.
        #Delete isolated buses(nodes).
        g = self.graph()
        for node in g.nodes():
            try:
                nx.shortest_path(g,slack, node)
            except nx.NetworkXNoPath:
                self.remove('Bus',node)
        
        try: 
            if nx.find_cycle(g):
                raise Exception('Loops present in the Network')
                print('loop present in the network')
        except nx.NetworkXNoCycle:    
            pass
            
            
        #Perform power flow after switching operations.
        self.lpf()
        self.pf(use_seed=True)

    
    def init_switches(self):
        """ 
        Applies switching logic to the initial Grid object. 
        Lines with open switches are deleted from the Grid.lines DataFrame. 
        Update the os_lines attribute. 
        Check for looping and isolated nodes using Networkx library.
        """
        
        lines_w_open_switches = []

        open_switches = self.switches[self.switches.status=='open']
        lines = self.lines
        
        #Line names(IDs) associated with open switches.
        for name, row in open_switches.iterrows():
            bus0 = row.bus0
            bus1 = row.bus1
            lines_w_open_switches.append(lines[((lines.bus0 == bus0) & (lines.bus1 == bus1))|
                    ((lines.bus0 == bus1) & (lines.bus1 == bus0))].index.item())
        #    
        for line in lines_w_open_switches:
            self.os_lines = self.os_lines.append(self.lines.loc[line])
            self.remove("Line",line)            
         
        slack = self.buses[self.buses.control=='Slack'].index.item()
        
        
        g_copy = self.graph()
        for node in g_copy.nodes():
            try:
                nx.shortest_path(g_copy,slack, node)
            except nx.NetworkXNoPath:
                self.remove('Bus',node)
        
        try: 
            if nx.find_cycle(g_copy):
                raise Exception('Loops present in the Network')
                print('loop present in the network')
        except nx.NetworkXNoCycle:    
            pass
        

        
        
        
grid = Grid(import_name='Test_Grid_switches',custom_line_types = 'lines' )
g = grid.graph()


