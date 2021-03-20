# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 17:57:04 2021

@author: SURFACE
"""
import pandas as pd

df = pd.read_csv('ocde_df.csv',header = [0,1])

pays_ocde = {"Germany" :'DEU',"Australia" :'AUS',"Austria":'AUT',"Belgium":'BEL',"Canada":'CAN',"Denmark":'DNK',"Spain":'ESP',"Finland":'FIN',"France":'FRA',"Greece":'GRC',"Ireland":'IRL',"Italy":'ITA',
             "Japan":'JPN',"Luxembourg":'LUX',"Norway":'NOR',"New-Zealand":'NZL',"Netherlands":'NLD',"Portugal":'PRT',"United Kingdom":'GBR',"Sweden":'SWE',"Switzerland":'CHE',"Turkey":'TUR',"United-States":'USA'}

'''
INPUT VARIABLES:
        
dataset: the dataset for the synthetic control procedure.
Should have the the following column structure:
ID, Time, outcome_var, x0, x1,..., xn
Each row in dataset represents one observation.
The dataset should be sorted on ID then Time. 
That is, all observations for one unit in order of Time, 
followed by all observations by the next unit also sorted on time
        
ID: a string containing a unique identifier for the unit associated with the observation.
E.g. in the simulated datasets provided, the ID of the treated unit is "A".
        
Time: an integer indicating the time period to which the observation corresponds.
        
treated_unit: ID of the treated unit
'''
df_ct = pd.DataFrame()
for i in pays_ocde.keys() :
    interm = df[['Pays',i]].drop([(i,'income p0p50'),(i,'income p90p100')],
                                 axis = 1).sort_values(('Pays','Variables'))
    interm.columns = interm.columns.droplevel()
    interm = interm.drop(0,axis = 0)
    interm['Variables'] = interm['Variables'].apply(lambda x:float(x[:4]) + float(x[5:7])*0.01)
    interm['ID'] = str(i)
    df_ct = pd.concat([df_ct,interm],axis = 0)
    
df_ct = df_ct[['ID','Variables','PIB','Actifs', 'Chomage', 'Conso', 'Emplois', 'Exports',
       'Formation']]
df_ct.sort_values('ID',inplace = True,kind = 'mergesort')
df_ct = df_ct.reset_index().drop('index',axis = 1)
df_ct.to_csv('df_scm.csv')


    