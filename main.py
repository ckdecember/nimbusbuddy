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
        """ Initializes a base client for querying AWS and clients for every region """
        # base client for basic get operations
        self.ec2client = boto3.client('ec2')

        # dictionary of ec2 clients for all regions to easily view other regions as needed.
        regionList = self.getAllRegions()
        self.ec2clientdict = self.initRegionList(regionList)
        
    def getAllRegions(self):
        """ List of all the regions in AWS """
        fullregionlist = self.ec2client.describe_regions()
        regionlist = [i['RegionName'] for i in fullregionlist['Regions']]
        return regionlist

    def initRegionList(self, regionList):
        """ initializes the clients for every region """
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
        return self.ec2clientdict[regionname].describe_instances()['Reservations']
    
class AWSResource():
    def __init__(self, amazonResourceList, resourceType):
        """ Keep core dictionary but format some values as needed """

        self.resourceType = resourceType
        self.resourceList = amazonResourceList
        self.resourceDictList = []
        self.expandedKeyList = ['Tags']
        self.amazonDefaultTagName = 'Name'

        # maybe make a separate loop for instances
        if self.resourceType != 'instance':
            for amazonResource in self.resourceList:
                resourceDict = {}
                skipFlag = False
                for (key, sublist) in amazonResource.items():
                    if key in self.expandedKeyList:
                        # ok these are dicts, or possibly lists of dicts.
                        # value is a sublist.  need to break it down again.
                        # how to handle for instance tags?
                        for subitem in sublist:
                            if 'Key' in subitem:
                                if subitem['Key'] == self.amazonDefaultTagName:
                                    resourceDict[key] = subitem['Value']
                    else:
                        resourceDict[key] = amazonResource[key]
                    
                if not skipFlag:
                    self.resourceDictList.append(resourceDict)
        elif self.resourceType == 'instance':
            for amazonResource in self.resourceList:
                # Resource->ReservationList->InstanceList->InstanceData.
                # amazon stores instances in a deeper level than subnets/vpcs
                resourceDict = {}
                skipFlag = False
                for instances in amazonResource['Instances']:
                    logger.debug("this is instances")
                    logger.debug(instances)
                    if instances['State']['Name'] == 'terminated':
                        skipFlag = True
                    for (key, value) in instances.items():
                        # need tag flattener code here.
                        if key == 'Tags':
                            flattenedString = ''
                            # [{'Key': 'Name', 'Value': 'Newinstance'}]
                            for flatitem in value:
                                flattenedString = flatitem['Value']
                            logger.debug("value list")
                            logger.debug(value)
                            resourceDict[key] = flattenedString
                        else:
                            resourceDict[key] = value
                self.resourceDictList.append(resourceDict)
                
        logger.debug("entering resource Dict")
        for resourceDict in self.resourceDictList:
            logger.debug("### type {}".format(resourceType))
            for (key, value) in resourceDict.items():
                logger.debug("{} {}".format(key, value))
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

    tf = terraformhandler.TerraformHandler(ami)

    tf.setDataList(vpcs2.resourceDictList, vpcs2.resourceType)
    tf.setDataList(subnets2.resourceDictList, subnets2.resourceType)
    tf.setDataList(inst2.resourceDictList, inst2.resourceType)

    tf.terraformDump(region, targetRegion)

def display(region):
    """ Display Simple Tables of VPCs, Instances, and Subnets """
    anb = AWSNimbusBuddy()

    print ("Region: {}".format(region))
    
    # could make a super list of dicts, with unified dicts.

    # three sections, maybe turn it into a function later
    # 
    tmpDict = {}
    
    displayList = []
    allowedKeys = ['CidrBlock', 'VpcId', 'IsDefault']
    print (10*"#")
    print ("VPCs")
    print (10*"#")
    vpcsuperlist = anb.getVPCs(regionname=region)
    for vpc in vpcsuperlist:
        trimmedDict = {key: value for (key, value) in vpc.items() if key in allowedKeys}
        displayList.append(trimmedDict)

    print (tabulate.tabulate(displayList, headers='keys'))
    print (2*"\n")

    print (10*"#")
    print ("Subnets")
    print (10*"#")
    displayList = []
    allowedKeys = ['CidrBlock', 'VpcId', 'IsDefault', 'SubnetId']
    subnetsuperlist = anb.getSubnets(regionname=region)
    for subnet in subnetsuperlist:
        trimmedDict = {key: value for (key, value) in subnet.items() if key in allowedKeys}
        displayList.append(trimmedDict)

    print (tabulate.tabulate(displayList, headers='keys'))
    print (2*"\n")

    print (10*"#")
    print ("Instances")
    print (10*"#")
    displayList = []
    allowedKeys = ['CidrBlock', 'VpcId', 'IsDefault', 'SubnetId', 'ImageId', 'InstanceId', 'SecurityGroups', 'State']
    instancesuperlist = anb.getInstances(regionname=region)
    # maybe run it through the main filter?

    for instanceList in instancesuperlist:
        for instance in instanceList['Instances']:
            trimmedDict = {key: value for (key, value) in instance.items() if key in allowedKeys}
            trimmedDict['SecurityGroups'] = flattenDict(trimmedDict['SecurityGroups'], 'GroupId')
            if trimmedDict['State']['Name'] == 'terminated':
                continue
            trimmedDict['State'] = flattenDict(trimmedDict['State'], 'Name')
            displayList.append(trimmedDict)

    print (tabulate.tabulate(displayList, headers='keys'))
    print (2*"\n")

