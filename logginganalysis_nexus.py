#!/bin/env python
# Patrick
"""
Copyright (c) 2006, Patrick Gourhant
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation and/
or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE."""

import numpy as N
from pylab import *
import sys
import os
sys.path.append("/home/experiences/proxima1/com-proxima1/atelierPX1/bin") 
from readLoggingNexus_V2 import ReadLoggingNexus

repSourceFile = '/nfs/ruche-proxima1/proxima1-soleil/com-proxima1/'
repResultFile = '/nfs/ruche-proxima1/proxima1-soleil/tempdata/com-proxima1/'

# lecture du nom du fichier en ligne de commande
if len(sys.argv) > 0 :
    nomFichier = sys.argv[1]
else :
    print 'no filename argument'
    exit(0)  
    
listedesRepEtLeFichier = nomFichier.split('/')
listedesRep =  listedesRepEtLeFichier[:-1]
repDest = repResultFile
for nom in listedesRep :
    repDest = os.path.join(repDest,nom)
    if not os.path.isdir(repDest) :
        os.mkdir(repDest,0755)
print repDest

source = os.path.join(repSourceFile,nomFichier)
result = os.path.join(repDest,listedesRepEtLeFichier[-1].split('.')[0]  + '.result')

loggingNexus = ReadLoggingNexus(source)
#print " Forme du tableau :"
#print loggingNexus.get_ArrayAllData().shape

strMode = {1:'Mode External Trigger Position',2:'Mode External Trigger Images',3:'Mode External Enable Temporel',4:'Mode External Enable Position'}

## parametres collectes qui sont recuperees des technical data du fichier
params_collect = loggingNexus.get_paramsCollect()
collectAxis = params_collect['Collect_Axis']
theoricNbImages = params_collect['Number_of_Images']
theoricPosStart = params_collect['Start_Angle']
theoricPosStep = params_collect['Image_Width']
theoricTimeExpoPeriod = params_collect['Exposure_Period'] # Temps d'exposition en s
theoricMode = params_collect['Trigger_Mode']

theoricTimeReadOut = loggingNexus.get_paramsPilatus()['TimeReadOut'] # en s

theoricDeltaT = loggingNexus.get_paramsLogging()['Sampling_Rate']         # intervalle echantillonnage en sec

#############  A METTRE A JOUR SUIVANT FICHIER LU  #####################
#Tenir compte de la resolution en vitesse de la CB = 1/10000 degre.
theoricVitesse = int(theoricPosStep* 10000.0 / theoricTimeExpoPeriod) / 10000.0      # en deg/s

# On peut en deduire la resolution en position en fonction du Sampling rate
resolPos = theoricVitesse * theoricDeltaT
print "Resolution en position : %5.4f deg" %(resolPos)

# Ces parametres doivent etre passe en option sous forme d'option exemple : -P pour WithoutPilatus et -d40 pour deltaDeriv de 40 avec valeur par defaut
withoutPilatus = False 
DeltaDeriv = 40        # delta en nb points pour calcul derivee

# Recuperation des donnees de temps et de position
timeData = loggingNexus.get_timeData()
collectAxisData = loggingNexus.get_collectAxisData()

# Recuperation des etats shutter
shutterOpenData = loggingNexus.get_shutterOpenData()
critOpen = (shutterOpenData == 1)                   # recherche 1 dans 3eme colonne
iOpen = N.where(critOpen)[0]    
# le resultat de where est un tuple dont le 1er elmt est le tableau d'indices !
# iOpen contient donc un tableau des indices ou le shutter est ouvert
# Normalement il ne doit y avoir qu'une valeur dans ce tableau

shutterCloseData = loggingNexus.get_shutterCloseData()
critClose = (shutterCloseData == 1)                   # recherche 1 dans 3eme colonne
iClose = N.where(critClose)[0]

print 'Number of Open Shutter ', len(iOpen)
print 'Number of Close Shutter ', len(iClose)
if len(iOpen) != 1 or len(iClose) != 1:
    print 'Number of Open Shutter or Close Shutter not correct'
    exit(0)

posOpen = [collectAxisData[iOpen[0]]]
posClose = [collectAxisData[iClose[0]]]

timeOpen = [timeData[iOpen[0]]]
timeClose = [timeData[iClose[0]]]

    
strOpenClosePos = 'position Open = %7.4f, position Close = %7.4f\n' %(posOpen[0], posClose[0])
strOpenCloseTime = 'time Open = %7.4f, time Close = %7.4f\n' %(timeOpen[0], timeClose[0])
print strOpenClosePos
print strOpenCloseTime

