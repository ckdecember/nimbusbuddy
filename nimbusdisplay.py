import logging

import tabulate

import aws
import utils


logger = logging.getLogger(__name__)

class Display():
    def __init__(self, region):
        self.anb = aws.AWSNimbusBuddy(region)
        self.region = region
    
    def VPCandSubnets(self, region):
        logger.debug("vpcs and subnets")
        allowedKeys = ['InstanceId', 'Tags', 'State', 'SecurityGroups']

        # get list of vpcid and subnetid pairs
        vpcsubnetpairs = self.anb.getVPCandSubnetPairs()
        logger.debug(vpcsubnetpairs)

        for (vpcid, vpccidr, subnetid, subnetcidr) in vpcsubnetpairs:
            originalList = self.anb.displayInstanceView(region, vpcid, subnetid)
            displayList = []

            # this dict helps flatten dictionaries that are values to keys.  
            # Key: Flatten Key
            
            flattenDict = {'Tags': 'Value', 'State': 'Name', 'SecurityGroups': 'GroupId'}

            print ("VPC: {} {} Subnet: {} {} ".format(vpcid, vpccidr, subnetid, subnetcidr))
            for originalitem in originalList:
                displayitem = {key: value for (key, value) in originalitem.items() if key in allowedKeys}
                for (fdkey, fdvalue) in flattenDict.items():
                    if fdkey in displayitem:
                        displayitem[fdkey] = utils.flattenItem(displayitem, fdkey, fdvalue)
                displayList.append(displayitem)
            finalDisplay = tabulate.tabulate(displayList, headers='keys')
            if finalDisplay:
                print (finalDisplay)
            else:
                print ("No Instances Found")

def testSecurityGroup(region, sgResource):
    # just expand the ipprotocol
    # ipprotocol -1 is ALL.
    # ip ranges is [], is that all?
    # if ippermissions is empty, it means no rules.  
    # could be hard to flatten

    # if a list for type of output is around
    ['IpProtocol', 'IpRanges']
    ['FromPort', 'IpProtocol', 'IpRanges', 'ToPort']
    # fromport is start range of ports.  toport is end range of ports
    # 'IpRanges': [{'CidrIp': '104.247.55.102/32', 'Description': ''}, {'CidrIp': '69.115.177.236/32', 'Description': ''}]
    # IpRanges is a list of CidrIp/Description dicts.  

    ipPermissionsList = utils.stripDictList(sgResource.resourceDictList, ['IpPermissions'])
    for ipPermission in ipPermissionsList:
        rulesList = ipPermission['IpPermissions']
        logger.debug("Start of Rules")
        for rules in rulesList:
            if "FromPort" in rules.keys():
                print ("hi")
            # interpret the dict keys
            if "FromPort" in rules:
                print ("\tPort: {FromPort} IpProtocol: {IpProtocol}".format(**rules))
            logger.debug(rules)
        logger.debug("end of rules")

    # pop one out of the list

    #logger.debug(ipPermissionsList)

    #print (tabulate.tabulate(ipPermissionsList, headers="keys"))

def display(region):
    """ Display Simple Tables of VPCs, Instances, and Subnets """
    anb = AWSNimbusBuddy()

    print ("Region: {}".format(region))
    
    # could make a super list of dicts, with unified dicts.
    # three sections, maybe turn it into a function later
    # 
    tmpDict = {}
    
    displayList = []
    allowedKeys = ['CidrBlock', 'VpcId', 'IsDefault']
    print (10*"#")
    print ("VPCs")
    print (10*"#")
    vpcsuperlist = anb.getVPCs(regionname=region)
    for vpc in vpcsuperlist:
        trimmedDict = {key: value for (key, value) in vpc.items() if key in allowedKeys}
        displayList.append(trimmedDict)

    print (tabulate.tabulate(displayList, headers='keys'))
    print (2*"\n")

    print (10*"#")
    print ("Subnets")
    print (10*"#")
    displayList = []
    allowedKeys = ['CidrBlock', 'VpcId', 'IsDefault', 'SubnetId']
    subnetsuperlist = anb.getSubnets(regionname=region)
    for subnet in subnetsuperlist:
        trimmedDict = {key: value for (key, value) in subnet.items() if key in allowedKeys}
        displayList.append(trimmedDict)

    print (tabulate.tabulate(displayList, headers='keys'))
    print (2*"\n")

    print (10*"#")
    print ("Instances")
    print (10*"#")
    displayList = []
    allowedKeys = ['CidrBlock', 'VpcId', 'IsDefault', 'SubnetId', 'ImageId', 'InstanceId', 'SecurityGroups', 'State']
    instancesuperlist = anb.getInstances(regionname=region)
    # maybe run it through the main filter?

    for instanceList in instancesuperlist:
        for instance in instanceList['Instances']:
            trimmedDict = {key: value for (key, value) in instance.items() if key in allowedKeys}
            trimmedDict['SecurityGroups'] = flattenDict(trimmedDict['SecurityGroups'], 'GroupId')
            if trimmedDict['State']['Name'] == 'terminated':
                continue
            trimmedDict['State'] = flattenDict(trimmedDict['State'], 'Name')
            displayList.append(trimmedDict)

    print (tabulate.tabulate(displayList, headers='keys'))
    print (2*"\n")

