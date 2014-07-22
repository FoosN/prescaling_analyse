#!/usr/bin/python2.7
# -*-coding:Utf-8 -*
"""Progs to plot scale corrections factors
 vs Xray flux variations acquired by Xbpm. 
 Fitting and correlation search 
 according theses data """
import sys
import os

VERBOSE = True

# OPTIONS :
# --g, -graph  Show graph in interactiv mode, if used : script don't
# stop untill graph are manually closed.
if '--g' in sys.argv :
    sys.argv.remove('--g')
    GRAPH = True
else :
    GRAPH = False
    pass

if '--n' in sys.argv :
    print "How many degree between each point would you use to sampling?"\
" Set f number of degree"
    sys.argv.remove('--n')
    NUMBER_POINT_4FIT = int(raw_input())
else :
    NUMBER_POINT_4FIT = False
    pass

if '--r' in sys.argv :
    sys.argv.remove('--r')    
    RANDOM = True
else :
    RANDOM = False
    pass

if '--c' in sys.argv :
    sys.argv.remove('--c')
    CUBIC = True
else :
    CUBIC = False
    pass
# read the file name given in the command line
if len(sys.argv) > 2 :
    input_file = sys.argv[1]
else : 
    print 'no Datafile.LP'
if len(sys.argv) >= 3 :
    nomFichier = sys.argv[2]
else :
    print 'no Datafile.nxs'
    exit(0)
# importing Xbpm Value (thanks to Patrick Ghourant scripts) 
from readLoggingNexus_V2 import ReadLoggingNexus
from math import pi
import numpy as np
import matplotlib.pyplot as pp
from scipy import interpolate

nomFichier2 = nomFichier.split('/')
nomFichier2 = nomFichier2[-1:].pop(0)
i = nomFichier2[:-24]
if RANDOM and NUMBER_POINT_4FIT:
    resultFile = 'resultsOfAnalysis.' + i + 'rand' +'.n.'+ str(NUMBER_POINT_4FIT)
elif RANDOM :
    resultFile = 'resultsOfAnalysis.' + i + 'rand'
elif NUMBER_POINT_4FIT:
    resultFile = 'resultsOfAnalysis.' + i + '.n.'+ str(NUMBER_POINT_4FIT)
else :
    resultFile = 'resultsOfAnalysis.' + i

try:
    os.makedirs(resultFile, 0777)
except OSError, e:
    print 'WARNING : Problem to create Directory for results'
    if not "File exists" in e:
       exit(0)
"""Create log file for summary of key value"""

def log(title, newInfo, verbose=False)  :
    """specific fonction to fill the log file, open file log1 and write newInfo"""
    log1 = open(os.path.join(resultFile, "%s.log"%i), 'a')
    title = str(title)
    newInfo = str(newInfo)
    info = (title +' '+ newInfo)    
    log1.write(info+ '\n')
    if verbose:
        print info
    log1.close()
     
# Import SCALE value

f = open(input_file)
lines = f.readlines()
f.close()

def filtre1(l):
    try:
        ln = l.split()
        map(float, ln)
        if len(ln) == 10 and ln[1] == "0":
           return True
    except:
        return False

tabl = np.array([map(float,line.split()) for line in lines if filtre1(line)])
print tabl

for r in lines:
    if r.find('OSCILLATION_RANGE') > -1:
        nbrLigne = lines.index(r)
        oscilation = float(lines[nbrLigne].split()[-2])
        oscilFind = True
if oscilFind:
    log('Oscilation =', oscilation, VERBOSE)
else : 
    print "oscilation not found"
    exit(0)
        
angleImage = 360/oscilation             
X = tabl[:,0]*2*pi/angleImage
Y = tabl[:,2]
# figure 1
pp.clf() #clear the figure
pp.plot(np.arange(len(X))*oscilation, tabl[:,2])
pp.xlabel("Angle in deg")
pp.ylabel("Scale correction factor")
#print resultFile
pp.savefig(os.path.join(resultFile, "Scale_correction_factor.png"), dpi=150, facecolor='w',
edgecolor='w', orientation='landscape')
pp.figure()
#pp.show()       

