#!/bin/env python
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


import sys
import tables
import numpy 


class ReadLoggingNexus :
    def __init__(self,nomFichierNexus) :  
        print "nomFichierNexus : ", nomFichierNexus
        try :
            self.fichierNexus = tables.openFile(nomFichierNexus)
        except Exception, e:
            raise e
            
        self.racine = self.fichierNexus.root.LoggingOnPX1Collect_00000
        self.nxentryName = 'LoggingOnPX1Collect_00000'
        self.DataBranche = self.racine.scan_data
        
        self.ConvertDate(self.racine.start_time.read()[0])
        print self.racine.start_time.read()                
        
        # Calcul de la transmission par FP 
        # A terme cette valeur sera recuperee du fichier Nexus ( donnees contextuelles, attribut d'un tangoParser)
#        area = self.configLigne['Slit1H_gap'] * self.configLigne['Slit1V_gap']
#        ratioArea = 100* area/0.544
#        TransFP = (-0.0099*(ratioArea**2.0)) + 1.9967 * ratioArea + 0.0357
#        self.configLigne['TransFP'] = TransFP
                            
                         
        
    def get_timeCollect(self) :
        print "get_timeCollect"
        timeCollect = {'debut' : self.ConvertDate(self.racine.start_time.read()[0]),
                       'fin' : self.ConvertDate(self.racine.end_time.read()[0])
                      }

        return timeCollect

    def get_paramsPilatus(self) :
        print "get_paramsPilatus"
        # Recuperation de parametres du Pilatus                                            
        PilatusBranche = self.racine.PROXIMA1.Pilatus
        paramsPilatus = {'TimeReadOut' : PilatusBranche.latency_time.read()/1000.0}       # pour l avoir en s   
#        paramsPilatus = {'TimeReadOut' : 2.3/1000.0}       # pour l avoir en s   
        return paramsPilatus

    def get_paramsDAQ(self) :
        print "get_paramsDAQ"
        paramsDAQ = {'integration_time' :  self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-C04__CA__BAI.1146.1B-DAQ.0__#1','integration_time').read()[0],
                          'sampling_frequency' : self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-C04__CA__BAI.1146.1B-DAQ.0__#1','sampling_frequency').read()[0],
                          'trigger_number' : self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-C04__CA__BAI.1146.1B-DAQ.0__#1','trigger_number').read()[0]
                         }
        return paramsDAQ
    
    def get_paramsLogging(self) :
        print "get_paramsLogging"
        # Recuperation de parametres du logging                                            
        loggingBranche =  self.racine.logging_parameters
        paramsLogging = {'Sampling_Rate' : loggingBranche.sampling_rate.read(), \
                         'Number_of_triggers' : loggingBranche.number_of_triggers.read()}
        return paramsLogging

    def get_timeData(self) :
        print "get_timeData"
        # Generation du tableau en temps fonction du samplingRate du logging 
        paramsLogging = self.get_paramsLogging()      
        timeData = numpy.arange(paramsLogging['Number_of_triggers']) * paramsLogging['Sampling_Rate'] 
        return timeData   

    def get_collectAxisData(self) :       
        print "get_collectAxisData"
        collectAxisData = self.DataBranche.collectAxis.read()[:-1]  # donne en degres        
        return collectAxisData
              
           
    def get_shutterOpenData(self) :
        print "get_shutterOpenData"
        # Probleme connu avec le comptage : Il y a un decalage de 1 indice entre des voies codeurs et des voies Edge
        # Du coup la dimension des tableaux suivants est plus petite de 1 valeur.  
        shutterOpenData = self.DataBranche.shutterOpen.read()[1:]                            # 1 ou 0
        return shutterOpenData 
             
    def get_shutterCloseData(self) :
        print "get_shutterCloseData"
        shutterCloseData = self.DataBranche.shutterClose.read()[1:]                          # 1 ou 0
        return shutterCloseData  

            
#    def get_cmdPilatusExpBeginData(self) :
#        cmdPilatusExpBeginData = self.DataBranche.cmdPilatusExpBegin.read()[1:]              # 1 ou 0
#        return cmdPilatusExpBeginData  
            
