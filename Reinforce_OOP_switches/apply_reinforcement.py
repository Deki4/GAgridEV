'''
Created on 31.07.2018

@author: dcirovic
'''

import pandas as pd
from check_lines import detect_overloading, loading

import random
import networkx as nx




def apply_parallel_reinforcement(grid,overloaded_lines):
    """
    Add the same line type parallel to original overloaded line between
    same buses.
    """
    
    #ToDo: this is probably something that should eventually go under logging
    if (detect_overloading(grid)<100).all():
        print(' No overloaded lines to reinforce')

    elif overloaded_lines:    
        for line in overloaded_lines:
            bus0 = grid.lines.loc[line]['bus0']
            bus1 = grid.lines.loc[line]['bus1']
            #add a standard line type from standard library
            if grid.lines.loc[line]['type']:
                grid.add("Line", name = grid.lines.loc[line].name + '*' ,
                            type = grid.lines.loc[line]['type'], 
                            bus0 = bus0, bus1 = bus1,
                            length = grid.lines.loc[line].length)
                  
            #ToDo: maybe have **kwargs included in the add method because then can add other params as well        
            if not grid.lines.loc[line]['type']:
                grid.add("Line", name = grid.lines.loc[line].name + '*' ,
                            bus0 = bus0, bus1 = bus1,
                            x = grid.lines.loc[line].x, r = grid.lines.loc[line].r,
                            s_nom = grid.lines.loc[line].s_nom )    
            print('reinforce the following lines....' + line)
        grid.lpf()
        grid.pf(use_seed=True) 
        grid.rein = grid   
        return grid

def apply_new_line(grid,overloaded_lines):
    """
    Add the next largest line from standard line types. Only reinforce lines 
    between trafo and buses where overvoltage/overload occurs.
    """
    #ToDo: this is probably something that should eventually go under logging
    if (detect_overloading(grid)<100).all():
        print(' No overloaded lines to reinforce')
        
        
    elif overloaded_lines:
        for line in overloaded_lines:
            line_type = grid.lines.loc[line].type
            size = grid.line_types.loc[line_type].cross_section
            
            
            
            
            
            
def bypass_line(grid):
    
    #ToDo: Add functionality to avoid bypassing the same line if another bypass is required/chosen
    bus_names = grid.buses.index.tolist()
    rand_bus = random.choice(bus_names)
    
    #choose a random bus to which to bypass to, but can't be the transformer
    if rand_bus in grid.transformers.bus0.item() or rand_bus in grid.transformers.bus1.item():
        bus_names.remove(rand_bus)
        rand_bus = random.choice(bus_names)
    
    start_bus = grid.transformers.bus1.item() #must be trafo LV side
    end_bus = grid.buses.loc[rand_bus].copy()
    end_bus_name = end_bus.name

    end_bus.name = rand_bus+'copy'
    grid.buses = grid.buses.append(end_bus)
   
    
    def bypass_length(grid,start_bus,end_bus_name):
        total_length = []
        bypass_path = nx.shortest_path(grid.graph(),start_bus,end_bus_name)
        num_lines_bypassed = len(bypass_path)-1
        i = 0 
        while i < num_lines_bypassed:
            total_length.append(grid.lines[((grid.lines.bus0 == bypass_path[i]) & (grid.lines.bus1 == bypass_path[i+1]))|
                    ((grid.lines.bus0 == bypass_path[i+1]) & (grid.lines.bus1 == bypass_path[i]))].length.item())
            i+=1
        return sum(total_length)
        
        
    grid.add('Line', 'bypass', type = 'NAYY 4x120 SE',bus0 = start_bus, bus1 = end_bus.name,length=bypass_length(grid,start_bus,end_bus_name))
    
    grid.lpf()
    grid.pf(use_seed=True)


    
       
    
    
    
    
    
    
    
                
            
            
            