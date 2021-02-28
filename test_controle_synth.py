# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 19:24:07 2021

@author: SURFACE

essai d'optimisation avec scipy
"""

import pandas as pd
import numpy as np
import cvxpy as cvx


pays_ocde = {"Germany" :'DEU',"Australia" :'AUS',"Austria":'AUT',"Belgium":'BEL',"Canada":'CAN',"Denmark":'DNK',"Spain":'ESP',"Finland":'FIN',"France":'FRA',"Greece":'GRC',"Ireland":'IRL',"Italy":'ITA',
             "Japan":'JPN',"Luxembourg":'LUX',"Norway":'NOR',"New-Zealand":'NZL',"Netherlands":'NLD',"Portugal":'PRT',"United Kingdom":'GBR',"Sweden":'SWE',"Switzerland":'CHE',"Turkey":'TUR',"United-States":'USA'}

variables = ['Actifs', 'Chomage', 'Conso', 'Emplois', 'Exports', 'Formation', 'PIB']

#Note pour prendre le second niveau d'un multiindex : 
#df_cs.xs('PIB', axis=1, level=1, drop_level=False)

#On importe les données
data = pd.read_csv(r'ocde_df.csv',header = [0,1])

#On supprime les inégalités qui ne nous intéressent pas pour l'instant.
for i in pays_ocde.keys() :
    data= data.drop([(i,'income p0p50'),(i,'income p90p100')],
                                 axis = 1)

#On trie les données pour améliorer les performances et éviter les warnings:
data = data.sort_index(axis = 1)
  
#on créé le dataframe qui nous intéresse qui est de la forme : pays en colonnes, 
#année + variable en ligne (une ligne est donc la valeur d'une variable, pour une 
#année donnée dans chaque pays)
df_ct = pd.DataFrame()
for i in variables :
    interm = data.xs(str(i),axis = 1,level = 1,drop_level = True)   #On prend uniquement les colonnes qui se rapporte à une variable avec .xs
    interm = interm.drop(0,axis = 0)                                #On enlève la ligne d'indice 0 qui est vide (seulement des nan)
    interm['Variables'] = str(i)                                    #on rajoute une colonne "variables" qui nous servira plus tard pour construire le problème d'optimisation
    df_ct = pd.concat([df_ct,interm],axis = 0)                      #On concatène le df ainsi créé avec les autres

#On créé les matrices pour la formulation du problème :
   
X1 = df_ct.dropna()[['United-States','Variables']]          #On créé le vecteur que l'on veut approcher X1
X1 = X1.drop(list(d for d in range (109,121)))              #On supprimme les lignes avec des indices entre 109 et 121 (qui correspondent aux années après 2016)
X1 = X1[X1.Variables != 'PIB'].drop('Variables',axis = 1)   #On ne garde que les variables et pas le PIB
X1 = X1.to_numpy()                                          #On passe en tableau Numpy

#On réitère le même processus mais cette fois avec le reste des pays

X0 = df_ct.dropna().drop('United-States',axis = 1)
X0 = X0.drop(list(d for d in range (109,121)))
X0 = X0[X0.Variables != 'PIB'].drop('Variables',axis = 1)
X0 = X0.to_numpy()


# On construit et on "résout" le problème cvxpy
x = cvx.Variable((22,1),nonneg=True)                #On définit un vecteur de variables cvxpy
cost = cvx.norm(X1 - X0@x, p=2)                     #on définit la fonction de cout : norme des résidus
constraints = [cvx.sum(x) == 1]                     #La contrainte
prob = cvx.Problem(cvx.Minimize(cost),constraints)  #On définit le problème
prob.solve()                                        #On le résout

#https://stackoverflow.com/questions/65526377/cvxpy-returns-infeasible-inaccurate-on-quadratic-programming-optimization-proble 
#explication de pourquoi avec sum_square ça ne fonctionnait pas

#Print result.
print("\nThe optimal value is", prob.value)
print("The optimal x is")
print(x.value)
print("The norm of the residual is ", cvx.norm(X0 @ x - X1, p=2).value)