def display2(region):
    logger.debug("display2")
    allowedKeys = ['InstanceId', 'Tags', 'State', 'SecurityGroups']
    # get list of vpcid and subnetid pairs
    
    vpcsubnetpairs = getVPCandSubnetPairs(region)
    logger.debug(vpcsubnetpairs)
    for (vpcid, subnetid) in vpcsubnetpairs:
        # start loop?  generate values.
        vpcid = 'vpc-0b615640807a87ba9'
        subnetid = 'subnet-0f67c0622bc9073dd'

        originalList = instanceView(region, vpcid, subnetid)
        displayList = []

        print ("VPC: {} Subnet: {} ".format(vpcid, subnetid))
        for originalitem in originalList:
            displayitem = {key: value for (key, value) in originalitem.items() if key in allowedKeys}
            if 'Tags' in displayitem:
                displayitem['Tags'] = flattenDict(displayitem['Tags'], 'Value')
            if 'State' in displayitem:
                displayitem['State'] = flattenDict(displayitem['State'], 'Name')
            displayList.append(displayitem)
        print (tabulate.tabulate(displayList, headers='keys'))

def flattenDict(flattenable, flattenKey):
    flatstring = ''
    
    if type(flattenable) == list:
        for tag in flattenable:
            if flattenKey in tag:
                flatstring = tag[flattenKey]
    elif type(flattenable) == dict:
        if flattenKey in flattenable:
            flatstring = flattenable[flattenKey]
    return flatstring

def getVPCandSubnetPairs(region):
    anb = AWSNimbusBuddy()
    vpcsubnetpair = []
    vpcsuperlist = anb.getVPCs(regionname=region)
    subnetsuperlist = anb.getSubnets(regionname=region)

    for vpc in vpcsuperlist:
        for subnet in subnetsuperlist:
            if vpc['VpcId'] == subnet['VpcId']:
                vpcsubnetpair.append((vpc['VpcId'], subnet['SubnetId']))
    return vpcsubnetpair

def instanceSecurityGroups():
    anb = AWSNimbusBuddy()
    securityGroupList = []
    instancesuperlist = anb.getInstances(regionname=region)
    
def instanceView(region, vpcid, subnetid):
    anb = AWSNimbusBuddy()
    displayList = []
    instancesuperlist = anb.getInstances(regionname=region)
    for instanceList in instancesuperlist:
        for instance in instanceList['Instances']:
            if (instance['VpcId'] == vpcid) and (instance['SubnetId'] == subnetid):
                displayList.append(instance)
    return displayList

def stripDictList(dictList, listOfAllowedFields):
    logger.debug("inside strip dict")
    tmpList = []
    for listItem in dictList:
        #logger.debug("list item")
        #logger.debug(listItem)
        tmpDict = {key: value for (key, value) in listItem.items() if key in listOfAllowedFields}
        logger.debug(tmpDict)
        if tmpDict:
            tmpList.append(tmpDict)
    logger.debug(tmpList)
    return tmpList

def testSecurityGroup(region):
    anb = AWSNimbusBuddy()
    sglist = anb.getSecurityGroups(regionname=region)
    SG = AWSResource(sglist, 'securitygroup')
    logger.debug(SG.resourceDictList)

    # if ippermissions is empty, it means no rules.  
    # could be hard to flatten

    ipPermissionsList = stripDictList(SG.resourceDictList, ['IpPermissions'])
    #ipPermissionsList = stripDictList(ipPermissionsList, ['IpProtocol', 'IpRanges'])
    #logger.debug(ipPermissionsList)

    print (tabulate.tabulate(ipPermissionsList, headers="keys"))
        

def noop():
    print("Nothing to be done")

def main():
    parser = argparse.ArgumentParser(description="Cloud Visualization and Backup Tool")
    parser.add_argument('command', help='valid commands: display, terraform')

    parser.add_argument('region', help="Current working AWS Region e.g.  us-west-1")
    parser.add_argument('--targetregion', help="Destination AWS Region for migration")
    parser.add_argument('--ami', help="Override AMI codes for region to region migration in terraform")

    args = parser.parse_args()

    #make region a requirement for some?

    if args.command == 'display':
        print (args.region)
        # maybe check if region is valid
        if args.region:
            display(region=args.region)
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

if  __name__ =='__main__': main()

__version__ = '0.3'
__author__ = 'Carroll Kong'