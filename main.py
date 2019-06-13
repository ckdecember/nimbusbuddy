"""
Core control module for cloudbuddy

"""

import boto3

# this will inherit aws cloud buddy OR we will use a function pointer
class CloudBuddy:
    def __init__(self):
        pass
    
class AWSCloudBuddy():
    def __init__(self):
        # for now, assume environment variables are in
        self.ec2client = boto3.client('ec2')
        self.iamclient = boto3.client('iam')
        # probably not the best data structure for it.
        self.subnets = None
        self.ec2instances = None
        self.iamusers = None

    def listSubnets(self):
        return self.ec2client.describe_subnets()
    
    def listInstances(self):
        self.ec2client.describe_instances()

    def listVPCs(self):
        self.ec2client.describe_vpcs()

    def listUsers(self):
        self.iamclient.list_users()

def main():
    acb = AWSCloudBuddy()
    subnet = acb.listSubnets()
    print (subnet)

if  __name__ =='__main__': main()   


__version__ = '0.1'
__author__ = 'Carroll Kong'