"""
Core control module for cloudbuddy

"""

import argparse
import unittest

import boto3
import botocore
import texttable
import tabulate

import terraformhandler

# this will inherit aws cloud buddy OR we will use a function pointer
class CloudBuddy:
    def __init__(self):
        pass
    
class AWSCloudBuddy():
    def __init__(self):
        self.ec2client = boto3.client('ec2', region_name = 'us-east-2')
        self.ec2clientdict = {}
        self.dataStruct = {}
        
        regionList = self.getAllRegions()
        
        self.initRegionList(regionList)

        #self.iamclient = boto3.client('iam')
        
        # we only pull a subset of fields from AWS
        self.vpcKeyList = ['CidrBlock', 'State', 'Tags', 'OwnerId', 'VpcId']
        self.vpcExpandedKeyList = ['Tags']

        self.subnetKeyList = ['AvailabilityZone', 'CidrBlock', 'MapPublicIpOnLaunch', 'State', 'SubnetId', 'VpcId', 'OwnerId', 'Tags', 'SubnetArn']
        self.subnetExpandedKeyList = ['Tags']

        self.instanceKeyList = ['InstanceId', 'InstanceType', 'ImageId', 'PrivateIpAddress', 'PublicDnsName', 'SubnetId', 'Placement', 'Tags', 'SecurityGroups', 'OwnerId', 'State']
        self.instanceExpandedKeyList = ['Tags', 'Placement', 'SecurityGroups']
    
    def getSecurityGroups(self):
        return self.ec2client.describe_security_groups()
        
    def getAllRegions(self):
        fullregionlist = self.ec2client.describe_regions()
        regionlist = [i['RegionName'] for i in fullregionlist['Regions']]
        return regionlist

    def initRegionList(self, regionList):
        for region in regionList:
            self.ec2clientdict[region] = boto3.client('ec2', region_name=region)
    
    def cycleRegionInstances(self):
        regionList = self.getAllRegions()
        print ("Start")
        for region in regionList:
            print (region)
            instances = self.getInstances(region)
            for reservation in instances['Reservations']:
                for reservedInstance in reservation['Instances']:
                    #print (reservedInstance)
                    #print (reservedInstance.keys())
                    print ("#####################")
                    instancekeyList = ['InstanceId', 'Subnet', 'KeyName', 
                        'State', 'SecurityGroups', 'Placement', 'Tags']
                    for instancekey in instancekeyList:
                        if instancekey in reservedInstance:
                            print ("{} {}".format(instancekey, reservedInstance[instancekey]))
                    print ("#####################")

    def getVPCs(self, regionname):
        return self.ec2clientdict[regionname].describe_vpcs()['Vpcs']

    def getSubnets(self, regionname):
        return self.ec2clientdict[regionname].describe_subnets()['Subnets']

    def getInstances(self, regionname):
        return self.ec2clientdict[regionname].describe_instances()['Reservations']
    
    def extractResource(self, slice, keyList, expandedKeyList):
        resourceDict = {}
        for key in keyList:
            if key in slice:
                # some values are actually lists, expand those lists.
                if key in expandedKeyList:
                    for item in slice[key]:
                        resourceDict[key] = item['Value']
                else:
                    resourceDict[key] = slice[key]
                # instances are handled differently
        return resourceDict
    
    def extractInstance(self, slice, keyList, expandedKeyList):
        resourceDict = {}
        for key in keyList:
            # need to add expansion for certain keys, maybe just drop 'values' in here.
            if key in slice:
                #value could be list, OR dictionary
                if key in expandedKeyList:
                    flattenedString = ''
                    for sliceitem in slice[key]:
                        # check type for list or dict.
                        if type(sliceitem) is list:
                            for subitem in sliceitem:
                                if key == 'Key':
                                    subitem.pop(key)
                                #flattenedString += ' '.join("{!r}".format(value) for (key, value) in subitem.items())
                                flattenedString += ' '.join("{}".format(value) for (key, value) in subitem.items() if key != 'Key')
                        elif type(sliceitem) is dict:
                            #resourceDict[key] = sliceitem.values()
                            flattenedString += ' '.join("{}".format(value) for (key, value) in sliceitem.items() if key != 'Key')
                            #print (flattenedString)
                    resourceDict[key] = flattenedString
                else:
                    resourceDict[key] = slice[key]
        return resourceDict
    
    def displayAWS(self):
        # client should be up already.
        # or init a crazy structure?
        print ("displayAWS")
        vpcs = self.getVPCs()
        print (vpcs)
        pass

