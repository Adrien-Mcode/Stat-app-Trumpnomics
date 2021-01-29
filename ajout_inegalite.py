# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 20:00:17 2021

@author: SURFACE
"""
import pandas as pd


pays_ocde = {"Germany" :'DEU',"Australia" :'AUS',"Austria":'AUT',"Belgium":'BEL',
             "Canada":'CAN',"Denmark":'DNK',"Spain":'ESP',"Finland":'FIN',
             "France":'FRA',"Greece":'GRC',"Ireland":'IRL',"Italy":'ITA',
             "Japan":'JPN',"Luxembourg":'LUX',"Norway":'NOR',"New-Zealand":'NZL',
             "Netherlands":'NLD',"Portugal":'PRT',"United Kingdom":'GBR',
             "Sweden":'SWE',"Switzerland":'CHE',"Turkey":'TUR',"United-States":'USA'}

bottom_50 = pd.read_csv('Donnees inegalite/top_bottom_income/WID_Data_Metadata/bottom_50_income.csv',
                        header = 1,
                        sep = ';',
                        engine = "python")

top_10 =pd.read_csv('Donnees inegalite/top_bottom_income/WID_Data_Metadata/top_10_income.csv',
                        header = 1,
                        sep = ';',
                        engine = "python")

df_ocde = pd.read_csv('ocde_df')

df_ocde.rename(columns={'Unnamed: 0':'Variables'}, inplace=True)

ind_tuple = list(zip(df_ocde['Pays'], df_ocde['Variables']))
new_index = pd.MultiIndex.from_tuples(ind_tuple, names=["Pays", "Variables"])
#mise en place du système de double indice
tocde = df_ocde.T.copy()
tocde.columns=new_index
tocde.drop(['Variables', 'Pays'],inplace=True)
tocde = tocde.drop(['2020-Q1','2020-Q2','2020-Q3','2020-Q4','2021-Q1'])
#renommage des colonnes de bottom_50 et top_10
bottom_50.columns = ['Variables','Year'] + sorted(pays_ocde.keys(), key = str)
top_10.columns = ['Variables','Year'] + sorted(pays_ocde.keys(), key = str)

#on prépare bottom_50 pour la fusion
bottom_50 = bottom_50.drop('Variables', axis = 1)
for i in range (1,3) : 

    bottom_50 = pd.concat([bottom_50,bottom_50])    
annee = []
for j in range (1,5):
    for i in range (0,29):
        annee.append(str(1991+i)+'-Q'+str(j))
bottom_50['Year'] = annee

#Mise en place double index pour bottom_50 :
bottom_50 = bottom_50.set_index('Year')

bottom_50['Variables'] = 'income p0p50'

ind_tuple = list(zip(bottom_50.columns, bottom_50['Variables']))

new_index = pd.MultiIndex.from_tuples(ind_tuple, names=["Pays", "Variables"])

bottom_50.columns = new_index

bottom_50 = bottom_50.drop(('Variables','income p0p50'), axis = 1)

tocde = tocde.merge(right = bottom_50,
                    how = 'outer',
                    left_index = True,
                    right_index = True).sort_index(axis = 0).sort_index(axis = 1)

#on prépare top_10 pour la fusion :
top_10 = top_10.drop('Variables', axis = 1)
for i in range (1,3) : 

    top_10 = pd.concat([top_10,top_10])    
annee = []
for j in range (1,5):
    for i in range (0,29):
        annee.append(str(1991+i)+'-Q'+str(j))
top_10['Year'] = annee

#Mise en place double index pour top_10 :
top_10 = top_10.set_index('Year')

top_10['Variables'] = 'income p90p100'

ind_tuple = list(zip(top_10.columns, top_10['Variables']))

new_index = pd.MultiIndex.from_tuples(ind_tuple, names=["Pays", "Variables"])

top_10.columns = new_index

top_10 = top_10.drop(('Variables','income p90p100'), axis = 1)

tocde = tocde.merge(right = top_10,
                    how = 'outer',
                    left_index = True,
                    right_index = True).sort_index(axis = 0).sort_index(axis = 1)
