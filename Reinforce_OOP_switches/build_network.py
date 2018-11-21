'''
Created on 10.07.2018

@author: dcirovic
'''
import pandas as pd

def build_nw(network):
    
    network.add("Bus","MVside",
                v_nom = 20, 
                carrier = "AC",
                x = 7.816728 , y = 48.014038)
    
    network.add("Bus","LVside",
                v_nom = 0.4,
                x = 7.817134 , y = 48.01455,
                carrier = "AC")  #bus0 for dist line purposes
      
   
     
    network.add("Bus","B1",
                v_nom = 0.4, 
                x = 7.817806 , y = 48.015595, 
                carrier = "AC" ) 
    network.add("Bus","B2",
                v_nom = 0.4, 
                x = 7.818446 , y = 48.015167, 
                carrier = "AC" ) 
    network.add("Bus","B3",
                v_nom = 0.4, 
                x = 7.819290, y = 48.015856, 
                carrier = "AC" ) 
    
    
    network.add("Generator", "Grid",
                bus = "MVside",control = "Slack")
    
    network.add("Generator","G1",
                bus = "B1",
                p_set = 0.1)
    
    network.add("Generator", "G2",
                bus = "B2", p_set = 0.1)
    
    
                
    network.add("Transformer","trans1", type="0.4 MVA 20/0.4 kV",     
                bus0="MVside",bus1="LVside")
         
    
    
    network.add("Load", 'load1',
                 bus = "B1",
                 p_set = 0.2)
     
    network.add("Load", 'load2',
                 bus = "B2",
                 p_set = 0.1)
    
    network.add("Load", 'load3',
                 bus = "B3",
                 p_set = 0.1)
    
    
    network.add("Line",'L1',
                type = "NAYY 4x120 SE",
                 bus0 = "LVside", bus1 = "B1",
                #===============================================================
                # x = 0.004, r = 0.01125, s_nom = 0.1677)
                #===============================================================
                length = 0.1)
    
    network.add("Line",'L2',
                type = "NAYY 4x120 SE",
                 bus0 = "LVside", bus1 = "B2",
                 length = 0.2)
    
    network.add("Line", "L3",
                type = "NAYY 4x120 SE",
                bus0 = "B3", bus1 = "B2",
                #===============================================================
                # x = 0.004, r = 0.01125, s_nom = 0.1677)
                #===============================================================
                length = 0.1)
    
    network.add("Link","Lk3", bus0 = "B3", bus1 = "B2", efficiency = 0 )
    
    
    
    network.snapshots = pd.Index(['now'], dtype='object')
    
    
    return network

