#!/bin/bash

rm provided_code/data/*
cp data/questions.json provided_code/data
cd provided_code
rm stanford-parser/questions/*
rm stanford-parser/parses/*
sed -i 's/25000m/2000m/g' run.sh
make clean
make
./run.sh Question
cd stanford-parser
./runparserfull.sh
mv question*.xml parses
cd ../../
cp -r provided_code/stanford-parser/parses ./
