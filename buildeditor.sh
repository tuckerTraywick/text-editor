#!/bin/sh
clear
echo "---- BUILDING ----"
make clean
make editor
echo ""
echo "---- RUNNING ----"
binary/runeditor
