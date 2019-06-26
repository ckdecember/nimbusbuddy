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
        # define constants
        self.DISPLAY_ALLTRAFFIC = """all"""
        self.DISPLAY_ICMP = """\ticmp"""
        self.DISPLAY_ICMPCODE = """\ticmpcode\t"""
        self.DISPLAY_FROM = """\tfrom\t"""
        self.DISPLAY_PORT = """\tport\t"""
        self.DISPLAY_TO = """\tto\t"""

    def VPCandSubnets(self):
        """ Gets a list of VPCs and the subnets that are within them."""
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
            print ("________________________________________________________")
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
            print ("\n")
   
    def getSecurityGroupRules(self, securityGroupResource):
        """ Given a security group ID, get the rules for it."""
        # needs ipPermission which is normally 
        #['Description', 'GroupName', 'IpPermissions', 'GroupId'])

        # get SG that fits the one groupId.

        rulesList = securityGroupResource['IpPermissions']
        defaultValues = ['FromPort', 'ToPort']
        formattedRulesList = []

        for rules in rulesList:
            for defaultValue in defaultValues:
                rules.setdefault(defaultValue, '')
            # ("{IpProtocol} {Code,From,Port} {FromPort,IpRange} {From,to,NULL} {IpRanges,ToPort} {NULL, NULL, From {IpRanges}, NULL}".format(**rules))

            # {IpProtocol}
            if rules['IpProtocol'] == "-1":
                ruleDisplayString = self.DISPLAY_ALLTRAFFIC
            else:
                ruleDisplayString = ("{IpProtocol}".format(**rules))
            
            # Code, From, or Port
            if rules['IpProtocol'] == "icmp":
                ruleDisplayString += self.DISPLAY_ICMPCODE
            elif (rules['IpProtocol'] == "-1") and (not rules['IpRanges']):
                pass
            # check if there is a real range difference
            elif (rules['IpProtocol'] == "-1") and (rules['IpRanges']):
                ruleDisplayString += self.DISPLAY_FROM
            elif (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                ruleDisplayString += self.DISPLAY_PORT
            else:
                ruleDisplayString += self.DISPLAY_FROM
                            
            # {FromPort},{IpRange}
            if (rules['IpProtocol'] == "-1") and (not rules['IpRanges']):
                pass
            elif (rules['IpProtocol'] == "-1") and (rules['IpRanges']):
                cidrList = [ipRange['CidrIp'] for ipRange in rules['IpRanges']]
                expandedCidrString = ", ".join(cidrList)
                ruleDisplayString += "{}".format(expandedCidrString)
            elif (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                ruleDisplayString += "{FromPort}".format(**rules)
            elif (rules['IpProtocol'] == "icmp"):
                ruleDisplayString += "{FromPort}".format(**rules)
            else:
                expandedCidrString = utils.flattenAndExpandList(rules['IpRanges'])
                ruleDisplayString += "{}".format(expandedCidrString)
            
            # "From, To, or NULL"
            if rules['IpProtocol'] == "-1":
                pass
            elif rules['IpProtocol'] == "icmp":
                ruleDisplayString += self.DISPLAY_FROM
            elif (rules['ToPort'] == rules['FromPort']) and ((rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp")):
                pass
            elif (rules['ToPort'] != "-1") and ((rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp")):
                ruleDisplayString += self.DISPLAY_TO
            else:
                pass

            # {IpRanges,ToPort}
            if (rules['ToPort'] == rules['FromPort']) and ((rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp")):
                pass
            elif (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                ruleDisplayString += "{ToPort}".format(**rules)
            elif (rules['IpProtocol'] == "icmp"):
                expandedCidrString = utils.flattenAndExpandList(rules['IpRanges'])
                ruleDisplayString += "{}".format(expandedCidrString)

            # From
            if (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                ruleDisplayString += self.DISPLAY_FROM
            else:
                pass

            # {IpRange}
            if (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                expandedCidrString = utils.flattenAndExpandList(rules['IpRanges'])
                ruleDisplayString += "{}".format(expandedCidrString)
            else:
                pass
            # push to list to return???
            formattedRulesList.append(ruleDisplayString)
        return formattedRulesList

    def getSecurityGroupFormattedList(self, groupId):
        """ Displays security group rules """
        print ("TESTHERE")
        #('sg-073d12a9bc6701df6')
        sgs = self.anb.getSecurityGroups(groupId)
        return self.getSecurityGroupRules(sgs)
    
    def display(self):
        """ Displays VPCs, Subnets """

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

        # here copy the list of displayed instances
        # use it to feed the rules

        for item in displayList:
            print ("InstanceId: {} \t SecurityGroup: {}".format(item['InstanceId'], item['SecurityGroups']))
            sgResources = self.anb.getSecurityGroups(item['SecurityGroups'])
            for sgResource in sgResources:
                rulesList = self.getSecurityGroupRules(sgResource)
                print ("________________________________________________________________________________")
                for rule in rulesList:
                    print (rule)
            print ("\n")
