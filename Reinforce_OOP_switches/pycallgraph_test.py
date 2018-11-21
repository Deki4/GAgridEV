'''
Created on 21.11.2018

@author: dcirovic
'''
from dist_grid import Grid

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput



graphviz = GraphvizOutput(output_file='filter_none.png')

with PyCallGraph(output=graphviz):
    grid = Grid(import_name='Test_Grid_switches',custom_line_types = 'lines' )
    grid.line_loading