# Thanks to readLoggingNexus_V2
# Data collection params from technical data of Flyscan-file
repSourceFile = './'
source = os.path.join(repSourceFile, nomFichier)

loggingNexus = ReadLoggingNexus(source)
params_collect = loggingNexus.get_paramsCollect()
theoricNbImages = params_collect['Number_of_Images']
log("image number",theoricNbImages)
# Start signal given by Pilatus = list position of each image start recording
trigDebut = loggingNexus.get_statusPilatusExpOffData()
trigFin = loggingNexus.get_statusPilatusExpOnData()

iDebutImage = np.where(trigDebut == 1)[0]
iFinImage = np.where(trigFin == 1)[0]
# Determine number of mesure acquired by xbpm along the data-collection
DAQVals = loggingNexus.get_DAQVals()
intensity = DAQVals[0] # at this time only DAQ[0] is in the beam + DAQVals[1] + DAQVals[2] + DAQVals[3]
deriv_intensity = np.diff(intensity)
maxDeriv = max(deriv_intensity)
posStartcollect = iDebutImage[0]
posEndcollect = iFinImage[-1]
iAlongCollect = intensity[posStartcollect:posEndcollect]
nbrMesureXbpm = np.size(iAlongCollect)
mesurPerImg = nbrMesureXbpm / theoricNbImages
# number of Xbpm record keeping for each image
mesurImgKeep = mesurPerImg * theoricNbImages
# resize array fonction of xbpm record keeping
xbpmVal = np.resize(iAlongCollect, mesurImgKeep)
# one array line per image
iperImgTabl = xbpmVal.reshape(theoricNbImages, mesurPerImg)
# Flux intensity per image
iperImgMeanI = np.mean(iperImgTabl, axis=1)
MeanIperImg = np.mean(iperImgMeanI)
SDiperImg = np.std(iperImgMeanI)
# derived (numerically)
derrI = iperImgMeanI[1:] - iperImgMeanI[:1]
moy_diff = np.average(derrI)
SDderI = np.std(derrI)
step_sigmaI = derrI / SDderI
step_absI = np.abs(step_sigmaI)
maxiI = np.amax(step_absI)
ymaxiI = np.amax(step_absI)
xmaxiI = np.argmax(step_absI)
#print (xmaxiI, ymaxiI)
log("intensity difference Max and image number",[ymaxiI, xmaxiI], VERBOSE)

# Normalization step for plotting and easy interpration 
iperImgStandard = (iperImgMeanI - MeanIperImg) / float(SDiperImg) 

# Linear regression of Intensity
imgNbrAxis= np.arange(1, theoricNbImages+1)

# Fitting :
frame_nmbr = tabl[:,0][-1]
if NUMBER_POINT_4FIT :
    ech_f = NUMBER_POINT_4FIT/oscilation
else :
    ech_f = 10/oscilation

