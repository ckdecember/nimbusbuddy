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
        
        # this will probably be all deprecated
        # we only pull a subset of fields from AWS
        self.vpcKeyList = ['CidrBlock', 'State', 'Tags', 'OwnerId', 'VpcId', 'IsDefault']
        self.vpcExpandedKeyList = ['Tags']

        self.subnetKeyList = ['AvailabilityZone', 'CidrBlock', 'MapPublicIpOnLaunch', 'State', 'SubnetId', 'VpcId', 'OwnerId', 'Tags', 'SubnetArn']
        self.subnetExpandedKeyList = ['Tags']

        self.instanceKeyList = ['InstanceId', 'InstanceType', 'ImageId', 'PrivateIpAddress', 'PublicDnsName', 'SubnetId', 'VpcId', 'Placement', 'Tags', 'SecurityGroups', 'OwnerId', 'State']
        self.instanceExpandedKeyList = ['Tags', 'Placement', 'SecurityGroups']
    
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

    def getSecurityGroups(self):
        return self.ec2client.describe_security_groups()['SecurityGroups']
        
    def getVPCs(self, regionname):
        return self.ec2clientdict[regionname].describe_vpcs()['Vpcs']

    def getSubnets(self, regionname):
        return self.ec2clientdict[regionname].describe_subnets()['Subnets']

    def getInstances(self, regionname):
        return self.ec2clientdict[regionname].describe_instances()['Reservations']
    
    def getProcessedVPCs(self, region):
        vpcslices = self.getVPCs(regionname=region)
        AWSVPCList = []
        for vpcslice in vpcslices:
            vpcDict = self.extractResource(vpcslice, self.vpcKeyList, self.vpcExpandedKeyList)
            AWSVPCinst = AWSVPC(vpcDict)
            AWSVPCList.append(AWSVPCinst)
        return AWSVPCList

    def getProcessedSubnets(self, region):    
        subnetslices = self.getSubnets(regionname=region)
        SubnetList = []
        for subnetslice in subnetslices:
            subnetDict = self.extractResource(subnetslice, self.subnetKeyList, self.subnetExpandedKeyList)
            SubnetInst = AWSSubnet(subnetDict)
            SubnetList.append(SubnetInst)
        return SubnetList
    
    def getProcessedInstances(self, region):
        instanceslices = self.getInstances(regionname=region)
        InstanceList = []
        for instanceslice in instanceslices:
            for instanceInSlice in instanceslice['Instances']:
                if instanceInSlice['State']['Name'] == 'terminated':
                    continue
                instanceDict = self.extractInstance(instanceInSlice, self.instanceKeyList, self.instanceExpandedKeyList)
                InstanceInst = AWSInstances(instanceDict)
                InstanceList.append(InstanceInst)
        return InstanceList

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
        """ Additional Formatting to extract Instance Data """
        resourceDict = {}
        for key in keyList:
            # need to add expansion for certain keys
            if key not in slice:
                continue
            #value could be list, OR dictionary
            if key in expandedKeyList:
                flattenedString = ''
                for sliceitem in slice[key]:
                    # check type for list or dict.
                    if type(sliceitem) is list:
                        for subitem in sliceitem:
                            flattenedString += ' '.join("{}".format(value) for (key, value) in subitem.items() if key != 'Key')
                    elif type(sliceitem) is dict:
                        # flatten any lists into a single string
                        #print (sliceitem)
                        flattenedString += ' '.join("{}".format(value) for (key, value) in sliceitem.items() if key != 'Key') 
                        #print (flattenedString)
                        #print ("into the resource dict {} {}".format(key, flattenedString))
                        resourceDict[key] = flattenedString
                        #print (resourceDict[key])
            else:
                resourceDict[key] = slice[key]
        return resourceDict
    
    def displayAWS(self):
        # client should be up already.
        # or init a crazy structure?
        print ("displayAWS")
        vpcs = self.getVPCs()
        print (vpcs)

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
        self.isDefault = vpcDict['IsDefault']

class AWSVPC2():
    def __init__(self, amazonResourceList):
        """ Keep core dictionary but format some values as needed """

        self.resourceList = amazonResourceList
        self.resourceDictList = []
        #self.keyList = ['CidrBlock', 'State', 'Tags', 'OwnerId', 'VpcId', 'IsDefault']
        self.expandedKeyList = ['Tags']
        self.amazonDefaultTagName = 'Name'

        for amazonResource in self.resourceList:
            resourceDict = {}
            for (key, sublist) in amazonResource.items():
                if key in self.expandedKeyList:
                    # ok these are dicts, or possibly lists of dicts.
                    # value is a sublist.  need to break it down again.
                    for subitem in sublist:
                        # check for missing key
                        if 'Key' in subitem:
                            if subitem['Key'] == self.amazonDefaultTagName:
                                resourceDict[key] = subitem['Value']
                else:
                    resourceDict[key] = amazonResource[key]
            self.resourceDictList.append(resourceDict)
        
        # debugs
        logging.debug("entering resource Dict")
        for resourceDict in self.resourceDictList:
            for (key, value) in resourceDict.items():
                logging.debug((key, value))
        
        



