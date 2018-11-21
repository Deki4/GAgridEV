'''
Created on 07.08.2018

@author: dcirovic
'''


import pandas as pd

def Added_lines(overloaded_grid,reinforced_grid):
    new_lines = pd.concat([overloaded_grid.lines,reinforced_grid.lines]).drop_duplicates(keep=False)
    return new_lines