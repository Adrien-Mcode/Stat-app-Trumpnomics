# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 22:51:14 2021

@author: SURFACE
"""

#Mise au propre du code de test controle synth : 
    
#------------ Importation des modules et fixation de l'aléatoire ---------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cvxpy as cvx
from scipy.optimize import differential_evolution, LinearConstraint
#from sklearn.model_selection import train_test_split
from math import sqrt
from random import seed

seed(3)

#------------ Importation des données et traitement de celles-ci ---------------

pays_ocde = {"Germany" :'DEU',"Australia" :'AUS',"Austria":'AUT',"Belgium":'BEL',"Canada":'CAN',"Denmark":'DNK',"Spain":'ESP',
             "Finland":'FIN',"France":'FRA',"Hungary":'HUN',"Ireland":'IRL', "Iceland": 'ISL', "Italy":'ITA', 'Korea': 'KOR',
             "Japan":'JPN',"Luxembourg":'LUX',"Norway":'NOR',"New-Zealand":'NZL',"Netherlands":'NLD',"Portugal":'PRT',
             "United Kingdom":'GBR',"Sweden":'SWE',"Switzerland":'CHE',"Slovak Republic":'SVK',"United-States":'USA'}

variables = ['Actifs','Emplois','PIB']


#On importe les données
data = pd.read_csv(r'df_countries.csv', header=[0,1])       #On importe les données de la table df_countries
data.drop(list(d for d in range(0, 20)), inplace=True)      #On supprime les lignes après 1995
data = data.reset_index().set_index('Pays')                               #On met en index "Pays" qui est en fait la date au format str


#On trie les données pour améliorer les performances et éviter les warnings:
data = data.sort_index(axis=1)


#On construit le df qui va nous contenir les séries temporelles pour le contrôle synthétique :  
df_ct = pd.DataFrame()
for i in variables :
    interm = data.xs(str(i), axis=1, level=1, drop_level=True)      #On prend uniquement les colonnes qui se rapporte à une variable avec .xs
    interm['Variables'] = str(i)                                   #On rajoute une colonne "variables" qui nous servira plus tard pour construire le problème d'optimisation
    df_ct = pd.concat([df_ct, interm], axis=0)                      #On concatène le df ainsi créé avec les autres


df_ct = df_ct.dropna()


# Nous créons aussi un df pour calculer les moyennes agrégées requises
data_mean = data.copy()

for pays in pays_ocde.keys() :
    data_mean[pays] = data_mean[pays].assign(Conso=lambda x: x.Conso / x.PIB)
    data_mean[pays] = data_mean[pays].assign(Emplois=lambda x: np.log(x.PIB/x.Emplois) - np.log(x.PIB.shift()/x.Emplois.shift()))
    data_mean=data_mean.drop([(pays,'PIB'),(pays,'Actifs')], axis=1)

data_mean.rename(columns={'Conso': 'Conso_share'}, inplace=True)
data_mean.rename(columns={'Emplois': 'Prod_growth'}, inplace=True)


#On le met ensuite sous la forme désirée pour le contrôle synthétique :
df_ct_mean = pd.DataFrame()
for i in ['Chomage', 'Conso_share', 'Prod_growth','Exports', 'Formation']:
    interm = data_mean.xs(str(i), axis=1, level=1, drop_level=True)         #On prend uniquement les colonnes qui se rapporte à une variable avec .xs
    interm['Variables'] = str(i)                                            #on rajoute une colonne "variables" qui nous servira plus tard pour construire le problème d'optimisation
    df_ct_mean = pd.concat([df_ct_mean, interm], axis=0)


# On mesure le PIB,les actifs et les emplois en déviation par rapport à l'année 1995
for var in ['PIB', 'Actifs', 'Emplois']:    
    for pays in df_ct.drop('Variables', 1).columns:    
        df_ct[df_ct["Variables"]==var] = df_ct[df_ct["Variables"]==var].assign(**{pays: lambda x: (x[pays] - x[pays].iloc[0]) / x[pays].iloc[0]})


#Les auteurs précisent qu'ils prennent comme critère de validation la qualité de la modélisation sur le taux de chomage.
#On créé donc un df contenant tous les taux de chomage
df_chomage = data.xs('Chomage',axis = 1,level = 1,drop_level = True).drop(list(data.reset_index().loc[d,'Pays'][0] for d in range(88,99)))

#Note : on a une problème de valeurs manquantes sur ce df, pour l'instant on utilise donc 
#la fonction df.fillna() qui les remplacent par des 0, mais il faudra voir pour à terme 
#faire autre chose avec : 
df_chomage = df_chomage.fillna(0) 
   
#------------ Partie Modélisation ----------------------------------------------

np.set_printoptions(suppress=True) # afin de rendre les sorties plus lisibles, on supprime les notations exponentielles.

#On créé le problème d'optimisation cvxpy :

#On prépare le vecteur qui contient les valeurs qui nous intéressent pour les USA : 
X1 = df_ct[['United-States', 'Variables']]
X1 = X1.drop(list(data.reset_index().loc[d,'Pays'][0] for d in range(88,99)))
X1_mean = df_ct_mean[['United-States', 'Variables']].groupby('Variables').mean().reset_index()
X1 = pd.concat([X1, X1_mean]).reset_index().drop(['index', 'Variables'], 1)
X_interm = X1
X1 = X1.values

# Notons que X1 n'a aucune valeur manquante, il va falloir en retirer pour
# correspondre à X0 qui, lui, en aura

# On prépare le vecteur qui contient les valeurs qui nous intéressent pour les autres pays :

X0 = df_ct.drop('United-States', 1)
X0 = X0.drop(list(data.reset_index().loc[d,'Pays'][0] for d in range(88,99)))
X0_mean = df_ct_mean.drop('United-States', 1).groupby('Variables').mean().reset_index()
X0 = pd.concat([X0, X0_mean]).reset_index().drop(['index', 'Variables'], 1)
X0 = X0.values


# On construit le problème cvxpy

V_opt = cvx.Parameter((154,154),PSD = True)                 #On définit V qui est un vecteur de paramètre
x = cvx.Variable((24,1),nonneg=True)                        #On définit un vecteur de variables cvxpy
cost = cvx.quad_form(X1 - X0@x,V_opt)                       #On définit la fonction de cout : norme des résidus
constraints = [cvx.sum(x)==1]                               #La contrainte
prob = cvx.Problem(cvx.Minimize(cost), constraints)         #On définit le problème
 
#On définit une fonction qui renvoit le "cout" pour l'optimisation de la fonction V :
def loss_V(V) :
    V_opt.value = np.diag(abs(V))
    prob.solve()
    return(((df_chomage['United-States'].values - df_chomage.drop('United-States',axis = 1).values @ x.value).T@(df_chomage['United-States'].values - df_chomage.drop('United-States',axis = 1).values @ x.value))[0,0])
   
#On définit et résout le problème d'optimisation en V : 

contrainte = LinearConstraint(np.ones((1,154)), 1, 1)
bounds = [(0,1) for i in range(154)]
result = differential_evolution(loss_V,bounds,maxiter=100,constraints=contrainte)
        
V = np.diag(result.x)
W = x.value
RMSPE = sqrt((X1 - X0@W).T@V@(X1 - X0@W))

#------------ Affichage des Résultats ------------------------------------------

# Voici la table des coefficients attribués à chaque pays
pd.set_option('display.float_format', lambda x: '%.3f' % x)     #Afin de désactiver les notations exponentielles

#Affichage de la table des coefficients : 
country_list = df_ct.dropna().drop(['United-States', 'Variables'], axis=1)
coeff = pd.DataFrame(x.value, index=country_list.columns)
print(coeff)


# Commençons par visualiser l'écart de tendance en PIB

df_pib = df_ct[df_ct["Variables"]=="PIB"]
#df_pib = df_pib.reset_index().drop('index', 1)

sc = df_pib.drop(['Variables','United-States'],axis = 1)@ W

plt.plot(df_pib['United-States'].values)
plt.plot(sc.values)
plt.vlines(84, 0, 1, linestyle = '--', color = 'red', label = 'Election de Trump')
plt.legend()
plt.show()
plt.close()

#On peut visualiser l'écart en terme de taux de chômage : 

plt.plot(df_chomage['United-States'].values)
plt.plot(df_chomage.drop('United-States',axis = 1).values@W)
plt.legend()
plt.show()
plt.close()