## Creation posDebutImage = liste des positions debut image 
trigDebut = loggingNexus.get_statusPilatusExpOnData()
trigFin = loggingNexus.get_statusPilatusExpOffData()
       
iDebutImage = N.where(trigDebut == 1)[0]    # le resultat de where est un tuple dont le 1er elmt est le tableau d'indices !
#print 'iDebutimag ', len(iDebutImage), iDebutImage

posDebutImage = collectAxisData[iDebutImage]
#print posDebutImage,posDebutImage.shape

iFinImage = N.where(trigFin == 1)[0]    # le resultat de where est un tuple dont le 1er elmt est le tableau d'indices !
#print 'iFinimage ', len(iFinImage), iFinImage

posFinImage = collectAxisData[iFinImage]
#print posFinImage,posFinImage.shape

print 'nb iDebutImage = %d, nb iFinImage = %d' %(iDebutImage.shape[0], iFinImage.shape[0])

print 'nb iFinImage = %d, nb iFinImage = %d' %(len(iFinImage), len(iFinImage))
nbPoints = iFinImage - iDebutImage
#print nbPoints
strNPts = 'nbPoints   mean= %d +/- %d \n' %(mean(nbPoints), (max(nbPoints)-min(nbPoints))/2)
print strNPts

largePos = posFinImage - posDebutImage
timeDebutImage = timeData[iDebutImage]
#print timeDebutImage,timeDebutImage.shape

timeFinImage = timeData[iFinImage]
#print timeFinImage,timeFinImage.shape
largeTemps = timeFinImage - timeDebutImage

### CALCUL DES VALEURS THEORIQUES
#theoricNbImages = iDebutImage.shape[0]
#theoricPosStart = round(posDebutImage[0],2)
theoricTimeStart = round(timeDebutImage[0],2)
#theoricVitesse = (posDebutImage[-1] - posDebutImage[0]) / (timeDebutImage[-1] - timeDebutImage[0])
#theoricTimeExpoPeriod = round(mean(largeTemps) + theoricTimeReadOut,2)

theoricPosReadOut = theoricVitesse * theoricTimeReadOut
#theoricPosStep = round(mean(largePos) + theoricPosReadOut,2)
#theoricVitesse = theoricPosStep / theoricTimeExpoPeriod
#theoricPosReadOut = theoricVitesse * theoricTimeReadOut
theoricLargePos = theoricPosStep - theoricPosReadOut
theoricLargeTemps = theoricTimeExpoPeriod - theoricTimeReadOut

theoricPosDebutImage = arange(theoricPosStart,theoricPosStart + (theoricPosStep * theoricNbImages), theoricPosStep)
theoricTimeDebutImage = arange(theoricTimeStart,theoricTimeStart+(theoricTimeExpoPeriod * theoricNbImages), theoricTimeExpoPeriod)
#print theoricPosDebutImage, theoricPosDebutImage.shape
# Calcul en se basant sur l'horloge du Pilatus
#theoricPosPilatus = theoricPosStart + (((timeDebutImage - theoricTimeStart) * 0.999995))

theoricPosFinImage = arange(theoricPosStart + theoricPosStep - theoricPosReadOut,theoricPosStart + theoricPosStep - theoricPosReadOut + (theoricPosStep * theoricNbImages), theoricPosStep)
theoricTimeFinImage = arange(theoricTimeStart+theoricTimeExpoPeriod - theoricTimeReadOut,theoricTimeStart + theoricTimeExpoPeriod - theoricTimeReadOut + (theoricTimeExpoPeriod * theoricNbImages), theoricTimeExpoPeriod)
# Calcul en se basant sur l'horloge du Pilatus
#print theoricPosFinImage, theoricPosFinImage.shape

