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

class CloudBuddy:
    def __init__(self):
        # for now, assume environment variables are in
        self.client = boto3.client('ec2')