#    def get_cmdPilatusExpEndData(self) :
#        cmdPilatusExpEndData = self.DataBranche.cmdPilatusExpEnd.read()[1:]                  # 1 ou 0
#        return cmdPilatusExpEndData      

    def get_statusPilatusExpOffData(self) :
        print "get_statusPilatusExpOffData"
        statusPilatusExpOffData = self.DataBranche.statusPilatusExpOff.read()[1:]            # 1 ou 0
        return statusPilatusExpOffData      

    def get_statusPilatusExpOnData(self) :
        print "get_statusPilatusExpOnData"
        statusPilatusExpOnData = self.DataBranche.statusPilatusExpOn.read()[1:]              # 1 ou 0
        return statusPilatusExpOnData   

                             
    def get_paramsCollect(self) :
        print "get_paramsCollect"
        # Recuperation des parametres de la collecte
        collectBranche = self.racine.collect_parameters
        paramsCollect = {'Collect_Axis': collectBranche.collect_axis.read(), \
                              'Exposure_Period' : collectBranche.exposure_period.read(), \
                              'Image_Width' : collectBranche.image_width.read(), \
                              'Number_of_Images' : int(collectBranche.number_of_images.read()), \
                              'Start_Angle' : collectBranche.start_angle.read(), \
#                              'Trigger_Mode' : int(collectBranche.trigger_mode.read()) }
                              'Trigger_Mode' : 2 }
        return paramsCollect   
    
        
    def get_DAQVals(self) :
        print "get_DAQVals"
        # La premiere valeur dans le tableau est celle apres 1 ms
        print "Lecture DAQCh0"
        DAQCh0 = (self.DataBranche.averagechannel0.read()[:-1]) * 100.0 /10.0
        print "Lecture DAQCh1"
        DAQCh1 = (self.DataBranche.averagechannel1.read()[:-1]) * 100.0 /10.0
        print "Lecture DAQCh2"
        DAQCh2 = (self.DataBranche.averagechannel2.read()[:-1]) * 100.0 /10.0
        print "Lecture DAQCh3"
        DAQCh3 = (self.DataBranche.averagechannel3.read()[:-1]) * 100.0 /10.0
        print "Lecture DAQCh termines"
        DAQVals = numpy.array([DAQCh0,DAQCh1,DAQCh2,DAQCh3])
        return DAQVals

    def get_configLigne(self) :
        print "get_configLigne"
        # Recuperation de la config de la ligne
        # Ici nous sommes oblige de passer par getNode car les noms de groupe ne sont pas compatibles Python a cause des . et du #
        # Pour l instant on ne recupere que les equipements susceptibles d etre differents d une collecte a l autre
        nameConfigLigneBranche =  '/' + self.nxentryName + '/PROXIMA1/'   
        configLigne = {'GapOndulator' : self.fichierNexus.getNode(nameConfigLigneBranche + 'U20','gap').read()[0],
                            'Encoder2Ondulator' : self.fichierNexus.getNode(nameConfigLigneBranche + 'U20','position_encoder2').read()[0],
                            'Slit1H_gap': self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-C01__EX__FENT_H.1__#1','gap').read()[0],
                            'Slit1V_gap': self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-C01__EX__FENT_V.1__#1','gap').read()[0],
                            'Energy': self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-C02__OP__MONO1__#1','energy').read()[0],
                             'ATT' : self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-C04__EX__ATT.1__#1','applied_transmissions').read()[0],
                            'Kappa' : self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-CX1__EX__KAPPA__#1','raw_value').read()[0],
                            'Omega' : self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-CX1__EX__OMEGA__#1','raw_value').read()[0],
                            'Phi' : self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-CX1__EX__PHI__#1','raw_value').read()[0],
                            'DetDistance' : self.fichierNexus.getNode(nameConfigLigneBranche + 'I10-C-CX1__DT__DTC_Se.1-MT_Ts__#1','raw_value').read()[0],
                            'TransFP' : self.fichierNexus.getNode(nameConfigLigneBranche + 'primary_slits','computed_transmission').read()[0]
                            }
        return configLigne   
        
    def get_archValues(self) :
        print "get_archValues"
        # Recuperation des donnes monitorees
        # Ici nous sommes oblige de passer par getNode car les noms de groupe ne sont pas compatibles Python a cause des .
        nameArchValuesBranche =  '/' + self.nxentryName + '/'