strParamCollect0 =  "Paramatres collecte \n"
strParamCollect1 =  "Collect axis : %s\n" %(collectAxis[0])
strParamCollect2 =  "%s\n" %(strMode[theoricMode])
strParamCollect3 =  "Oscillation Range : %7.4fdeg\n" %(theoricPosStep)
strParamCollect4 = "ExposureTime : %7.4fs\n" %(theoricTimeExpoPeriod)
strParamCollect5 = "Number of images : %d\n" %(theoricNbImages)
strParamCollect6 = "Oscillation Pos Start : %7.4fdeg\n" %(theoricPosStart)
strParamCollect7 = "Oscillation Time Start : %7.4fs\n" %(theoricTimeStart)
strParamCollect8 = "Oscillation End: %7.4fdeg\n" %(theoricPosStart + (theoricPosStep * theoricNbImages))
strParamCollect9 =  "Vitesse : %7.4fdeg/s\n" %(theoricVitesse)
strParamCollect10 = "Total Oscillation time: %7.4fs\n" %(theoricTimeExpoPeriod * theoricNbImages)
print strParamCollect0,strParamCollect1,strParamCollect2,strParamCollect3,strParamCollect4,strParamCollect5,strParamCollect6,strParamCollect7,strParamCollect8,strParamCollect9,strParamCollect10

strLPos = 'largPos    mean = %.4fdeg +/- %.4fdeg - sigma = %.4fdeg (theoric : %.4fdeg)\n' %(mean(largePos), (max(largePos)-min(largePos))/2, std(largePos),theoricLargePos)
print strLPos
strLTps = 'largeTemps  mean= %7.4fs     +/-%7.4fs     sigma= %7.4fs  (theoric : %7.4fs)\n' %(mean(largeTemps),(max(largeTemps)-min(largeTemps))/2,std(largeTemps),theoricLargeTemps)
print strLTps

vitesses = largePos/largeTemps
#print vitesses, vitesses.shape
strVit  = 'vitesses   mean= %7.4fdeg/s +/-%7.4fdeg/s sigma= %7.4fdeg/s  (theoric : %7.4fdeg/s)\n' %(mean(vitesses),(max(vitesses)-min(vitesses))/2, std(vitesses),theoricVitesse)
print strVit

if theoricMode in (3,4) :
    theoricPosDebutSpi = theoricPosStart + (((timeDebutImage - theoricTimeStart) * theoricVitesse))
    ecartDebutImage = posDebutImage - theoricPosDebutSpi
    theoricPosFinSpi = theoricPosStart + (((timeFinImage - theoricTimeStart) * theoricVitesse))
    ecartFinImage = posFinImage - theoricPosFinSpi
elif theoricMode in (1,2) :     
    theoricPosDebutPilatus = theoricPosStart + (((timeDebutImage - theoricTimeStart) * theoricVitesse))
    ecartDebutImage = posDebutImage - theoricPosDebutPilatus
    theoricPosFinPilatus = theoricPosStart + (((timeFinImage - theoricTimeStart) * theoricVitesse))
    ecartFinImage = posFinImage - theoricPosFinPilatus
#print ecartDebutImage,ecartDebutImage.shape
strEDebutImage = 'ecartDebutImage  mean= %7.4fdeg   +/-%7.4fdeg   sigma= %7.4fdeg   (theoric : %7.4fdeg)\n' %(mean(ecartDebutImage), (max(ecartDebutImage)-min(ecartDebutImage))/2,std(ecartDebutImage),0.0)
print strEDebutImage

#print ecartFinImage,ecartFinImage.shape
strEFinImage = 'ecartFinImage  mean= %7.4fdeg   +/-%7.4fdeg   sigma= %7.4fdeg   (theoric : %7.4fdeg)\n' %(mean(ecartFinImage), (max(ecartFinImage)-min(ecartFinImage))/2,std(ecartFinImage),0.0)
print strEFinImage

timeReadOut = timeDebutImage[1:] - timeFinImage[:-1]
#print timeReadOut
strTimeReadOut = 'timeReadOut  mean= %7.4fs   +/-%7.4fs   sigma= %7.4fs   (theoric : %7.4fs)\n' %(mean(timeReadOut), (max(timeReadOut)-min(timeReadOut))/2,std(timeReadOut),theoricTimeReadOut)
print strTimeReadOut

posReadOut =  posDebutImage[1:] - posFinImage[:-1]
#print posReadOut
strPosReadOut = 'posReadOut  mean= %7.4fdeg   +/-%7.4fdeg   sigma= %7.4fdeg   (theoric : %7.4fdeg)\n' %(mean(posReadOut), (max(posReadOut)-min(posReadOut))/2,std(posReadOut),theoricPosReadOut)
print strPosReadOut


## plot tableau positions + vert lignes verticales aux pos ouv et ferm shutter
figure (figsize = (10,10))
subplots_adjust(hspace=0.5)

