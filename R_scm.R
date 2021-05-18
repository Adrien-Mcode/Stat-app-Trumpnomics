
##########   Package    ###########
library(Synth)
library(SCtools)
library(stringr)



##########   Import des données    ###########

#Après avoir importer la base, on observe sa forme puis on met la variable "TIME" au format numérique.
data <- read.csv("dfR_complete_netexp.csv")
summary(data)


data$TIME <- str_replace_all(data$TIME, "[:punct:]Q1", ".00" )
data$TIME <- str_replace_all(data$TIME, "[:punct:]Q2", ".25" )
data$TIME <- str_replace_all(data$TIME, "[:punct:]Q3", ".50" )
data$TIME <- str_replace_all(data$TIME, "[:punct:]Q4", ".75" )
data <- transform(data, TIME = as.numeric(TIME))
data$LOCATION <- as.character(data$LOCATION)
summary(data)


#Création de la liste des prédicteurs
list_predictor <- rep(list(list()), 261)

#PIB
for (i in 1:87) {
  list_predictor[[i]] <- append(list_predictor[[i]], list('PIB', data$TIME[i+1], 'mean'))
}
#Emplois
for (j in 1:87) {
  list_predictor[[j+87]]  <- append(list_predictor[[j+87]], list('Emplois', data$TIME[j+1], 'mean'))
}
#Actifs
for (k in 1:87) {
  list_predictor[[k+174]]  <- append(list_predictor[[k+174]], list('Actifs', data$TIME[k+1], 'mean'))
}

########## MODELE BASELINE #########

#On utilise d'abord la fonction dataprep() du package "Synth", 
#qui va préparer les vecteurs et matrices utilisées pour trouver la pondération. 
#x1 est le vecteur pour l'unité traité (les Etats-Unis) des 3 séries temporelles et des 5 covariables, 
#X0, la matrice équivalente pour les unités de contrôle (le donor pool), 
#Z1 le vecteur de la variable d'intérêt (ici le taux de chômage) pour l'unité traité 
#et Z0 la matrice de la variable d'intérêt pour chacun des pays du donor pool.



##########   Création des vecteurs du problème d'optimisation    ###########
dataprep.out <- dataprep(
  foo = data,
  predictors = c("Chomage", "Conso_share", "Invest_share", 'NExport_share', 'Labor_prod'),
  predictors.op = "mean",
  time.predictors.prior = 2015.50:2016.50,
  special.predictors = list_predictor,
  dependent = "Chomage",
  unit.variable = "ID_country",
  unit.names.variable = "LOCATION",
  time.variable = "TIME",
  treatment.identifier = 25,
  controls.identifier = 1:24,
  time.optimize.ssr = 1995.00:2016.50,
  time.plot = 1995.00:2020.00)



##########   Vecteurs et matrices obtenus    ###########
dataprep.out$X1  #Vecteur des US
dataprep.out$X0  #Matrice du donor pool
dataprep.out$Z1  #Vecteur du taux de chômage US sur la période d'entraînement
dataprep.out$Z0  #Matrice des taux de chômage des unités de contrôle sur la période d'entraînement


##########   Résolution du problème d'optimisation et résultats    ###########
#Résolution du problème de minisation à l'aide de la fonction synth() du package "Synth".
#Elle nous donne en sortie les valeurs prédites par le contrôle synthétique pour chacune des variables de la minimisation, 
#la pondération W du contrôle synthétique et la pondération V des variables.


start.time <- Sys.time()
synth.out <- synth(data.prep.obj = dataprep.out, method = "All")
end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken

#Tableaux des matching et poids

synth.tables <- synth.tab(dataprep.res = dataprep.out, synth.res = synth.out)
gaps <- dataprep.out$Y1plot - (dataprep.out$Y0plot %*% synth.out$solution.w)
#Ecart entre le taux de chômage prédit par le contrôle synthétique et celui observé des US

head(synth.tables$tab.pred, 5) #Tableau des prédictions comparées aux valeurs observées
head(synth.tables$tab.v, 5)    #Tableau des pondérations des variables
synth.tables$tab.w            #Tableau des pondérations des pays


##########   Graphiques du modèle baseline    ###########
path.plot(synth.res = synth.out, dataprep.res = dataprep.out, Ylab = "Chomage", Xlab = "year", Legend = c("USA", "synthetic"), Legend.position = "topright")
abline(v = 2016.75, col="blue", lwd=3, lty=2)
gaps.plot(synth.res = synth.out, dataprep.res = dataprep.out, Ylab = "gap in unemployment rate", Main = NA)
abline(v = 2016.75, col="blue", lwd=3, lty=2)

