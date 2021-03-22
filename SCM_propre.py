# -*- coding: utf-8 -*-
"""
Created on Sat Mar 20 17:45:52 2021

Sauvegarde du contrôle synthétique propre

@author: Jérémie Stym-Popper
"""

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
from random import seed
# from time import clock

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

#Ajout des données sur le chômage plus complète 

df_cho = pd.read_csv(r'donnee_chomage_Ad.csv')
df_cho = df_cho[(df_cho['LOCATION'].isin(pays_ocde.values())) & 
                (df_cho['VARIABLE']=='UNR')].set_index(['LOCATION','Time'])

df_cho = df_cho.drop(['Country',
                      'VARIABLE',
                      'Variable',
                      'FREQUENCY',
                      'Frequency',
                      'TIME',
                      'Unit Code',
                      'Unit',
                      'PowerCode Code',
                      'PowerCode',
                      'Reference Period Code',
                      'Reference Period',
                      'Flag Codes',
                      'Flags'],axis = 1)

df_chomage =pd.DataFrame()
for i in sorted(pays_ocde.keys()) :
    print(i)
    interm = df_cho.loc[pays_ocde[i]]
    interm.columns = [i]
    df_chomage = pd.concat([df_chomage, interm], axis=1) 


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

'''
#Les auteurs précisent qu'ils prennent comme critère de validation la qualité de la modélisation sur le taux de chomage.
#On créé donc un df contenant tous les taux de chomage
df_chomage = data.xs('Chomage',axis = 1,level = 1,drop_level = True).drop(list(data.reset_index().loc[d,'Pays'][0] for d in range(88,99)))

#Note : on a une problème de valeurs manquantes sur ce df, pour l'instant on utilise donc 
#la fonction df.fillna() qui les remplacent par des 0, mais il faudra voir pour à terme 
#faire autre chose avec : 
df_chomage = df_chomage.dropna() 
'''

#------------ Partie Modélisation ----------------------------------------------

np.set_printoptions(suppress=True) # afin de rendre les sorties plus lisibles, on supprime les notations exponentielles.

#On créé le problème d'optimisation cvxpy :

#On prépare le vecteur qui contient les valeurs qui nous intéressent pour les USA : 
X1 = df_ct[['United-States', 'Variables']]
X1 = X1.drop(list(data.reset_index().loc[d,'Pays'][0] for d in range(88,99)))
X1_mean = df_ct_mean[['United-States', 'Variables']].groupby('Variables').mean().reset_index()
X1 = pd.concat([X1, X1_mean]).reset_index().drop(['index', 'Variables'], 1)
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
#cost = cvx.quad_form((X1 - X0@x),V_opt)                     #On définit la fonction de cout : norme des résidus
cost = cvx.pnorm(V_opt@(X1 - X0@x))  
constraints = [cvx.sum(x)==1]                               #La contrainte
prob = cvx.Problem(cvx.Minimize(cost), constraints)         #On définit le problème
  

#On définit une fonction qui renvoit le "cout" pour l'optimisation de la fonction V :
def loss_V(V) :
    V_opt.value = np.diag(np.abs(V)**1/2)
    prob.solve(warm_start = True)
    return(np.linalg.norm((df_chomage['United-States'].values - df_chomage.drop('United-States',axis = 1).values@ x.value)))

#Note de performance : utiliser la fonction pnorm plutot que quadform est plus avantageux (de peu, on gagne environ 8 minutes sur le temps d'éxecution total)

#On définit et résout le problème d'optimisation en V : 

# tps1 = clock()

contrainte = LinearConstraint(np.ones((1,154)), 1, 1)
bounds = [(0,1) for i in range(154)]
result = differential_evolution(loss_V,bounds,maxiter=100,constraints=contrainte,polish = False)

# tps2 = clock()
# print((tps2 - tps1)/60)

V_opt.value = np.diag(result.x)
prob.solve()
W = x.value
RMSPE = np.linalg.norm((X1 - X0@W))


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

#------------ Partie passage en fonction : -------------------------------------

