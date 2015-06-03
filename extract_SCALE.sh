#!/bin/bash
#"""Copyright (c) 2014, Nicolas Foos
#All rights reserved.

#Redistribution and use in source and binary forms, with or without modification, 
#are permitted provided that the following conditions are met:
#1. Redistributions of source code must retain the above copyright notice, this
#list of conditions and the following disclaimer.

#2. Redistributions in binary form must reproduce the above copyright notice,
#this list of conditions and the following disclaimer in the documentation and/
#or other materials provided with the distribution.

#3. Neither the name of the copyright holder nor the names of its contributors 
#may be used to endorse or promote products derived from this software without 
#specific prior written permission.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
#ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
#LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
#CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
#SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
#INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
#CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
#ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
#POSSIBILITY OF SUCH DAMAGE."""
#create working directory
test ! -d analyse_$1 && mkdir analyse_$1 
#extract column and frame number and for each : correction factor for Scale in INTEGREATE.LP
echo "run with" $1
prefix='$1'
egrep " .....   0 ...... ........   ..  .....    ....   ...  ......  ......" $1 > analyse_$1/frames.scales
#ploter les donnees et les garder en png
cd analyse_$1
gnuplot<<EOF
set term png
set grid
set title "SCALE"
set out 'scale.png'
plot "frames.scales" using 1:3
set title "Diverg"
set out 'divergence.png' 
plot "frames.scales" using 1:9
set title "Mos."
set out 'mosaicity.png' 
plot "frames.scales" using 1:10
EOF
sort  -k 3 frames.scales > frames.scales.sort
min=$(head -1 frames.scales.sort  | awk '{print $3}')
max=$(tail -1 frames.scales.sort  | awk '{print $3}')
#plot data and show interactivs figs.
echo "Scales min: " $min  "  max:  " $max
display *.png
