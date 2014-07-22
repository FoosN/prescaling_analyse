#!/bin/bash

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