class AWSVPC():
    def __init__(self, vpcDict):
        #['CidrBlock', 'State', 'Tags', 'OwnerId', 'VpcId']
        #['Tags']
        self.vpcid = vpcDict['VpcId']
        self.cidrblock = vpcDict['CidrBlock']
        self.state = vpcDict['State']
        if 'Tags' in vpcDict:
            self.tags = vpcDict['Tags']
        else:
            self.tags = None
        self.ownerid = vpcDict['OwnerId']
        self.uniqueid = vpcDict['VpcId']

class AWSSubnet():
    def __init__(self, subnetDict):
        #['AvailabilityZone', 'CidrBlock', 'MapPublicIpOnLaunch', 'State', 'SubnetId', 'VpcId', 'OwnerId', 'Tags', 'SubnetArn']
        self.vpcid = subnetDict['VpcId']
        self.cidrblock = subnetDict['CidrBlock']
        self.state = subnetDict['State']
        if 'Tags' in subnetDict:
            self.tags = subnetDict['Tags']
        else:
            self.tags = None
        self.ownerid = subnetDict['OwnerId']
        self.availabilityzone = subnetDict['AvailabilityZone']
        self.mappubliciponlaunch = subnetDict['MapPublicIpOnLaunch']
        self.subnetarn = subnetDict['SubnetArn']
        self.uniqueid = subnetDict['SubnetId']

class AWSInstances():
    def __init__(self, instanceDict):
        #>>> cli.describe_instances()['Reservations'][0]['Instances'][0].keys()
        #['AmiLaunchIndex', 'ImageId', 'InstanceId', 'InstanceType', 'KeyName', 'LaunchTime', 'Monitoring', 'Placement', 'PrivateDnsName', 'PrivateIpAddress', 'ProductCodes', 'PublicDnsName', 'State', 'StateTransitionReason', 'SubnetId', 'VpcId', 'Architecture', 'BlockDeviceMappings', 'ClientToken', 'EbsOptimized', 'EnaSupport', 'Hypervisor', 'NetworkInterfaces', 'RootDeviceName', 'RootDeviceType', 'SecurityGroups', 'SourceDestCheck', 'StateReason', 'Tags', 'VirtualizationType', 'CpuOptions', 'CapacityReservationSpecification', 'HibernationOptions'])

        # ['InstanceId', 'ImageId', 'PrivateIpAddress', 'PublicDnsName', 'SubnetId', 'Placement', 'Tags', 'SecurityGroups', 'OwnerId', 'State']

        self.instanceid = instanceDict['InstanceId']
        self.imageid = instanceDict['ImageId']
        self.privateipaddress = instanceDict['PrivateIpAddress']

        
        self.publicdnsname = instanceDict['PublicDnsName']
        self.subnetid = instanceDict['SubnetId']

        if 'InstanceType' in instanceDict:
            self.instancetype = instanceDict['InstanceType']
        else:
            self.instancetype = None

        if 'Placement' in instanceDict:
            self.placement = instanceDict['Placement']
        else:
            self.placement = None
        if 'Tags' in instanceDict:
            self.tags = instanceDict['Tags']
        else:
            self.tags = None
        if 'SecurityGroups' in instanceDict['SecurityGroups']:
            self.securitygroups = instanceDict['SecurityGroups']
        else:
            self.securitygroups = None

        if 'OwnerId' in instanceDict:
            self.ownerid = instanceDict['OwnerId']
        else:
            self.ownerid = None
        self.state = instanceDict['State']
        self.uniqueid = self.instanceid

class TestCloudBuddy(unittest.TestCase):
    def test_aws(self):
        client = boto3.client('ec2')
        isinstance(client, type(boto3.client))

    #def test_aws_regions(self):
    #    client = boto3.client('ec2')
    #    isinstance(client.describe_regions(),type(list))