#Pour le taux de chômage, le PIB, l'emploi et les actifs, on trace les courbes obtenus pour les Etats-Unis et le contrôle synthétique,
#l'intervalle de confiance étant obtenu par + ou - 2 fois l'écart-type de la différence entre les vraies valeurs 
#et celles prédites sur la période pré-traitement.

#Plot du PIB 

graph_bl <- read.csv("graph_bl.csv")
gaps_pib <- data$PIB[1718:1804] - graph_bl$USA_pib[1:87]
sd_pib <- sd(gaps_pib)
pib_p <- graph_bl$USA_pib + 2*sd_pib
pib_m <- graph_bl$USA_pib - 2*sd_pib


plot(data$TIME[2:101], data$PIB[1718:1817], ylab = 'PIB (en variation depuis 1995)', xlab = 'Time', ylim = c(0,1.2), col="blue", type = "l", lty = 1, lwd=4)
lines(data$TIME[1:101], graph_bl$USA_pib, col="red", type = "l", lty=1, lwd=4)
lines(data$TIME[1:101], pib_p, col="black",lty=2)
lines(data$TIME[1:101], pib_m, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 1, legend=c("USA", "contrôle synthétique", "élection de Trump"), col=c("blue", "red", "green"), lty=1)

#Plot du chomage
chom = graph_bl$sc_cho - 2*sd(graph_bl$USA_cho - graph_bl$sc_cho)
chop = graph_bl$sc_cho + 2*sd(graph_bl$USA_cho - graph_bl$sc_cho)

plot(data$TIME[1:101], graph_bl$USA_cho, ylab = 'Taux de chômage', xlab = 'Time', ylim = c(0,10), col="blue", type = "l", lty = 1, lwd=4)
lines(data$TIME[1:101], graph_bl$sc_cho, col="red", type = "l", lty=1, lwd=4)
lines(data$TIME[1:101], chom, col="black",lty=2)
lines(data$TIME[1:101], chop, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 10, legend=c("USA", "contrôle synthétique", "élection de Trump"), col=c("blue", "red", "green"), lty=1)


#Plot de l'emploi
empm = graph_bl$sc_emp - 2*sd(graph_bl$USA_emp - graph_bl$sc_emp)
empp = graph_bl$sc_emp + 2*sd(graph_bl$USA_emp - graph_bl$sc_emp)

plot(data$TIME[1:101], graph_bl$USA_emp, ylab = 'Emplois (en variation depuis 1995))', xlab = 'Time', ylim = c(0,0.8), col="blue", type = "l", lty = 1, lwd=4)
lines(data$TIME[1:101], graph_bl$sc_emp, col="red", type = "l", lty=1, lwd=4)
lines(data$TIME[1:101], empm, col="black",lty=2)
lines(data$TIME[1:101], empp, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 0.8, legend=c("USA", "contrôle synthétique", "élection de Trump"), col=c("blue", "red", "green"), lty=1)

#Plot des actifs
actm = graph_bl$sc_act - 2*sd(graph_bl$USA_act - graph_bl$sc_act)
actp = graph_bl$sc_act + 2*sd(graph_bl$USA_act - graph_bl$sc_act)

plot(data$TIME[1:101], graph_bl$USA_act, ylab = 'Actifs (en variation depuis 1995))', xlab = 'Time', ylim = c(0,0.8), col="blue", type = "l", lty = 1, lwd=4)
lines(data$TIME[1:101], graph_bl$sc_act, col="red", type = "l", lty=1, lwd=4)
lines(data$TIME[1:101], actm, col="black",lty=2)
lines(data$TIME[1:101], actp, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 0.8, legend=c("USA", "contrôle synthétique", "élection de Trump"), col=c("blue", "red", "green"), lty=1)

##########   Tests de robustesse    ###########

# Test du leave-one-out

country <- c(4, 12, 13, 14, 16, 22)
y0plot1 <- dataprep.out$Y0plot %*% synth.out$solution.w
d <- as.data.frame(y0plot1)

