#!/bin/sh
# should check paths, etc
python3 -m unittest main.py 
python3 -m unittest aws.py 
python3 -m unittest utils.py 
python3 -m unittest nimbusdisplay.py 
python3 -m unittest terraformhandler.py 
