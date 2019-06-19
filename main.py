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
        regionList = self.getAllRegions()
        #self.initDataStruct(regionList)

        self.vpcKeyList = ['CidrBlock', 'State', 'Tags', 'OwnerId', 'VpcId']
        self.vpcExpandedKeyList = ['Tags']

        self.subnetKeyList = ['AvailabilityZone', 'CidrBlock', 'MapPublicIpOnLaunch', 'State', 'SubnetId', 'VpcId', 'OwnerId', 'Tags', 'SubnetArn']
        self.subnetExpandedKeyList = ['Tags']
    
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
        return resourceDict

    def extractVPC(self, vpcslice):
        vpcDict = {}
        for key in self.vpcKeyList:
            if key in vpcslice:
                # some values are actually lists, expand those lists.
                if key in self.vpcExpandedKeyList:
                    for item in vpcslice[key]:
                        vpcDict[key] = item['Value']
                else:
                    vpcDict[key] = vpcslice[key]
        return vpcDict

    def extractSubnet(self, subnetslice):
        subnetDict = {}
        for key in self.subnetKeyList:
            if key in subnetslice:
                if key in self.vpcExpandedKeyList:
                    for item in vpcslice[key]:
                        subnetDict[key] = item['Value']
                else:
                    subnetDict[key] = subnetslice[key]
        return subnetDict                

    
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

class AWSSubnets():
    def __init__(self, subnetDict):
        pass

class TerraformHandler():
    def __init__(self, mainConfigFileName='cloudbuddy-main.tf', variableFileName='cloudbuddy-var.tf'):
        self.mainConfigFileName = mainConfigFileName
        self.variableFileName = variableFileName
        self.resourceDictList = {}
    
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
        # use hcl to check if provider exists.  if so, don't bother.
        # open'r' then.
        # check
        resourceType = 'vpc'

        # making the main.tf file equivalent        
        fp = open(self.mainConfigFileName, 'w')
        # you can change the region here
        # by default, no region, but maybe allow you to pass a new region here.
         
        tfcode = self.providerOutput()

        # with a basename, random digits, then string stuffing
        #  bstr.zfill(maxdigits-len(bstr))
        # need to make unique values for the 'variables' or even resource names that have more than one
        # 
        # go through the list, can trust unique vpcid from amazon.
        # self.dataList[0].vpcid

        for data in self.resourceDictList[resourceType]:
            tfcode += self.resourceOutput(resourceType, data.vpcid, data.vpcid, data.tags)
        fp.write(tfcode)
        fp.close()

        fp = open(self.variableFileName, 'w')

        for data in self.resourceDictList[resourceType]:
            tfcode = self.variableOutput(resourceType, data.vpcid, data.cidrblock, data.tags)
            fp.write(tfcode)
        fp.close()
        
    def providerOutput(self, provider="aws", region="us-west-1"):
        providerStr = """provider "{provider}" {{
            region = "{region}"
        }}\n""".format(provider=provider, region=region)
        print (providerStr)
        return providerStr
    
    def resourceOutput(self, resourceType, resourceName, varName, resourceTag):
        if resourceType == 'vpc':
            resourceStr = """resource "{resource}" "{resource_name}" {{
                cidr_block = "${{var.var_{varName}}}"
                tags = {{
                    Name = "{tags}"
                }}
            }}\n""".format(resource='aws_vpc', varName=varName, resource_name=resourceName,tags=resourceTag)
        print (resourceStr)
        return resourceStr

    def variableOutput(self, resourceType, varName, typeValue, description):
        variableStr = ""
        if resourceType == 'vpc':
            variableStr = """variable "var_{varName}" {{
                description = "{tags}"
                default = "{cidr}"
            }}\n\n""".format(varName=varName, cidr=typeValue, tags=description)
        return variableStr
    
    def setDataList(self, dataList, resourceType):
        self.resourceDictList[resourceType] = dataList
        
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
    
    print ("number of vpcs is {}".format(len(vpcslices)))
    for vpcslice in vpcslices:
        vpcDict = acb.extractVPC(vpcslice)
        AWSVPCinst = AWSVPC(vpcDict)
        AWSVPCList.append(AWSVPCinst)
    
    # generate all lists.
    # get subnetlist
    # get ec2 list

    # setVPClist.setDataList
    
    #list is initialized
    # push the lists onto the dict

    tf = TerraformHandler()
    tf.setDataList(AWSVPCList, "vpc")

    tf.terraformDump()
        #self.vpcid = vpcDict['VpcId']
        #self.cidrblock = vpcDict['CidrBlock']
        #self.state = vpcDict['State']
        #if 'Tags' in vpcDict:
        #    self.tags = vpcDict['Tags']
        #else:
        #    self.tags = None
        #self.ownerid = vpcDict['OwnerId']


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