"""
        for key in self.keyList:
            if key in originalDict:
                if key in self.expandedKeyList:
                    for item in originalDict[key]:
                        #resourceDict[]
"""

        #def extractResource(self, slice, keyList, expandedKeyList):
        #resourceDict = {}
        #for key in keyList:
        #    if key in slice:
        #        # some values are actually lists, expand those lists.
        #        if key in expandedKeyList:
        #            for item in slice[key]:
        #                resourceDict[key] = item['Value']
        #        else:
        #            resourceDict[key] = slice[key]
                # instances are handled differently
        #return resourceDict

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
        self.subnetid = subnetDict['SubnetId']
        self.uniqueid = subnetDict['SubnetId']

class AWSInstances():
    def __init__(self, instanceDict):
        #>>> cli.describe_instances()['Reservations'][0]['Instances'][0].keys()
        #['AmiLaunchIndex', 'ImageId', 'InstanceId', 'InstanceType', 'KeyName', 'LaunchTime', 'Monitoring', 'Placement', 'PrivateDnsName', 'PrivateIpAddress', 'ProductCodes', 'PublicDnsName', 'State', 'StateTransitionReason', 'SubnetId', 'VpcId', 'Architecture', 'BlockDeviceMappings', 'ClientToken', 'EbsOptimized', 'EnaSupport', 'Hypervisor', 'NetworkInterfaces', 'RootDeviceName', 'RootDeviceType', 'SecurityGroups', 'SourceDestCheck', 'StateReason', 'Tags', 'VirtualizationType', 'CpuOptions', 'CapacityReservationSpecification', 'HibernationOptions'])

        # ['InstanceId', 'ImageId', 'PrivateIpAddress', 'PublicDnsName', 'SubnetId', 'VpcId', 'Placement', 'Tags', 'SecurityGroups', 'OwnerId', 'State']

        self.instanceid = instanceDict['InstanceId']
        self.imageid = instanceDict['ImageId']
        self.privateipaddress = instanceDict['PrivateIpAddress']
        
        self.publicdnsname = instanceDict['PublicDnsName']
        self.subnetid = instanceDict['SubnetId']

        self.vpcid = instanceDict['VpcId']

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
        
        # maybe find a way to grab the groupid from here and set it.
        if 'SecurityGroups' in instanceDict:
            self.securitygroups = instanceDict['SecurityGroups']
        else:
            self.securitygroups = None

        if 'OwnerId' in instanceDict:
            self.ownerid = instanceDict['OwnerId']
        else:
            self.ownerid = None
        self.state = instanceDict['State']
        self.uniqueid = self.instanceid
    
class AWSSecurityGroups():
    """ Class for AWS Security Groups """
    # securitygroup of Instances contains GroupId which matches GroupId in describe_security_groups()
    # IpPermissions might just be printed out right instead of flattened?  not sure.
    def __init__(self):
        pass

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



def outputTerraform(region, targetRegion, ami):
    """ Dumps a terraform configuration as a main.tf and variables.tf file """
    acb = AWSNimbusBuddy()

    AWSVPCList = acb.getProcessedVPCs(region=region)
    SubnetList = acb.getProcessedSubnets(region=region)
    InstanceList = acb.getProcessedInstances(region=region)
    
    tf = terraformhandler.TerraformHandler(ami)

    tf.setDataList(AWSVPCList, "vpc")
    tf.setDataList(SubnetList, "subnet")
    tf.setDataList(InstanceList, "instance")

    tf.terraformDump(region, targetRegion)

def noop():
    print ("noop")

def howtomerge(region):
    """ skeleton function to merge vpcs and subnets """
    acb = AWSNimbusBuddy()

    AWSVPCList = acb.getProcessedVPCs(region=region)
    SubnetList = acb.getProcessedSubnets(region=region)
    InstanceList = acb.getProcessedInstances(region=region)

    for vpc in AWSVPCList:
        print ("VPC {} {}".format(vpc.vpcid, vpc.tags))
        for subnet in SubnetList:
            if subnet.vpcid == vpc.vpcid:
                print ("Subnet {} {}".format(subnet.subnetid, subnet.tags))
            for instance in InstanceList:
                if (subnet.subnetid == instance.subnetid) and (instance.vpcid == vpc.vpcid):
                    print ("Instance {} {} {} {}".format(instance.instanceid, instance.tags, instance.privateipaddress, instance.securitygroups))

def display(region):
    """ Display Simple Tables of VPCs, Instances, and Subnets """
    print ("display")
    acb = AWSNimbusBuddy()
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
    """ Preps a dictionary list by stripping excessive keys """
    for slice in slices:
        if not allowList:
            dict_variable = {key:value for (key,value) in slice.items() if key not in killlist }
        else:
            dict_variable = {key:value for (key,value) in slice.items() if key in allowList }
        dictList.append(dict_variable)
    return dictList
    #return tabulate.tabulate(dictList, headers='keys')

def testAWSVPC2(region):
    anb = AWSNimbusBuddy()
    originalDict = anb.getVPCs(region)
    vpc2 = AWSVPC2(originalDict)


def main():
    logging.basicConfig(filename='example.log',level=logging.DEBUG)

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
        testAWSVPC2(args.region)
    else:
        noop()

if  __name__ =='__main__': main()

__version__ = '0.2'
__author__ = 'Carroll Kong'