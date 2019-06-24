"""
Core control module for nimbus buddy

"""

import argparse
import logging
import unittest

import boto3
import botocore
import texttable
import tabulate

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
    
class AWSNimbusBuddy():
    """ Hey I'm a NimbusBuddy """
    def __init__(self):
        # base client for basic get operations
        self.ec2client = boto3.client('ec2')

        # dictionary of ec2 clients for all regions to easily view other regions as needed.
        regionList = self.getAllRegions()
        self.ec2clientdict = self.initRegionList(regionList)
        
    def getAllRegions(self):
        fullregionlist = self.ec2client.describe_regions()
        regionlist = [i['RegionName'] for i in fullregionlist['Regions']]
        return regionlist

    def initRegionList(self, regionList):
        clientDict = {}
        for region in regionList:
            clientDict[region] = boto3.client('ec2', region_name=region)
        return clientDict

    def viewAllRegionInstances(self):
        regionList = self.getAllRegions()
        for region in regionList:
            logger.debug(region)
            instances = self.getInstances(region)
            for reservation in instances['Reservations']:
                for reservedInstance in reservation['Instances']:
                    instancekeyList = ['InstanceId', 'Subnet', 'KeyName', 
                        'State', 'SecurityGroups', 'Placement', 'Tags']
                    for instancekey in instancekeyList:
                        if instancekey in reservedInstance:
                            logger.debug("{} {}".format(instancekey, reservedInstance[instancekey]))

    def getSecurityGroups(self, regionname):
        return self.ec2clientdict[regionname].describe_security_groups()['SecurityGroups']
        
    def getVPCs(self, regionname):
        return self.ec2clientdict[regionname].describe_vpcs()['Vpcs']

    def getSubnets(self, regionname):
        return self.ec2clientdict[regionname].describe_subnets()['Subnets']

    def getInstances(self, regionname):
        # not sure when there are multiple reservations
        return self.ec2clientdict[regionname].describe_instances()['Reservations'][0]['Instances']
    
class AWSResource():
    def __init__(self, amazonResourceList, resourceType):
        """ Keep core dictionary but format some values as needed """

        self.resourceType = resourceType
        self.resourceList = amazonResourceList
        self.resourceDictList = []
        self.expandedKeyList = ['Tags']
        self.amazonDefaultTagName = 'Name'

        for amazonResource in self.resourceList:
            resourceDict = {}
            for (key, sublist) in amazonResource.items():
                if key in self.expandedKeyList:
                    # ok these are dicts, or possibly lists of dicts.
                    # value is a sublist.  need to break it down again.
                    for subitem in sublist:
                        if 'Key' in subitem:
                            if subitem['Key'] == self.amazonDefaultTagName:
                                resourceDict[key] = subitem['Value']
                else:
                    resourceDict[key] = amazonResource[key]
            self.resourceDictList.append(resourceDict)

        logger.debug("entering resource Dict")
        for resourceDict in self.resourceDictList:
            logger.debug("###")
            for (key, value) in resourceDict.items():
                logger.debug((key, value))
            logger.debug("###")

class TestNimbusBuddy(unittest.TestCase):
    """ Basic Unit Test for boto3 / ec2 instantiation"""
    def test_aws(self):
        client = boto3.client('ec2')
        isinstance(client, type(boto3.client))

    #def test_aws_regions(self):
    #    client = boto3.client('ec2')
    #    isinstance(client.describe_regions(),type(list))

    #def test_aws_region(self):
    #    regionTest = 'us-east-1'
    #    client = boto3.client('ec2', region_name=regionTest)
    #    session = boto3.session.Session()
    #    region = session.region_name
    #    self.assertEquals(region, regionTest)

# prob should test each function
# display
# merge
# terraform

def outputTerraform(region, targetRegion, ami):
    """ Dumps a terraform configuration as a main.tf and variables.tf file """
    anb = AWSNimbusBuddy()
    VPCList = anb.getVPCs(regionname=region)
    vpcs2 = AWSResource(VPCList, 'vpc')

    SubnetList = anb.getSubnets(regionname=region)
    InstanceList = anb.getInstances(regionname=region)

    subnets2 = AWSResource(SubnetList, 'subnet')
    inst2 = AWSResource(InstanceList, 'instance')

    # should refactor this?
    
    tf = terraformhandler.TerraformHandler(ami)

    tf.setDataList(vpcs2.resourceDictList, vpcs2.resourceType)
    tf.setDataList(subnets2.resourceDictList, subnets2.resourceType)
    tf.setDataList(inst2.resourceDictList, inst2.resourceType)

    tf.terraformDump(region, targetRegion)

def display(region):
    """ Display Simple Tables of VPCs, Instances, and Subnets """
    anb = AWSNimbusBuddy()
    vpcsuperlist = anb.getVPCs(regionname=region)

    


    print (tabulate.tabulate(vpcsuperlist, headers='keys'))
    
def testSecurityGroup(region):
    anb = AWSNimbusBuddy()
    sglist = anb.getSecurityGroups(regionname=region)
    SG = AWSResource(sglist, 'securitygroup')


def main():
    parser = argparse.ArgumentParser(description="Cloud Visualization and Backup Tool")
    parser.add_argument('command', help='Action')

    parser.add_argument('--region')
    parser.add_argument('--targetregion')
    parser.add_argument('--ami')

    args = parser.parse_args()

    #make region a requirement for some?

    if args.command == 'display':
        print (args.region)
        # maybe check if region is valid
        if args.region:
            display(region=args.region)
        else:
            display()
    elif args.command == 'terraform':
        ami = None
        if args.ami:
            ami = args.ami

        if args.region and args.targetregion:
            outputTerraform(args.region, args.targetregion, ami)
        elif args.region:
            print ('no target region set, defaulting to region = targetregion')
            outputTerraform(args.region, args.region, ami)
        else:
            print ('need args')
    elif args.command == 'merge':
        howtomerge(args.region)
    elif args.command == 'test':
        testSecurityGroup(args.region)
    else:
        noop()

if  __name__ =='__main__': main()

__version__ = '0.3'
__author__ = 'Carroll Kong'