#        self.archValues = None
# A chaque cle : on recupere le spectre des donnees archivees de chaque attribut, la tolerance admise sur le sigma,XBPMtype
        self.archValues = { 'SDCAngleX': ['ANS-C10_DG_CALC-SDC-POSITION-ANGLE_angleX',0.2,False],
                            'SDCAngleZ' : ['ANS-C10_DG_CALC-SDC-POSITION-ANGLE_angleZ',0.2,False],
                            'SDCPosX' : ['ANS-C10_DG_CALC-SDC-POSITION-ANGLE_positionX',0.2,False],
                            'SDCPosZ' : ['ANS-C10_DG_CALC-SDC-POSITION-ANGLE_positionZ',0.2,False],
                            'CurrentMachine' : ['ANS_CA_MACHINESTATUS_current',1.5,True],
                            'XBPM1_X' : ['I10-C-C02_DT_XBPM_DIODE.1_horizontalPosition',0.01,True],
                            'XBPM1_I' : ['I10-C-C02_DT_XBPM_DIODE.1_intensity',0.01,True],
                            'XBPM1_Z' : ['I10-C-C02_DT_XBPM_DIODE.1_verticalPosition',0.01,True],
                            'TempMonoOut' : ['I10-C-C02_EX_LASH.1_temperature5',0.2,False],
                            'TempMonoIn' : ['I10-C-C02_OP_MONO1-PT100.1_temperature',0.2,False],
                            'TempMonoIn' : ['I10-C-C02_OP_MONO1-PT100.1_temperature',0.2,False],
                            'XBPM2_X' : ['I10-C-C03_DT_XBPM_DIODE.2_horizontalPosition',0.01,True],
                            'XBPM2_I' : ['I10-C-C03_DT_XBPM_DIODE.2_intensity',0.01,True],
                            'XBPM2_Z' : ['I10-C-C03_DT_XBPM_DIODE.2_verticalPosition',0.01,True],
                            'XBPM3_X' : ['I10-C-C04_DT_XBPM_DIODE.3_horizontalPosition',0.01,True],
                            'XBPM3_I' : ['I10-C-C04_DT_XBPM_DIODE.3_intensity',0.01,True],
                            'XBPM3_Z' : ['I10-C-C04_DT_XBPM_DIODE.3_verticalPosition',0.01,True],
                            'XBPM4_X' : ['I10-C-C04_DT_XBPM_DIODE.4_horizontalPosition',0.01,True],
                            'XBPM4_I' : ['I10-C-C04_DT_XBPM_DIODE.4_intensity',0.01,True],
                            'XBPM4_Z' : ['I10-C-C04_DT_XBPM_DIODE.4_verticalPosition',0.01,True],
                            'TempHutchKB' :['I10-C-C04_VI_TC.1_temperature',0.2,False],
                            'TempHutchGonio' :['I10-C-CX1_VI_TC.1_temperature',0.2,False],
                            'TDLXBPM1_X' : ['TDL-I10-C_DG_XBPM.1_xPos',0.01,False],
                            'TDLXBPM1_Z' : ['TDL-I10-C_DG_XBPM.1_zPos',0.01,False],
                            'TDLXBPM2_X' : ['TDL-I10-C_DG_XBPM.2_xPos',0.01,False],
                            'TDLXBPM2_Z' : ['TDL-I10-C_DG_XBPM.2_zPos',0.01,False],
                            'HEmittance' : ['ANS_CA_MACHINESTATUS_hEmittance',1.0,False],
                            'VEmittance' : ['ANS_CA_MACHINESTATUS_vEmittance',1.0,False],
                            'TempFCSonde4':['ANS-C10_FC_PT100.1_BOI.1_sonde4',0.2,False],
                            'TempFCSonde5' : ['ANS-C10_FC_PT100.1_BOI.1_sonde4',0.2,False],
                            'TempGTCMT022' : ['ANS-C10_GTC_MT022_temperature',0.2,False]
#                            'XBPM5_I' : [self.fichierNexus.getNode(nameArchValuesBranche + 'I10-C-C04_DT_XBPM_DIODE.5_intensity','value').read(),0.005,False]
                            } 
        for key in self.archValues.keys() :
            try :
                self.archValues[key].append(self.fichierNexus.getNode(nameArchValuesBranche + self.archValues[key][0],'value').read())   
            except Exception, e :
                print e
                print "Erreur sur lecture sur " + self.archValues[key][0]
                self.archValues[key].append([])
#                raise e 

        if self.archValues :
            return self.archValues
        else :
            print self.msgerror
            
    def ConvertDate(self,dateNexus) :
        dateSplitte = dateNexus.split('T')
        jourUS = dateSplitte[0].replace('-','/') + ' '
        jourSplitte = jourUS.split('/')
        jourFR = jourSplitte[2] + '/' + jourSplitte[1] + '/' + jourSplitte[0] + ' '
        heure = dateSplitte[1][0:8]
        return {'US' : jourUS +  heure, 'FR' : jourFR + heure}
                                
if __name__ == "__main__" :
    # lecture du nom du fichier en ligne de commande
    if len(sys.argv) > 0 :
        fichierNom = sys.argv[1]
    else :
        print 'no filename argument : ', fichierNom
        exit(0)  
 
    fichierNexus =  ReadLoggingNexus(fichierNom)
    print fichierNexus.get_timeCollect()
#    print fichierNexus.get_timeCollect()['fin'] - fichierNexus.get_timeCollect()['debut']
#    print fichierNexus.get_configLigne()
    archValues = fichierNexus.get_archValues()
    print archValues
#    if archValues :
#        for key in archValues.keys() :
#            print '%15s\tmean = %5.3f\tsigma = %5.3f' %(key,archValues[key].mean(),archValues[key].std())

    print fichierNexus.get_collectAxisData()

    print fichierNexus.get_configLigne()




