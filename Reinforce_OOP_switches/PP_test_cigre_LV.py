# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 13:00:49 2018

@author: dcirovic
"""

import pandapower as pp
import pandapower.networks as pn
from pandapower.networks import mv_oberrhein

import pandapower.plotting as plot
from pandapower.plotting.plotly import simple_plotly

net = mv_oberrhein()

simple_plotly(net, on_map=True, projection='epsg:31467')
#net = pn.create_cigre_network_lv()