for (i in country) {
  dp.out <- dataprep(
    foo = data,
    predictors = c("Chomage", "Conso_share", "Invest_share", 'NExport_share', 'Labor_prod'),
    predictors.op = "mean",
    time.predictors.prior = 2015.50:2016.50,
    special.predictors = list_predictor,
    dependent = "Chomage",
    unit.variable = "ID_country",
    unit.names.variable = "LOCATION",
    time.variable = "TIME",
    treatment.identifier = 25,
    controls.identifier = c(1:(i-1),(i+1):24),
    time.optimize.ssr = 1995.00:2016.50,
    time.plot = 1995.00:2020.00)
  s.out <- synth(data.prep.obj = dp.out, method = "BFGS")
  y0plot <- dp.out$Y0plot %*% s.out$solution.w
  d[ , ncol(d) + 1] <- y0plot                  # Append new column
  colnames(d)[ncol(d)] <- paste0("y0plot", i)  # Rename column name
}

plot(dataprep.out$tag$time.plot, dataprep.out$Y1plot, col = 'red', type = 'l',lwd=3, lty=1, xlab = 'Time', ylab = 'Taux de chomage')
lines(dataprep.out$tag$time.plot, d$w.weight, col = 'blue', type = 'l',lwd=3, lty=2)
lines(dataprep.out$tag$time.plot, d$y0plot4, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot12, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot13, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot14, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot16, col = 'grey', type = 'l',lwd=2, lty=3)
lines(dataprep.out$tag$time.plot, d$y0plot22, col = 'grey', type = 'l',lwd=2, lty=3)
abline(v = 2016.75, col="black", lwd=3, lty=2)
legend(1995, 10, legend=c("USA", "contrôle synthétique", "élection de Trump", "leave-one-out"),
       col=c("red", "blue", "black", "grey"), lty=c(1,2,2,3,3,3))

# Space placebos

tdf <- generate.placebos(dataprep.out,synth.out, Sigf.ipop = 2, strategy = "multiprocess")
mspe.plot(
  tdf,
  discard.extreme = FALSE,
  mspe.limit = 20,
  plot.hist = FALSE,
  title = "Ratio MSPE Chomage",
  xlab = "Post/Pre MSPE ratio",
  ylab = NULL
)

ratio <- mspe.test(tdf)
ratio$p.val # p-value obtenue

plot_placebos(
  tdf = tdf,
  discard.extreme = FALSE,
  mspe.limit = 20,
  xlab = 'Time',
  ylab = 'Différence de taux de chômage entre prédicteurs et vraies valeurs pour chacun des pays',
  title = "Placebo chomage",
  alpha.placebos = 1,
)

# Time placebo 2011
list_pred_2011 <- rep(list(list()), 189)

#PIB
for (i in 1:63) {
  list_pred_2011[[i]] <- append(list_pred_2011[[i]], list('Chomage', data$TIME[i+1], 'mean'))
}
#Emplois
for (j in 1:63) {
  list_pred_2011[[j+63]]  <- append(list_pred_2011[[j+63]], list('Emplois', data$TIME[j+1], 'mean'))
}
#Actifs
for (k in 1:63) {
  list_pred_2011[[k+126]]  <- append(list_pred_2011[[k+126]], list('Actifs', data$TIME[k+1], 'mean'))
}

dp2011.out <- dataprep(
  foo = data,
  predictors = c("Chomage", "Conso_share", "Invest_share", 'NExport_share', 'Labor_prod'),
  predictors.op = "mean",
  time.predictors.prior = 2009.50:2010.75,
  special.predictors = list_pred_2011,
  dependent = "Chomage",
  unit.variable = "ID_country",
  unit.names.variable = "LOCATION",
  time.variable = "TIME",
  treatment.identifier = 25,
  controls.identifier = 1:24,
  time.optimize.ssr = 1995.00:2010.75,
  time.plot = 1995.00:2020.00)

start.time <- Sys.time()
synth2011.out <- synth(data.prep.obj = dp2011.out, method = "BFGS")
end.time <- Sys.time()
time.taken <- end.time - start.time
time.taken


synth2011.tables <- synth.tab(dataprep.res = dp2011.out, synth.res = synth2011.out)
synth2011.tables$tab.w

path.plot(synth.res = synth2011.out, dataprep.res = dp2011.out, Ylab = "Chomage", Xlab = "year", Legend = c("USA", "synthetic"), Legend.position = "topright")
abline(v = 2011, col="green", lwd=3, lty=2)
lines(data$TIME[1:101], graph_bl$sc_cho, col="red", type = "l", lty=1, lwd=4)
lines(data$TIME[1:101], chom, col="grey",lty=2)
lines(data$TIME[1:101], chop, col="grey",lty=2)

##########   Modèle alternatif    ###########

