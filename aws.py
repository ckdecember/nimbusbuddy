import logging
import unittest

import boto3
import botocore

logger = logging.getLogger(__name__)

#logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)
logger.addHandler(ch)

class AWSNimbusBuddy():
    """ Hey I'm a NimbusBuddy """
    def __init__(self, region):
        """ Initializes a base client for querying AWS and clients for every region """
        # base client for basic get operations
        self.ec2client = boto3.client('ec2')

        # dictionary of ec2 clients for all regions to easily view other regions as needed.
        regionList = self.getAllRegions()
        self.ec2clientdict = self.initRegionList(regionList)
        self.region = region
        
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
    
    def getVPCandSubnetPairs(self):
        """ retrieve matching VPC and Subnet Pairs"""
        region = self.region
        vpcsubnetpair = []
        vpcsuperlist = self.getVPCs()
        subnetsuperlist = self.getSubnets()

        for vpc in vpcsuperlist:
            for subnet in subnetsuperlist:
                if vpc['VpcId'] == subnet['VpcId']:
                    # perhaps can add more meta data, or just use the ids here to retrieve data ?
                    #logger.debug(vpc)
                    vpcsubnetpair.append((vpc['VpcId'], vpc['CidrBlock'], subnet['SubnetId'], subnet['CidrBlock']))
        return vpcsubnetpair

    def displayInstanceView(self, vpcid, subnetid):
        """ return a list of dicts suitable for tabulate display """
        displayList = []
        instancesuperlist = self.getInstances()
        for instanceList in instancesuperlist:
            for instance in instanceList['Instances']:
                if (instance['VpcId'] == vpcid) and (instance['SubnetId'] == subnetid):
                    displayList.append(instance)
        return displayList

    def getSecurityGroups(self, groupId):
        """ get All security groups or select the group by groupId """
        regionname = self.region
        sgs = self.ec2clientdict[regionname].describe_security_groups()['SecurityGroups']

        if groupId:
            sgList = [sg for sg in sgs if sg['GroupId'] == groupId]
            return sgList
        else:
            return sgs

    def getVPCs(self):
        """ get vpcs from ec2 client """
        regionname = self.region
        return self.ec2clientdict[regionname].describe_vpcs()['Vpcs']

    def getSubnets(self):
        """ get subnets from ec2 client """
        regionname = self.region
        return self.ec2clientdict[regionname].describe_subnets()['Subnets']

    def getInstances(self):
        """ get instances from ec2 client """
        regionname = self.region
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
                    logger.debug(instances['State'])
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
                if skipFlag:
                    continue
                else:
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

class TestAWS(unittest.TestCase):
    """ Basic Unit tests for all functions """
    def test_getSecurityGroups(self):
        anb = AWSNimbusBuddy('us-west-2')
        value = anb.getSecurityGroups(None)
        isinstance(value, list)
    
    def test_getAllRegions(self):
        anb = AWSNimbusBuddy('us-west-2')
        regionlist = anb.getAllRegions()
        regionlist.sort()
        awsregionlist = ['ap-northeast-1', 'ap-northeast-2', 'ap-south-1', 'ap-southeast-1', 
            'ap-southeast-2', 'ca-central-1', 'eu-central-1', 'eu-north-1', 'eu-west-1', 
            'eu-west-2', 'eu-west-3', 'sa-east-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
        self.assertEqual(regionlist, awsregionlist)
    
    def test_initRegionList(self):
        regionlist = ['ap-northeast-1', 'ap-northeast-2', 'ap-south-1', 'ap-southeast-1', 
            'ap-southeast-2', 'ca-central-1', 'eu-central-1', 'eu-north-1', 'eu-west-1', 
            'eu-west-2', 'eu-west-3', 'sa-east-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
        anb = AWSNimbusBuddy('us-west-2')
        anb.initRegionList(regionlist)
        ec2keys = list(anb.ec2clientdict.keys())
        ec2keys.sort()
        self.assertEquals(ec2keys, regionlist)

if  __name__ =='__main__': pass
