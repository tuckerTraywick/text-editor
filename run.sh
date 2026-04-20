set -e
clear
make clean

echo "---- BUILDING SOURCE ----"
make build/run

echo -e "\n---- BUILDING TESTS ----"
make build/test

echo -e "\n---- RUNNING TESTS ----"
build/test

echo -e "\n---- RUNNING SOURCE ----"
build/run
