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
        self.initRegionList()

        self.iamclient = boto3.client('iam')
        # probably not the best data structure for it.
        self.subnets = None
        self.ec2instances = None
    
    def listSubnets(self):
        self.ec2client.describe_subnets()
    
    def listInstances(self):
        self.ec2client.describe_instances()
        # 

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

class TestCloudBuddy(unittest.TestCase):
    def test_aws(self):
        client = boto3.client('ec2')
        isinstance(client, type(boto3.client))

def main():
    acb = AWSCloudBuddy()
    #acb.initRegionList()
    #for key in acb.ec2clientdict.keys():
        #print (key)
        #print (acb.ec2clientdict[key])
    #regionlist = acb.getAllRegions()
    #print (regionlist)

if  __name__ =='__main__': main()

__version__ = '0.1'
__author__ = 'Carroll Kong'