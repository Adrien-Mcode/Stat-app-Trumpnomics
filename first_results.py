# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 09:13:25 2021

Preprocessing pour adapter la table (sans inégalités) au module
Premiers résultats 

@author: Jérémie Stym-Popper
"""

import pandas as pd
from SyntheticControlMethods import Synth


data = pd.read_csv('https://raw.githubusercontent.com/OscarEngelbrektson/SyntheticControlMethods/master/examples/datasets/german_reunification.csv')
data = data.drop(columns="code", axis=1)

ocde_df = pd.read_csv(r"Tableaux_csv\ocde2.csv")
ocde_df.rename(columns={'Unnamed: 0':'Variables'}, inplace=True)


pd.options.mode.chained_assignment = None  # default='warn'
liste_table = []
for pays in ocde_df['Pays'].unique():
    pays_table = ocde_df.iloc[:7]
    liste_table.append(pays_table)
    ocde_df.drop(pays_table.index, inplace=True)

liste2 = []
for table in liste_table:
    keep_pays = table["Pays"].values[1]
    table.drop("Pays", axis=1, inplace=True)
    table2 = table.T.copy()
    table2.columns = table2.loc['Variables'].values 
    table2.drop('Variables', inplace=True)  
    table2.reset_index(inplace=True)
    table2.rename(columns={'index':'years'}, inplace=True)
    table2['Pays'] = pd.DataFrame([keep_pays]*120, columns=['Pays'])
    liste2.append(table2)
    
table_finale = pd.concat([table for table in liste2], ignore_index=True)
table_finale['years'] = pd.to_datetime(table_finale['years'])
table_finale = table_finale.convert_dtypes()



#Fit classic Synthetic Control
fit1 = Synth(table_finale, "PIB", "Pays", "years", table_finale['years'][106], "USA", pen=0)

# Ne fonctionne pas. Faîtes le test avec data (les données allemandes)
# Visualisez les données allemandes pour comprendre la table qu'il faut mettre

#Visualize synthetic control
fit1.plot(["original", "pointwise", "cumulative"], treated_label="États-Unis", 
            synth_label="Synthetic USA", treatment_label="Élection de Trump")
