"""
Core control module for cloudbuddy

"""

import boto3
import botocore

import unittest

# this will inherit aws cloud buddy OR we will use a function pointer
class CloudBuddy:
    def __init__(self):
        pass
    
class AWSCloudBuddy():
    def __init__(self):
        self.ec2client = boto3.client('ec2', region_name = 'us-east-2')
        self.ec2clientdict = {}
        self.dataStruct = {}
        self.initRegionList()

        self.iamclient = boto3.client('iam')
        # probably not the best data structure for it.
        self.subnets = None
        self.ec2instances = None

        regionList = self.getAllRegions()
        self.initDataStruct(regionList)
    
    def listSubnets(self):
        self.ec2client.describe_subnets()
    
    def listInstances(self, region):
        instances = self.ec2clientdict[region].describe_instances()
        return instances

    def listVPCs(self):
        self.ec2client.describe_vpcs()

    def listUsers(self):
        self.iamclient.list_users()

    def getAllRegions(self):
        fullregionlist = self.ec2client.describe_regions()
        regionlist = [i['RegionName'] for i in fullregionlist['Regions']]
        return regionlist

    def initRegionList(self):
        regionList = self.getAllRegions()
        for region in regionList:
            self.ec2clientdict[region] = boto3.client('ec2', region_name=region)
    
    def cycleRegionInstances(self):
        regionList = self.getAllRegions()
        print ("Start")
        for region in regionList:
            print (region)
            instances = self.listInstances(region)
            for reservation in instances['Reservations']:
                for reservedInstance in reservation['Instances']:
                    #print (reservedInstance)
                    #print (reservedInstance.keys())
                    print ("InstanceId {}".format(reservedInstance['InstanceId']))
                    print ("Subnet {}".format(reservedInstance['SubnetId']))
                    print ("KeyName {}".format(reservedInstance['KeyName']))
                    print ("State {}".format(reservedInstance['State']))
                    print ("Security Groups {}".format(reservedInstance['SecurityGroups']))
                    if 'Placement' in reservedInstance:
                        print ("Placement {}".format(reservedInstance['Placement']))
                    if 'Tags' in reservedInstance:
                        print ("Tags {}".format(reservedInstance['Tags']))

    def initDataStruct(self, regionList):
        for region in regionList:
            self.dataStruct[region] = []

class TestCloudBuddy(unittest.TestCase):
    def test_aws(self):
        client = boto3.client('ec2')
        isinstance(client, type(boto3.client))

    def test_aws_regions(self):
        pass

def main():
    acb = AWSCloudBuddy()
    acb.cycleRegionInstances()
    #print (acb.listInstances('us-east-2'))





    #acb.initRegionList()
    #for key in acb.ec2clientdict.keys():
        #print (key)
        #print (acb.ec2clientdict[key])
    #regionlist = acb.getAllRegions()
    #print (regionlist)

if  __name__ =='__main__': main()

__version__ = '0.1'
__author__ = 'Carroll Kong'