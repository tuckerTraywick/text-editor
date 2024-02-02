#!/bin/sh
clear
echo "---- BUILDING ----"
make clean
make
echo ""
echo "---- RUNNING ----"
binary/run
