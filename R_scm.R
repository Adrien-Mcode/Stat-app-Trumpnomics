
##########   Package    ###########
#install.packages(Synth)
library(datasets)
library(dbplyr)
library(dplyr)
library(stringr)
library(Synth)
library(tidyr)
library(readxl)



##########   Import des données    ###########
tableR <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/dfR_complete.csv")

# On met les dates en un format numérique
tableR$TIME <- str_replace_all(tableR$TIME, "[:punct:]Q1", ".00" )
tableR$TIME <- str_replace_all(tableR$TIME, "[:punct:]Q2", ".25" )
tableR$TIME <- str_replace_all(tableR$TIME, "[:punct:]Q3", ".50" )
tableR$TIME <- str_replace_all(tableR$TIME, "[:punct:]Q4", ".75" )
tableR <- transform(tableR, TIME = as.numeric(TIME))
tableR$LOCATION <- as.character(tableR$LOCATION)
str(tableR)

#Création de la liste des prédicteurs
list_predictor <- rep(list(list()), 261)

#PIB
for (i in 1:87) {
  list_predictor[[i]] <- append(list_predictor[[i]], list('PIB', tableR$TIME[i+1], 'mean'))
}
#Emplois
for (j in 1:87) {
  list_predictor[[j+87]]  <- append(list_predictor[[j+87]], list('Emplois', tableR$TIME[j+1], 'mean'))
}
#Actifs
for (k in 1:87) {
  list_predictor[[k+174]]  <- append(list_predictor[[k+174]], list('Actifs', tableR$TIME[k+1], 'mean'))
}


##########   Création des vecteurs du problème d'optimisation    ###########
dataprep.out <- dataprep(
  foo = tableR,
  predictors = c("Chomage", "Conso_share", "Invest_share", 'Export_share', 'Labor_prod'),
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
synth.out <- synth(data.prep.obj = dataprep.out, method = "BFGS")

#Tableaux des matching et poids
synth.tables <- synth.tab(dataprep.res = dataprep.out, synth.res = synth.out)
synth.tables$tab.pred #Tableau des prédictions comparées aux valeurs observées
synth.tables$tab.w    #Tableau des pondérations
synth.tables$tab.v
gaps <- dataprep.out$Y1plot - (dataprep.out$Y0plot %*% synth.out$solution.w)
gaps  #Ecart entre le PIB prédit par le contrôle synthétique et le PIB observé des US

#write.csv(synth.out$solution.w,"C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/ponderation.csv")

##########   Graphiques    ###########
path.plot(synth.res = synth.out, dataprep.res = dataprep.out, Ylab = "Chomage", Xlab = "year", Legend = c("USA", "synthetic"), Legend.position = "topright")
abline(v = 2016.75, col="blue", lwd=3, lty=2)
gaps.plot(synth.res = synth.out, dataprep.res = dataprep.out, Ylab = "gap in unemployment rate", Main = NA)
abline(v = 2016.75, col="blue", lwd=3, lty=2)

#Plot du PIB 

#pred_pib <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred_pib.csv")
pred2_pib <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred2_pib.csv")


gaps_pib <- tableR$PIB[1718:1804] - pred2_pib$X0[1:87]
sd_pib <- sd(gaps_pib)

pib_p <- pred2_pib$X0 + sd_pib
pib_m <- pred2_pib$X0 - sd_pib
#sc_pib <- c(synth.tables$tab.pred[6:92,2], pred_pib$X0)

plot(tableR$TIME[2:101], tableR$PIB[1718:1817], ylab = 'PIB (en variation depuis 1995)', xlab = 'Time', ylim = c(0,1.2), col="red", type = "l", lty = 1, lwd=4)
#lines(tableR$TIME[2:101], sc_pib, col="red",lty=5)
lines(tableR$TIME[1:101], pred2_pib$X0, col="blue", type = "l", lty=1, lwd=4)
lines(tableR$TIME[1:101], pib_p, col="black",lty=2)
lines(tableR$TIME[1:101], pib_m, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 1, legend=c("USA", "contrôle synthétique", "élection de Trump"),
       col=c("red", "blue", "green"), lty=1, cex=0.8)

#Plot du chomage
pred_cho <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred_cho.csv")

plot(tableR$TIME[1:101], pred_cho$USA, ylab = 'Taux de chômage', xlab = 'Time', ylim = c(0,12), col="red", type = "l", lty = 1, lwd=4)
lines(tableR$TIME[1:101], pred_cho$sc, col="blue", type = "l", lty=1, lwd=4)
lines(tableR$TIME[1:101], pred_cho$chom, col="black",lty=2)
lines(tableR$TIME[1:101], pred_cho$chop, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 12, legend=c("USA", "contrôle synthétique", "élection de Trump"),
       col=c("red", "blue", "green"), lty=1, cex=0.8)

#Plot de l'emploi
pred_emp <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred_emp.csv")

plot(tableR$TIME[1:101], pred_emp$USA, ylab = 'Emplois', xlab = 'Time', ylim = c(0,0.5), col="red", type = "l", lty = 1, lwd=4)
lines(tableR$TIME[1:101], pred_emp$sc, col="blue", type = "l", lty=1, lwd=4)
lines(tableR$TIME[1:101], pred_emp$empm, col="black",lty=2)
lines(tableR$TIME[1:101], pred_emp$empp, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 0.5, legend=c("USA", "contrôle synthétique", "élection de Trump"),
       col=c("red", "blue", "green"), lty=1, cex=0.8)

#Plot des actifs
pred_actifs <- read.csv("C:/Users/adxva/OneDrive/Bureau/ENSAE 2A - S1/STAT APP/pred_actifs.csv")

plot(tableR$TIME[1:101], pred_actifs$USA, ylab = 'Actifs', xlab = 'Time', ylim = c(0,0.5), col="red", type = "l", lty = 1, lwd=4)
lines(tableR$TIME[1:101], pred_actifs$sc, col="blue", type = "l", lty=1, lwd=4)
lines(tableR$TIME[1:101], pred_actifs$actm, col="black",lty=2)
lines(tableR$TIME[1:101], pred_actifs$actp, col="black",lty=2)
abline(v = 2016.75, col="green", lwd=3, lty=2)
legend(1995, 0.5, legend=c("USA", "contrôle synthétique", "élection de Trump"),
       col=c("red", "blue", "green"), lty=1, cex=0.8)



