#!/bin/bash
rm -rf venv
virtualenv2 venv
source venv/bin/activate

pip install sympy
pip install scipy
pip install numpy
