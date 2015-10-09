#!/usr/bin/python2.7
# -*-coding:Utf-8 -*

"""
Copyright (c) 2014, Nicolas Foos
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

"""Progs to plot table of correlation from SFTOOLS ccp4
and to create a hierarchical clustering of the datasets """
import sys
import os
import numpy as np
import xscale_clusters_pierre as xscale_clust

#to modify at the end of the devpt
sys.path.append("/progs/progsDev/gitRepo/prescaling_analyse")
sys.path.append("/data/bioxsoft/bin")

SFTOOL_EXEC = "sftools<<EOF"

#copied from xupy
#def exec_prog(prog_name, stdinp=None, stdout= None, stderr=None):
#    if not stdout : stdout = " "
#    else: stdout = " > " + stdout
#    if not stdinp : stdinp = " "
#    else: stdinp = " < " + stdinp
#    if not stderr : stderr = " "
#    else: stderr = " 2>" + stderr
#    os.system(prog_name+stdinp+stdout+stderr ) # use popen instead ?
    
    

def exec_sftools(runcommand, fileInp, outputFile):
    #fileInp : must come from xscale or xds output convert in ccp4 mtz
    # or it could be add directrly from commande line as arg.
    fileInp =  #must be text file write before can be create from a dict as XDS.INP in other script
    ouptuFile =
    runcommand = "sftools<sftool.inp."+i+ "|tee sftools_"+"sftools."+i+".log"   
    os.system(runcommand)
    
    
    
def grab_sftools_out(sftoolsLog):
    #ideq : pick multiple sftools output, put them in list,
#from this list, read object (sftools.log) and read line in the sftools.log
#extract table from this file.
    sftoolsLog = []
    
    