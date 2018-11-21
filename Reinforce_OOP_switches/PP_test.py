# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 09:04:00 2018

@author: dcirovic
"""

import pandapower as pp
import pandapower.plotting as plot
from pandapower.plotting.plotly import simple_plotly

net = pp.create_empty_network()

MVside = pp.create_bus(net, vn_kv = 20, name = 'MVside',geodata=(7.82,48.01) )
LVside = pp.create_bus(net, vn_kv = 0.4, name = 'LVside', geodata = (7.819184,48.008429))
MVside1 = pp.create_bus(net, vn_kv = 20, name = 'MVside1', geodata = (7.837,48.0225))
LVside1 = pp.create_bus(net, vn_kv = 0.4, name = 'LVside1', geodata = (7.835,48.025))
LV = pp.create_bus(net, vn_kv = 0.4, name = 'LV', geodata = (7.816363,48.010059))

pp.create_ext_grid(net, bus = MVside, vm_pu=1, name = "grid connection")


pp.create_load(net, bus = LV, p_kw = 300, name = "home load") 

trans1 = pp.create_transformer(net, hv_bus = MVside , lv_bus = LVside, std_type = "0.4 MVA 20/0.4 kV",
                              name = "trans1")
trans2 = pp.create_transformer(net, hv_bus = MVside1 , lv_bus = LVside1, std_type = "0.4 MVA 20/0.4 kV",
                              name = "trans2")


pp.create_line(net, from_bus=LVside, to_bus=LV, length_km=0.1, name="dist_line",
               std_type="NAYY 4x120 SE")
pp.create_line(net, from_bus=LVside1, to_bus=LV, length_km=0.4, name="dist_line1",
               std_type="NAYY 4x120 SE")


pp.create_sgen(net,MVside1, p_kw = -100, name = "Gas" )
pp.create_sgen(net,LV, p_kw = -100, name = "PV" )

