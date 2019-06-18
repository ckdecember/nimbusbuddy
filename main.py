"""
Core control module for cloudbuddy

"""

import boto3
import botocore
import hcl

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

        self.vpcKeyList = ['CidrBlock', 'State', 'Tags', 'OwnerId', 'VpcId']
        self.vpcExpandedKeyList = ['Tags']

    
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
                    print ("#####################")
                    instancekeyList = ['InstanceId', 'Subnet', 'KeyName', 
                        'State', 'SecurityGroups', 'Placement', 'Tags']
                    for instancekey in instancekeyList:
                        if instancekey in reservedInstance:
                            print ("{} {}".format(instancekey, reservedInstance[instancekey]))
                    print ("#####################")

    def initDataStruct(self, regionList):
        for region in regionList:
            self.dataStruct[region] = []
    
    def getVPCs(self, regionname='us-west-1'):
        #vpc_id, cidrblock, tags, state, ownerid 
        return self.ec2clientdict[regionname].describe_vpcs()
    
    def extractVPC(self, vpcslice):
        vpcDict = {}
        for key in self.vpcKeyList:
            if key in vpcslice:
                # some values are actually lists, expand those lists.
                if key in self.vpcExpandedKeyList:
                    for item in vpcslice[key]:
                        #print ("{} {}".format('Name:', item['Value']))
                        vpcDict[key] = item['Value']
                else:
                    #print ("{} {}".format(key, vpcslice[key]))
                    vpcDict[key] = vpcslice[key]
        # so we can get the data now.  store it somewhere?
        # do we store it in a db?  too heavy?  serialize?
        # have a dump to terraform.
        # instantiate a AWSVPC, somehow make the keylist universal for vpcs
        return vpcDict
    
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


class TerraformHandler():
    def __init__(self, mainConfigFileName='cloudbuddy-main.tf', variableFileName='cloudbuddy-var.tf'):
        # remember, these are the output files
        self.mainConfigFileName = mainConfigFileName
        self.variableFileName = variableFileName
    
    def updateOrSendStuff(self):
        # get the list of vpcs.  subnets.  (maybe build a super string?  then append?)
        pass

    def terraformDump(self):
        # calls different terraoutput modules to create a working config
        # need a better way to collect and call this later.
        # will probably be called all at once.  
        # somehow get the data to loop across.

        # getProviders()
        # getResources()
        # getVpcResources()
        # getSubnetResources()
        # getEC2Resources()
        # getSecurityGroups()
        # getGateways()



        fp = open(self.mainConfigFileName, 'w')

        # use logic on resourceType to dictate the inputs 
        tfcode = self.providerOutput()
        tfcode += self.resourceOutput()

        fp.write(tfcode)
        fp.close()

        fp = open(self.variableFileName, 'w')

        tfcode = self.variableOutput(resourceType, typeValue)
        fp.write(tfcode)
        fp.close()
        
    def providerOutput(self, provider="aws", region="us-west-1"):
        # 
        providerStr = """provider "{provider}" {{
            region = "{region}"
        }}\n""".format(provider=provider, region=region)
        print (providerStr)
        return providerStr
    
    def resourceOutput(self):
        # maybe resource list type, vpcs, subnets, ec2s, securitygroups, internet gateways
        # either conditional or different template.  probably different template for clarity
        # resource, resource_name (arb), cidrblock for vpcs
        # vpcname arbitrary - auto generated, tags/names - any previous tags or else auto create

        resourceStr = """resource "{resource}" "{resource_name}" {{
            cidr_block = "${{var.vpc_cidr}}"
            tags = {{
                Name = "{tags}"
            }}
        }}""".format(resource='aws_vpc', resource_name='vpc_X',tags="automated drone")
        print (resourceStr)
        return resourceStr

    def variableOutput(self, resourceType, typeValue):
        # need to pass cidr
        variableStr = ""

        if resourceType == 'vpc':
            variableStr = """variable "vpc_cidr" {{
                description = "VPC CIDR address"
                default = "{cidr}"
            }}""".format(cidr=typeValue)
        return variableStr

class AWSSubnet():
    def __init__(self):
        pass

class TestCloudBuddy(unittest.TestCase):
    def test_aws(self):
        client = boto3.client('ec2')
        isinstance(client, type(boto3.client))

    #def test_aws_regions(self):
    #    client = boto3.client('ec2')
    #    isinstance(client.describe_regions(),type(list))

def main():
    acb = AWSCloudBuddy()
    #acb.cycleRegionInstances()
    vpcslices = acb.getVPCs()['Vpcs']
    AWSVPCList = []

    #gets vpcs and saves it to the awsvpclist
    
    print ("number of vpcs is {}".format(len(vpcslices)))
    for vpcslice in vpcslices:
        vpcDict = acb.extractVPC(vpcslice)
        AWSVPCinst = AWSVPC(vpcDict)
        AWSVPCList.append(AWSVPCinst)
    
    #list is initialized
    for i in AWSVPCList:
        print (i)

    #print (acb.listInstances('us-east-2'))
    #acb.initRegionList()
    #for key in acb.ec2clientdict.keys():
        #print (key)
        #print (acb.ec2clientdict[key])
    #regionlist = acb.getAllRegions()
    #print (regionlist)


if  __name__ =='__main__': main()

__version__ = '0.2'
__author__ = 'Carroll Kong'