# on reprend le code du modèle baseline en inversant chômage et PIB

list_pred_pib <- rep(list(list()), 261)

#Chomage
for (i in 1:87) {
  list_pred_pib[[i]] <- append(list_pred_pib[[i]], list('Chomage', data$TIME[i+1], 'mean'))
}
#Emplois
for (j in 1:87) {
  list_pred_pib[[j+87]]  <- append(list_pred_pib[[j+87]], list('Emplois', data$TIME[j+1], 'mean'))
}
#Actifs
for (k in 1:87) {
  list_pred_pib[[k+174]]  <- append(list_pred_pib[[k+174]], list('Actifs', data$TIME[k+1], 'mean'))
}

dp_pib.out <- dataprep(
  foo = data,
  predictors = c("PIB", "Conso_share", "Invest_share", 'NExport_share', 'Labor_prod'),
  predictors.op = "mean",
  time.predictors.prior = 2015.50:2016.50,
  special.predictors = list_pred_pib,
  dependent = "PIB",
  unit.variable = "ID_country",
  unit.names.variable = "LOCATION",
  time.variable = "TIME",
  treatment.identifier = 25,
  controls.identifier = 1:24,
  time.optimize.ssr = 1995.00:2016.50,
  time.plot = 1995.00:2020.00)

#dp_pib.out$X1
#dp_pib.out$X0  
#dp_pib.out$Z0
dp_pib.out$Z1

s_pib.out <- synth(data.prep.obj = dp_pib.out, method = "BFGS")

s_pib.tables <- synth.tab(dataprep.res = dp_pib.out, synth.res = s_pib.out)
gaps <- dp_pib.out$Y1plot - (dp_pib.out$Y0plot %*% s_pib.out$solution.w)

head(s_pib.tables$tab.pred, 5)
head(s_pib.tables$tab.v, 5)
s_pib.tables$tab.w

# Graphiques des résultats

graph_pib <- read.csv("graph_pib.csv")
gaps_pib2 <- data$PIB[1718:1804] - graph_pib$sc_pib[1:87]
sd_pib2 <- sd(gaps_pib2)
pib_p2 <- graph_pib$sc_pib + sd_pib2
pib_m2 <- graph_pib$sc_pib - sd_pib2

plot(data$TIME[2:101], data$PIB[1718:1817], ylab = 'PIB (en variation depuis 1995)', xlab = 'Time', ylim = c(0,1.2), col="blue", type = "l", lty = 1, lwd=2)
lines(data$TIME[1:101], graph_pib$sc_pib, col="red", type = "l", lty=1, lwd=2)
lines(data$TIME[1:101], pib_p2, col="black",lty=2)
lines(data$TIME[1:101], pib_m2, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 1, legend=c("USA", "contrôle synthétique", "élection de Trump"), col=c("blue", "red", "green"), lty=1)

chom2 = graph_pib$sc_cho - 2*sd(data$Chomage[1718:1804] - graph_pib$sc_cho)
chop2 = graph_pib$sc_cho + 2*sd(data$Chomage[1718:1804] - graph_pib$sc_cho)

plot(data$TIME[2:101], data$Chomage[1718:1817], ylab = 'Taux de chômage', xlab = 'Time', ylim = c(0,10), col="blue", type = "l", lty = 1, lwd=4)
lines(data$TIME[1:101], graph_pib$sc_cho, col="red", type = "l", lty=1, lwd=4)
lines(data$TIME[1:101], chom2, col="black",lty=2)
lines(data$TIME[1:101], chop2, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 10, legend=c("USA", "contrôle synthétique", "élection de Trump"), col=c("blue", "red", "green"), lty=1)

# Tests de robustesse pour le modèle alternatif

tdf2 <- generate.placebos(dp_pib.out,s_pib.out, Sigf.ipop = 2, strategy = "multiprocess")

mspe.plot(
  tdf2,
  discard.extreme = FALSE,
  mspe.limit = 20,
  plot.hist = FALSE,
  title = "Ratio MSPE PIB",
  xlab = "Post/Pre MSPE ratio",
  ylab = NULL
)
ratio2 <- mspe.test(tdf2)

plot_placebos(
  tdf = tdf2,
  discard.extreme = FALSE,
  mspe.limit = 20,
  xlab = 'Time',
  ylab = 'Différence de PIB entre prédicteurs et vraies valeurs pour chacun des pays',
  title = "Placebo PIB",
  alpha.placebos = 1,
)

ratio2$p.val
