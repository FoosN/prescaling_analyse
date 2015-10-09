#!/bin/bash

#i=0
#if -d sftools_$i; then let $[i=$i+=]1;fi
#if "$3"=""; then echo "No name for logfile";fi
sftools<<EOF | tee sftools_$3.log
READ
"$1"
READ
"$2"
CHECKHKL
CORREL
COLUMN 4 10
#PLOT COL 3 VERSUS RESOL
STOP
y
EOF