#subplot (411)                   # 3 = nb subplots dans m figure, dernier = no subplot
#plot (collectAxisData, 'b')
#plot (shutterOpenData*100,'r')
#plot (shutterCloseData*100,'g')
#title('Open(red)/Close(green) Shutter positions in deg')

## plot tableau positions + vert lignes verticales aux pos debut image et fin image
subplot (311)                   # 3 = nb subplots dans m figure, dernier = no subplot
#plot (collectAxisData, 'b')
#plot (trigDebut*100,'r')
#plot (trigFin*100,'g')
#title('Images positions in deg (red for begin, green for end')
title('Ecarts en temps des prises images')

x = theoricTimeDebutImage
yDebut = timeDebutImage - theoricTimeDebutImage
yFin = timeFinImage - theoricTimeFinImage
plot(x,yDebut,'b')
plot(x,yFin,'r')
#legend(('debut image','fin image'),loc = 'upper left')
xlim(theoricTimeStart,(theoricTimeStart + (theoricTimeExpoPeriod * theoricNbImages)))
xlabel('time in s.')
ylabel('error in s.')


subplot (312)            
title('Ecarts en position des prises images')
colors = ['c', 'g', 'r', 'b', 'm', 'y', 'b', 'chartreuse', 'burlywood', 'aqua', 'grey', 'c', 'g']
# Calcul de la pente due a l'errur de vitesse
x = theoricPosDebutImage
yDebut = ecartDebutImage # en deg
A = N.vstack([x, N.ones(len(x))]).T
(m, c), err = N.linalg.lstsq(A, yDebut)[0:2]
residu = ecartDebutImage - ((x * m) + c)
strPente = "Regression lineaire: pente= %.7f   offset= %.4f \n" % ( m, c)
print  strPente
strResidu =  "positioning errors : mean= %.4fdeg +/-%.4fdeg  sigma= %.4fdeg (theoric: 0.0000deg)\n" % (mean(residu),(max(residu)-min(residu))/2.0, std(residu))
print strResidu
yDebut = residu
yDebut = ecartDebutImage

x = theoricPosDebutImage
# xlim(theoricPosDebutImage[0],theoricPosDebutImage[-1])
yFin = ecartFinImage
plot(x,yDebut,'b')
plot(x,yFin,'r')
#legend(('debut image','fin image'), loc='upper left') 
xlim(int(theoricPosStart),int((theoricPosStart + (theoricPosStep * theoricNbImages))))
xlabel('angle in deg.')
ylabel('error in deg.')
#try :
#    zonePosImages = collectAxisData[iDebutImage[0]:iFinImage[iFinImage.shape[0]-1]+int(theoricTimeReadOut/theoricDeltaT)-1]
#    #print zonePosImages,zonePosImages.shape
#    zonesImages = zonePosImages.reshape(-1,int(theoricTimeExpoPeriod/theoricDeltaT)) 
#    trueZonesImages = zonesImages[:,:-int(theoricTimeReadOut/theoricDeltaT)]
#    for i in trueZonesImages:
#        plot (i - i[0], colors[0])
#except :
#    print " Probleme de creation du tableau des zones images"    

#print trueZonesImages[1] - trueZonesImages[1][0]


subplot (313)            # pour plot recouvrement entre images
plot (posReadOut, 'b')
title('Repeatability of read time in deg')

savefig(result + '.png')

f = open (result, 'w')
#f.write ('\nVitesse = %3.1fdeg/s - Mode : %s - PosStart : %7.4fdeg - PosStep : %7.4fdeg) \n' % (theoricVitesse, strMode[theoricMode],theoricPosStart,theoricPosStep))
f.write ('Nombre images = %5d (theoric : %5d)\n' %(len(iDebutImage),theoricNbImages))
f.write ('Fichier : %s \n' %(repSourceFile + nomFichier))
f.writelines ([strParamCollect0,strParamCollect1,strParamCollect2,strParamCollect3,strParamCollect4,strParamCollect5,strParamCollect6,strParamCollect7,strParamCollect8,strParamCollect9])
f.writelines ([strOpenClosePos, strNPts, strLPos, strLTps, strVit, strEDebutImage, strEFinImage,strTimeReadOut,strPosReadOut])

f.writelines ([strPente,strResidu, '\n'])

f.close ()

## affichage de toutes les figures
show()

    

