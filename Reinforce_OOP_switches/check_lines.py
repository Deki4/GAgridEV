'''
Created on 10.07.2018

@author: dcirovic
'''
import pandas as pd
import numpy as np
from math import sqrt, pi



def line_voltage(network):


    q0 = pd.concat(
        [np.abs(network.lines_t['q0']),
         np.abs(network.transformers_t['q0']),
         np.abs(network.generators_t['q']['Generator_slack'])], axis=1)
    q1 = pd.concat(
        [np.abs(network.lines_t['q1']),
         np.abs(network.transformers_t['q1']),
         np.abs(network.generators_t['q']['Generator_slack'])], axis=1)
    p0 = pd.concat(
        [np.abs(network.lines_t['p0']),
         np.abs(network.transformers_t['p0']),
         np.abs(network.generators_t['p']['Generator_slack'])], axis=1)
    p1 = pd.concat(
        [np.abs(network.lines_t['p1']),
         np.abs(network.transformers_t['p1']),
         np.abs(network.generators_t['p']['Generator_slack'])], axis=1)
     
    s0 = np.hypot(p0, q0)
    s1 = np.hypot(p1, q1)
    
    #from edisgo/tools/pypsa_io - choose p and q from line ending with max(s0,s1)
     
    pfa_p = p0.where(s0 > s1, p1) 
    pfa_q = q0.where(s0 > s1, q1)
     
    lines_bus0 = network.lines['bus0'].to_dict()
    bus0_v_mag_pu = network.buses_t['v_mag_pu'].T.loc[list(lines_bus0.values()), :].copy()
    bus0_v_mag_pu.index = list(lines_bus0.keys())
    
    lines_bus1 = network.lines['bus1'].to_dict()
    bus1_v_mag_pu = network.buses_t['v_mag_pu'].T.loc[list(lines_bus1.values()), :].copy()
    bus1_v_mag_pu.index = list(lines_bus1.keys())
     
    line_voltage_avg = 0.5 * (bus0_v_mag_pu + bus1_v_mag_pu)
            
    for name, row in network.lines.iterrows():
        if not row.type:
            s_nom = row.s_nom
            s = float(s0[name])
            if s > s_nom:
                network.lines.at[name,'overloading'] = round(s/s_nom,5)*100
            elif s_nom > s:
                network.lines.at[name,'overloading'] = None
                
        else:
            i_nom = network.line_types.loc[row.type].i_nom
            s_nom = float(row.v_nom*i_nom)
            network.lines.at[name,'s_nom'] = s_nom
            s = float(s0[name])
            if s > s_nom:
                network.lines.at[name,'overloading'] = round(s/s_nom,5)*100
            elif s_nom > s:
                network.lines.at[name,'overloading'] = None
    if network.lines.overloading.isnull().values.all() or (network.lines.overloading == 0).all():
        return pd.DataFrame()
    else:
        buses_t = network.buses_t['v_mag_pu'].T
        buses_t.columns = ['v_mag_pu']
        return pd.concat([network.lines,network.transformers,buses_t], keys = ('lines','transformers','buses'))
        #network.ovd_grid = network
        #return network.ovd_grid
        #return network.lines.overloading
       
  
    

def calc_s_nom(network):
    
    if len(network.snapshots)>1:
        print('Try for a single snapshot')
    snap = network.snapshots[0]
    network.lines["v_nom"] = network.lines.bus0.map(network.buses.v_nom)
    
    lines_bus0 = network.lines['bus0'].to_dict()
    bus0_v_mag_pu = network.buses_t['v_mag_pu'].T.loc[list(lines_bus0.values()), :].copy()
    bus0_v_mag_pu.index = list(lines_bus0.keys())
    
    lines_bus1 = network.lines['bus1'].to_dict()
    bus1_v_mag_pu = network.buses_t['v_mag_pu'].T.loc[list(lines_bus1.values()), :].copy()
    bus1_v_mag_pu.index = list(lines_bus1.keys())
     
    line_voltage_avg = 0.5 * (bus0_v_mag_pu + bus1_v_mag_pu)
    i_nom = network.line_types.loc[network.lines.type].i_nom.copy()
    i_nom.index = network.lines.index
    
    # Next two rows do the same thing, but the first one doesn't give the pandas warning: 
    # 'SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame'
    network.lines.s_nom.where(network.lines.s_nom > 0, network.lines.v_nom*i_nom,inplace=True)
    #network.lines.s_nom.loc[network.lines.s_nom == 0] = network.lines.v_nom*i_nom*line_voltage_avg[snap]
    network.lines.s_nom.where(network.lines.s_nom.notna(), network.lines.v_nom*i_nom ,inplace=True)
    
    
