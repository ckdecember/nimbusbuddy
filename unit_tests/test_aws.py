"""
Test suite for aws module in Nimbusbuddy

"""

import unittest

import boto3

from aws import AWSNimbusBuddy, AWSResource


class TestNimbusBuddy(unittest.TestCase):
    """ Basic Unit Test for boto3 / ec2 instantiation"""

    def test_aws(self):
        client = boto3.client("ec2")
        isinstance(client, type(boto3.client))


class TestAWS(unittest.TestCase):
    """ Basic Unit tests """

    def test_boto3(self):
        ec2client = boto3.client("ec2")
        isinstance(boto3.client, type(ec2client))

    def test_getAWSResource(self):
        anb = AWSNimbusBuddy("us-west-2")
        instances = anb.getInstances()
        resource = AWSResource(instances, "instance")
        isinstance(resource.resourceDictList, list)

    def test_getSecurityGroups(self):
        anb = AWSNimbusBuddy("us-west-2")
        value = anb.getSecurityGroups(None)
        isinstance(value, list)

    def test_getAllRegions(self):
        anb = AWSNimbusBuddy("us-west-2")
        regionlist = anb.getAllRegions()
        regionlist.sort()
        awsregionlist = [
            "ap-northeast-1",
            "ap-northeast-2",
            "ap-south-1",
            "ap-southeast-1",
            "ap-southeast-2",
            "ca-central-1",
            "eu-central-1",
            "eu-north-1",
            "eu-west-1",
            "eu-west-2",
            "eu-west-3",
            "sa-east-1",
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
        ]
        self.assertEqual(regionlist, awsregionlist)

    def test_initRegionList(self):
        regionlist = [
            "ap-northeast-1",
            "ap-northeast-2",
            "ap-south-1",
            "ap-southeast-1",
            "ap-southeast-2",
            "ca-central-1",
            "eu-central-1",
            "eu-north-1",
            "eu-west-1",
            "eu-west-2",
            "eu-west-3",
            "sa-east-1",
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
        ]
        anb = AWSNimbusBuddy("us-west-2")
        anb.initRegionList(regionlist)
        ec2keys = list(anb.ec2clientdict.keys())
        ec2keys.sort()
        self.assertEqual(ec2keys, regionlist)

    def test_terminated_instance(self):
        # test to ensure terminated instances do NOT leak through
        # unfortunately needs a mock since original us-west-2 might not have it.
        anb = AWSNimbusBuddy("us-west-2")
        resourceList = anb.getInstances()
        awsresource = AWSResource(resourceList, "instance")
        for resource in awsresource.resourceDictList:
            self.assertNotEqual(
                resource["State"]["Name"],
                "terminated",
                msg="Terminated Instances leaked through",
            )

    def test_getVpcsAndSubnets(self):
        # getVPCandSubnetPairs
        # maybe get a mock instead?  or test more closely
        pass
