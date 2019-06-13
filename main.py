"""
Core control module for cloudbuddy

"""


import boto3

# get AWS credentials
# get from environment variables
# check for failure on no-auth
#Boto3 will check these environment variables for credentials:
#AWS_ACCESS_KEY_ID
#The access key for your AWS account.
#AWS_SECRET_ACCESS_KEY
#The secret key for your AWS account.
#AWS_SESSION_TOKEN
#The session key for your AWS account. This is only needed when you are using temporary credentials. The AWS_SECURITY_TOKEN environment variable can also be used, but is only supported for backwards compatibility purposes. AWS_SESSION_TOKEN is supported by multiple AWS SDKs besides python.

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
    
    def listUsers(self):
        self.client.list_users()

def main():
    acb = AWSCloudBuddy()
    subnet = acb.listSubnets()

if  __name__ =='__main__': main()   


__version__ = '0.1'
__author__ = 'Carroll Kong'