def loading(network,timestep=0):
    '''
    Returns pd series of line and overloading percentage. Only works if 
    s_nom provided (ie doesn't work for pypsa standard line types, as s_nom 
    defaults to 0) 
    
    '''

    calc_s_nom(network)
    network.lines["v_nom"] = network.lines.bus0.map(network.buses.v_nom)
    if network.lines_t.q0.empty:#no reactive component, only use real power and nominal apparent for loading (DC 16.07.2018)
        loading_c0 = abs((network.lines_t.p0.loc[network.snapshots[timestep]] /
                         (network.lines.s_nom)) * 100)
        loading_c1 = abs((network.lines_t.p1.loc[network.snapshots[timestep]] /
                         (network.lines.s_nom)) * 100)
    
        loading_df = pd.DataFrame(loading_c0)
        loading_df = loading_df.rename(columns={loading_df.columns[0]: "p0"})
        loading_df['p1'] = (loading_c1)
        loading_df['diff'] = loading_df['p0']-loading_df['p1']
        loading_df['max'] = np.maximum(loading_c0, loading_c1)
    
        loading = pd.Series(loading_df.loc[:, 'max'])
    else: #when real and reactive power present use power triangle (DC 16.07.2018)
    
        loading_c0 = ((network.lines_t.p0.loc[network.
                                              snapshots[timestep]] ** 2 +
                      network.lines_t.q0.loc[network.
                                             snapshots[timestep]] ** 2).
                      apply(sqrt) / (network.lines.s_nom)) * 100
        loading_c1 = ((network.lines_t.p1.loc[network.
                                              snapshots[timestep]] ** 2 +
                      network.lines_t.q1.loc[network.
                                             snapshots[timestep]] ** 2).
                      apply(sqrt) / (network.lines.s_nom)) * 100
        
        loading_df = pd.DataFrame(loading_c0)
        loading_df = loading_df.rename(columns={loading_df.columns[0]: "s0"})
        loading_df['s1'] = (loading_c1)
        loading_df['diff'] = loading_df['s0']-loading_df['s1']
        loading_df['max'] = np.maximum(loading_c0, loading_c1)
        
        loading = pd.Series(loading_df.loc[:, 'max'])
        
    del loading_c0
    del loading_c1
    del loading_df
    
    overloaded_lines_i = loading[loading > 100].index.tolist()
    bus_voltage = network.buses_t.v_mag_pu.T
    bus_voltage = bus_voltage[network.snapshots[timestep]]
    overloaded_lines = pd.DataFrame(loading[loading > 100])
    overloaded_lines.rename(columns={0: "loading"})
    voltage_level = network.lines.loc[overloaded_lines_i].v_nom
    overloaded_lines['v_nom'] = voltage_level
    length = network.lines.loc[overloaded_lines_i].length
    overloaded_lines['length'] = length
    
    return loading
            
            
def detect_overloading(network):
    load = loading(network)            
    if (load>100).any():
        return load
    elif (load<100).all():
        return pd.Series()
    
def format_custom_lines(grid):    
    """ 
    Format the DataFrame to match PyPSA's standard line types in standard_types.line_types.csv.
    
    Returns
    -------
    pandas.DataFrame
    """
    df = grid.custom_lines
    df['f_nom'] = 50
    df['mounting'] = np.select([df['comment'].str.contains('overhead'),df['comment'].str.contains('cable')],['overhead','cable'],'unknown')
#        df.drop(columns=['comment'],inplace=True)
    df['reference'] = 'custom'
    df.rename(columns={'type':'name'},inplace=True)
    df.set_index(['name'],inplace=True)
    df['X'] = 2*pi*df['f_nom']*df['L'] / 1000
    cols = ['f_nom','R','X','C','max_I','mounting','size','reference']
    df = df[cols]
    df.columns =  grid.components['LineType']["standard_types"].columns
    
    
    return df
        
   
   
 