# Randomisation of Xp
if RANDOM :
    pointNbr = int(frame_nmbr // ech_f)
    Xp = np.random.choice(tabl[:,0], size = pointNbr, replace = False)
    Xcol = tabl[:,0]
    nb = 0     
    Yp = tabl[:,2]    
    Ypt = np.array([])

    for value in (Xp):
        #print value
        Ypt = np.append(Ypt, Yp[value-1])    
    Yp = Ypt 
    Xp = Xp*2*pi/1800
     
else :    
    Xp = tabl[::ech_f,0]*2*pi/angleImage # sampling of X each exh_f frames and converted
    Yp = tabl[::ech_f,2] # sampling of Y each ech_f frames

# in angle
Xp2 = np.append((X[-1]),(X[0]))
Xpfin = np.append((Xp), (Xp2))
Yp2 = np.append((Y[-1]), (Y[-0]))
Ypfin = np.append((Yp), (Yp2))
ech_plt = 10 # sampling value for X value
Xnew = Xpfin[::ech_plt] # Xnew : X sampled each 10 frames
Xnew_last_indice = Xnew.searchsorted(Xpfin[-2])

if CUBIC :
    cspl = interpolate.interp1d(Xp, Yp, kind='cubic')
else :
    cspl = interpolate.UnivariateSpline(Xpfin, Ypfin, k = 2, s = 0)
    coef = interpolate.UnivariateSpline.get_coeffs(cspl)

err =  Y - cspl(X)

# figure 2
pp.clf() #clear the figure
pp.plot(180*X/pi, err)
pp.plot(180*X/pi, Y)
pp.plot(180*Xpfin/pi, Ypfin, 'o')
pp.plot(180*X/pi, cspl(X), 'k--')
pp.xlabel('Angle in deg')
pp.legend(['residual', 'data to fit', 'point use 4 fit', 'fitting curve'], loc='best')
pp.savefig(os.path.join(resultFile,'ErrorSpline.png'), dpi=150, facecolor='w',
edgecolor='w', orientation='landscape')
pp.figure()
#pp.show()

# next step : find the maxi err area
SD = np.std(err)
#print "Mean Error:   %.3e  Std  %.3e" % (np.mean(err), SD)
log("Mean Error and SD", [np.mean(err), SD])
moy_err = np.average(err)

# have to calculate redisual, SD and numeric derived
der1 = err[1:] - err[:1]
moy_err_der = np.average(der1)
SDder = np.std(der1)
step_sigma = der1 / SDder
step_abs = np.abs(step_sigma)
maxi = np.amax(step_abs)
ymaxi = np.amax(step_abs)
xmaxi = np.argmax(step_abs)
log("Maxi scaling correction factor difference and image number", [ymaxi, xmaxi])
#print (xmaxi, ymaxi)

# Normalization step for plotting and easy interpration 
errResidualStandard = (err - moy_err) / float(SD)

# figure 3
# create plot form (data, fit, error between data-fit, max value) .
pp.clf()
fig1 = pp.subplot(211)
pp.plot(np.arange(len(X))*oscilation, tabl[:,2])
pp.xlabel("Angle in deg")
pp.ylabel("Scale correction factor")
pp.plot(np.arange(len(X))*oscilation, cspl(X), '--')
fig2 = pp.subplot(212)
pp.plot(errResidualStandard, label = 'Residual Scale error normalized')
#pp.plot(err/SD, label='Scale exp - Scale calc / SD')
pp.plot(xmaxi, ymaxi, 'ro', label = [xmaxi, 'diff maxi scale'])
pp.xlabel("Image Number")
pp.ylabel("Sigma-level")
# pp.plot(iperImgMean/SDIMean, label = 'Intensity')
pp.plot(iperImgStandard, label = 'Intensity normalized')
pp.plot(xmaxiI, ymaxiI, 'go', label= [xmaxiI,'diff max Intensity'])
leg = pp.legend(bbox_to_anchor=(0., -0.5), numpoints = 1, ncol = 2, loc = 2)
pp.savefig(os.path.join(resultFile,'integrate_scales.png'), dpi=150,
orientation="landscape", bbox_extra_artists=(leg,), bbox_inches='tight')
pp.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
pp.tight_layout()
pp.figure()
#pp.show()

# figure 4
# compare evo xbpm and scale factor
diff_I_scale = iperImgMeanI/SDiperImg - err/SD
#scale vs Intensity
fig3 = pp.subplot(211)
pp.plot(err, iperImgMeanI, 'bo')
pp.ylabel('Intensity')
pp.xlabel('scale correction residual (scale-fit)')
fig4 = pp.subplot(212)
pp.plot(Y , iperImgMeanI, 'ro')
pp.ylabel('Intensity')
pp.xlabel('scale correction factor')
pp.savefig(os.path.join(resultFile,'Cloud_IvsResidualSpline.png'), dpi=150,
facecolor='w', edgecolor='w', orientation='landscape')



# correlation research CoV determination :
covIscale = np.cov(iperImgMeanI, err)
#print covIscale
log("covariance I with Scaling adjustment",covIscale)
# Corelation coef
corelIscal = np.corrcoef(iperImgMeanI, err)
#
if GRAPH :
    pp.show()
else :
    exit(0)
