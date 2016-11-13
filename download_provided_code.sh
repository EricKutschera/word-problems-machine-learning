#!/bin/bash

wget http://groups.csail.mit.edu/rbg/code/wordprobs/wordprobs.tar.gz
mkdir provided_code
mv wordprobs.tar.gz provided_code
cd provided_code
tar -xzf wordprobs.tar.gz
rm wordprobs.tar.gz
mv wordprobs/* ./
cd ..
mkdir data
cp provided_code/data/questions.json ./data
