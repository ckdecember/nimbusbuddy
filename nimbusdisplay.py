import logging

import tabulate

import aws
import utils


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)
logger.addHandler(ch)

class Display():
    def __init__(self, region):
        self.anb = aws.AWSNimbusBuddy(region)
        self.region = region
    
    def VPCandSubnets(self):
        logger.debug("vpcs and subnets")
        allowedKeys = ['InstanceId', 'Tags', 'State', 'SecurityGroups']

        # get list of vpcid and subnetid pairs
        vpcsubnetpairs = self.anb.getVPCandSubnetPairs()
        logger.debug(vpcsubnetpairs)

        for (vpcid, vpccidr, subnetid, subnetcidr) in vpcsubnetpairs:
            originalList = self.anb.displayInstanceView(vpcid, subnetid)
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

    def testSecurityGroup(self):
        # ipprotocol -1 is ALL.
        # ip ranges is [], is that all?
        # if ippermissions is empty, it means no rules.  

        sgs = self.anb.getSecurityGroups()
        sgResource = aws.AWSResource(sgs, 'securitygroup')
        # if a list for type of output is around
        ['IpProtocol', 'IpRanges']
        ['FromPort', 'IpProtocol', 'IpRanges', 'ToPort']
        # fromport is start range of ports.  toport is end range of ports
        # 'IpRanges': [{'CidrIp': '104.247.55.102/32', 'Description': ''}, {'CidrIp': '69.115.177.236/32', 'Description': ''}]
        # IpRanges is a list of CidrIp/Description dicts.  

        ipPermissionsList = utils.stripDictList(sgResource.resourceDictList, ['Description', 'GroupName', 'IpPermissions'])
        for ipPermission in ipPermissionsList:
            logger.debug(ipPermission)
            rulesList = ipPermission['IpPermissions']
            logger.debug("Start of Rules")
            for rules in rulesList:
                if "FromPort" in rules.keys():
                    continue
                # interpret the dict keys
                if "FromPort" in rules:
                    #print ("\tPort: {FromPort} IpProtocol: {IpProtocol}".format(**rules))
                    continue
                logger.debug(rules)
            logger.debug("end of rules")

        # pop one out of the list
        #logger.debug(ipPermissionsList)
        #print (tabulate.tabulate(ipPermissionsList, headers="keys"))

    def display(self):
        """ Display Simple Tables of VPCs, Instances, and Subnets """

        region = self.region
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
        vpcsuperlist = self.anb.getVPCs()
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
        subnetsuperlist = self.anb.getSubnets()
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
        instancesuperlist = self.anb.getInstances()
        # maybe run it through the main filter?

        for instanceList in instancesuperlist:
            for instance in instanceList['Instances']:
                trimmedDict = {key: value for (key, value) in instance.items() if key in allowedKeys}
                trimmedDict['SecurityGroups'] = utils.flattenDict(trimmedDict['SecurityGroups'], 'GroupId')
                if trimmedDict['State']['Name'] == 'terminated':
                    continue
                trimmedDict['State'] = utils.flattenDict(trimmedDict['State'], 'Name')
                displayList.append(trimmedDict)

        print (tabulate.tabulate(displayList, headers='keys'))
        print (2*"\n")

