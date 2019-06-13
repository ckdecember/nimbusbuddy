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
        self.client = boto3.client('ec2')

    def listSubnets(self):
        self.client.describe_subnets()
    
    def listInstances(self):
        self.client.describe_instances()

    def listVPCs(self):
        pass

    def listUsers(self):
        self.client.list_users()

def main():
    acb = AWSCloudBuddy()
    subnet = acb.listSubnets()

if  __name__ =='__main__': main()   


__version__ = '0.1'
__author__ = 'Carroll Kong'