#!/bin/sh
clear
echo "---- BUILDING ----"
make clean
make keylogger
echo ""
echo "---- RUNNING ----"
binary/runkeylogger