def prep_donnee (pays):
    X1 = df_ct[[pays, 'Variables']]
    X1 = X1.drop(list(data.reset_index().loc[d,'Pays'][0] for d in range(88,99)))
    X1_mean = df_ct_mean[[pays, 'Variables']].groupby('Variables').mean().reset_index()
    X1 = pd.concat([X1, X1_mean]).reset_index().drop(['index', 'Variables'], 1)
    X1 = X1.values
    
    X0 = df_ct.drop(pays, 1)
    X0 = X0.drop(list(data.reset_index().loc[d,'Pays'][0] for d in range(88,99)))
    X0_mean = df_ct_mean.drop(pays, 1).groupby('Variables').mean().reset_index()
    X0 = pd.concat([X0, X0_mean]).reset_index().drop(['index', 'Variables'], 1)
    X0 = X0.values
    
    return (X1,X0)

def synth(X1,X0):
    V_opt = cvx.Parameter((154,154),PSD = True)                 #On définit V qui est un vecteur de paramètre
    x = cvx.Variable((24,1),nonneg=True)                        #On définit un vecteur de variables cvxpy
    cost = cvx.pnorm(V_opt@(X1 - X0@x))                         #On définit la fonction de cout : norme des résidus
    constraints = [cvx.sum(x)==1]                               #La contrainte
    prob = cvx.Problem(cvx.Minimize(cost), constraints)         #On définit le problème
    
    # tps1 = clock()

    contrainte = LinearConstraint(np.ones((1,154)), 1, 1)
    bounds = [(0,1) for i in range(154)]
    result = differential_evolution(loss_V,bounds,maxiter=100,constraints=contrainte,polish = False)

    # tps2 = clock()
    # print((tps2 - tps1)/60)
    
    V_opt.value = np.diag(result.x)
    prob.solve()
    W = x.value
    RMSPE = np.linalg.norm((X1 - X0@W))
    
    return(W,V_opt.value,RMSPE)

def synth_plot (W,pays) :
    X1,X0 = prep_donnee(pays)
    sc = df_pib.drop(['Variables',pays],axis = 1)@ W
    
    fig = plt.figure(0)
    plt.plot(np.linspace(1996,2019,df_pib[pays].values.shape[0]),
             df_pib[pays].values*100, label='{0}'.format(pays))
    plt.plot(np.linspace(1996,2019,df_pib[pays].values.shape[0]), sc.values*100,
             label='Synthetic Control')    
    plt.vlines(2017, 0, 100, linestyle='--', color='red', label='Election de Trump')

    # plt.errorbar(np.linspace(1995,2016,df_pib[pays].values.shape[0]),
    #             sc.values,
    #             2*(df_pib[pays].values - sc.values).std()/(96)**(1/2))
    error = (df_pib[pays].values - sc.values).std()/(df_pib[pays].values.shape[0])**(1/2)
    plt.title('Graphique du PIB : {0}'.format(pays))
    plt.xlabel('Années')
    plt.ylabel('Écart du PIB par rapport à 1995 en pourcentage')
    plt.fill_between(np.linspace(1996,2019,df_pib[pays].values.shape[0]),
                     df_pib[pays].values*100 - error*100, df_pib[pays].values*100 + error*100,
                     color='0.75')
    plt.legend()
    plt.show()
    plt.close()
    
    fig1 = plt.figure(1)
    plt.plot(np.linspace(1996,2019,df_chomage[pays].values.shape[0]),df_chomage[pays].values)
    # plt.errorbar(np.linspace(1996,2019,df_chomage[pays].values.shape[0]),
    #             df_chomage.drop(pays,axis = 1)@ W,
    #             2*np.linalg.norm((df_chomage[pays] - df_chomage.drop(pays,axis = 1)@ W)/89))
    
    plt.title('Courbe du chomage')
    plt.show()
    plt.close()


X1,X0 = prep_donnee('United-States')
W_US,V_US,RMSPE_US = synth(X1,X0)
synth_plot(W_US,'United-States')

#Il y a unproblème à un moment avec cles errorbars