def outputTerraform(region, targetRegion):
    acb = AWSCloudBuddy()
    #acb.cycleRegionInstances()
    vpcslices = acb.getVPCs(regionname=region)
    AWSVPCList = []

    subnetslices = acb.getSubnets(regionname=region)
    #print (subnetslices)
    SubnetList = []

    instanceslices = acb.getInstances(regionname=region)
    #print (instanceslices)
    InstanceList = []
    #['Instances']
    
    for vpcslice in vpcslices:
        #vpcDict = acb.extractVPC(vpcslice)
        vpcDict = acb.extractResource(vpcslice, acb.vpcKeyList, acb.vpcExpandedKeyList)
        AWSVPCinst = AWSVPC(vpcDict)
        AWSVPCList.append(AWSVPCinst)
    
    for subnetslice in subnetslices:
        subnetDict = acb.extractResource(subnetslice, acb.subnetKeyList, acb.subnetExpandedKeyList)
        SubnetInst = AWSSubnet(subnetDict)
        SubnetList.append(SubnetInst)

    for instanceslice in instanceslices:
        #print (instanceslice)
        #print (instanceslice['Instances'][0])
        # instances are handled differently
        #instanceDict = acb.extractResource(instanceslice['Instances'][0], acb.instanceKeyList, acb.instanceExpandedKeyList)
        for instanceInSlice in instanceslice['Instances']:
            if instanceInSlice['State']['Name'] == 'terminated':
                continue
            instanceDict = acb.extractInstance(instanceInSlice, acb.instanceKeyList, acb.instanceExpandedKeyList)
            print ("instance dict")
            print (instanceDict)
            InstanceInst = AWSInstances(instanceDict)
            InstanceList.append(InstanceInst)
    
    tf = terraformhandler.TerraformHandler()
    tf.setDataList(AWSVPCList, "vpc")
    tf.setDataList(SubnetList, "subnet")
    tf.setDataList(InstanceList, "instance")

    tf.terraformDump(region, targetRegion)

def noop():
    print ("noop")

def howtomerge(region):
    # get vpcs first
    acb = AWSCloudBuddy()
    #acb.cycleRegionInstances()
    vpcslices = acb.getVPCs(regionname=region)
    subnetslices = acb.getSubnets(regionname=region)

    #list of dicts
    # maybe pull individual vpcids
    # filter subnets by individual vpcsids
    #for subnetslice in subnetslices:
    #    dictfiltered = {key: value for key, value in subnetslice.items() if key in ['VpcId', 'SubnetId']}
    #    dictfiltered = {key: value for key, value in dictfiltered.items() if 'vpc-850c16ed' in value}
    #    print (dictfiltered)

    #vpc-850c16ed

    # variable vpcid

    vpcid = "vpc-850c16ed"
    #vpcid = "vpc-0cfd1cd66295ae2e5"
    test = [item for item in subnetslices if item["VpcId"] == vpcid]
#    print ("test with {}".format(vpcid))

    
 #   for i in test:
 #       print (i['SubnetId'])
    


# but need to MERGE it into sensible views
# define VIEWS
# Subnets join on vpcid INSIDE VPCs AND INTERNET GATEWAYS
# EC2s join on subnets.  subnets know v pcids.(check internet gateway)
# EC2s SecurityGroups know... instanceids???
# i wonder if using an sql db would work better here??? 

def display(region):
    print ("display")
    acb = AWSCloudBuddy()
    # filter dictionaries with dict comprehension
    killlist = ['DhcpOptionsId', 'InstanceTenancy', 'CidrBlockAssociationSet', 'Tags']
    
    dictList = []
    slices = acb.getVPCs(regionname=region)
    table = sliceDisplay(dictList, slices, region, killlist)
    #print (table)

    dictList = []
    slices = acb.getSubnets(regionname=region)
    table = sliceDisplay(dictList, slices, region, killlist)
    #print (table)

    dictList = []
    slices = acb.getInstances(regionname=region)
    # iterate slices.
    
    table = []
    for slice in slices:
        allowList = ['ImageId', 'InstanceId', 'InstanceType', 'PrivateDnsName', 'PrivateIpAddress', 'PublicDnsName', 'State', 'SubnetId', 'VpcId', 'VirtualizationType', 'CpuOptions']
        table = sliceDisplay(dictList, slice['Instances'], region, killlist, allowList)

    print (tabulate.tabulate(table, headers='keys'))
    
def sliceDisplay(dictList, slices, regionname, killlist, allowList=[]):
    #dictList = []
    for slice in slices:
        if not allowList:
            dict_variable = {key:value for (key,value) in slice.items() if key not in killlist }
        else:
            dict_variable = {key:value for (key,value) in slice.items() if key in allowList }
        dictList.append(dict_variable)
    return dictList
    #return tabulate.tabulate(dictList, headers='keys')

def main():
    parser = argparse.ArgumentParser(description="Cloud Visualization and Backup Tool")
    parser.add_argument('command', help='Action')

    parser.add_argument('--region')
    parser.add_argument('--targetregion')

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
        if args.region and args.targetregion:
            outputTerraform(args.region, args.targetregion)
        elif args.region:
            print ('no target region set, defaulting to region = targetregion')
            outputTerraform(args.region, args.region)
        else:
            print ('need args')
    elif args.command == 'merge':
        howtomerge(args.region)
    else:
        noop()

if  __name__ =='__main__': main()

__version__ = '0.2'
__author__ = 'Carroll Kong'