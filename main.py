"""
Core control module for nimbus buddy

"""

import argparse
import logging
import unittest

import nimbusdisplay
import terraformhandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)
logger.addHandler(ch)

# this will inherit aws cloud buddy OR we will use a function pointer
class NimbusBuddy:
    def __init__(self):
        pass

def main():
    parser = argparse.ArgumentParser(description="Cloud Visualization and Backup Tool")
    parser.add_argument('command', help='valid commands: display, terraform')

    parser.add_argument('region', help="Current working AWS Region e.g.  us-west-1")
    parser.add_argument('--targetregion', help="Destination AWS Region for migration")
    parser.add_argument('--ami', help="Override AMI codes for region to region migration in terraform")

    args = parser.parse_args()

    nd = nimbusdisplay.Display(args.region)

    if args.command == 'display':
        nd.display()
    elif args.command == 'terraform':
        ami = None
        if args.ami:
            ami = args.ami
        if args.region and args.targetregion:
            tf = terraformhandler.TerraformHandler(args.region, args.targetregion, ami)
            tf.terraformDump()
        elif args.region:
            print ('no target region set, defaulting to region = targetregion')
            tf = terraformhandler.TerraformHandler(args.region, args.region, ami)
            tf.terraformDump()
        else:
            print ('need args')
    elif args.command == 'test':
        nd.VPCandSubnets()

if  __name__ =='__main__':
    main()

def test_displayarg(self):
    pass

__version__ = '0.4'
__author__ = 'Carroll Kong'