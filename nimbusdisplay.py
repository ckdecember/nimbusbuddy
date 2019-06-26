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

    def displaySecurityGroups(self):
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
        # FromPort == icmp code when in icmp mode
        # ToPort == -1 for icmp

        ipPermissionsList = utils.stripDictList(sgResource.resourceDictList, ['Description', 'GroupName', 'IpPermissions'])
        for ipPermission in ipPermissionsList:
            #logger.debug(ipPermission)
            rulesList = ipPermission['IpPermissions']
            defaultValues = ['FromPort', 'ToPort']
            for rules in rulesList:
                # if FromPort = ToPort, FromPort alone.
                # if icmp, FromPort is Code
                # if IpProtocol tcp or udp, treat as normal.
                # IpRanges: CidrIp 
                # maybe set defaults here?
                for defaultValue in defaultValues:
                    rules.setdefault(defaultValue, '')
                
                # if icmp, change Port to icmp-code, remove ToPort
                # if protocol is not 6 and 17 (tcp and udp respectively) and icmp (1) OR -1, no ports.
                # if normal tcp/udp traffic, and FromPort != ToPort, keep range
                # if normal tcp/udp traffic and FromPort == ToPort, drop ToPort.

                #print ("{IpProtocol} Code {FromPort} From {IpRanges}".format(**rules))
                #print ("{IpProtocol} From {IpRanges}".format(**rules))
                
                #print ("{IpProtocol} Port {FromPort} to {ToPort} From {IpRanges}".format(**rules))
                #print ("{IpProtocol} Port {FromPort} From {IpRanges}".format(**rules))

                #print ("{IpProtocol} {Code,From,Port} {FromPort,IpRange} {From,to,NULL} {IpRanges,ToPort} {NULL, NULL, From {IpRanges}, NULL}".format(**rules))

                # {IpProtocol}
                if rules['IpProtocol'] == "-1":
                    ruleDisplayString = "All traffic"
                else:
                    ruleDisplayString = ("{IpProtocol}".format(**rules))
                
                # Code, From, or Port
                if rules['IpProtocol'] == "icmp":
                    ruleDisplayString += " code "
                elif (rules['IpProtocol'] == "-1") and (not rules['IpRanges']):
                    pass
                # check if there is a real range difference
                elif (rules['IpProtocol'] == "-1") and (rules['IpRanges']):
                    ruleDisplayString += " from "
                elif (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                    ruleDisplayString += " port "
                else:
                    ruleDisplayString += " from "
                                
                # {FromPort},{IpRange}
                if (rules['IpProtocol'] == "-1") and (not rules['IpRanges']):
                    pass
                elif rules['IpProtocol'] == "-1":
                    ruleDisplayString += "{IpRanges}".format(**rules)
                elif (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                    ruleDisplayString += "{FromPort}".format(**rules)
                elif (rules['IpProtocol'] == "icmp"):
                    ruleDisplayString += "{FromPort}".format(**rules)
                else: 
                    ruleDisplayString += "{IpRanges}".format(**rules)

                #logger.debug(rules)
                # "From, To, or NULL"
                if rules['IpProtocol'] == "-1":
                    pass
                elif rules['IpProtocol'] == "icmp":
                    ruleDisplayString += " from "
                elif (rules['ToPort'] == rules['FromPort']) and ((rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp")):
                    pass
                elif (rules['ToPort'] != "-1") and ((rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp")):
                    ruleDisplayString += " to "
                else:
                    pass

                # {IpRanges,ToPort}
                if (rules['ToPort'] == rules['FromPort']) and ((rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp")):
                    pass
                elif (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                    ruleDisplayString += "{ToPort}".format(**rules)
                elif (rules['IpProtocol'] == "icmp"):
                    ruleDisplayString += "{IpRanges}".format(**rules)
                
                # From
                if (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                    ruleDisplayString += " from "
                else:
                    pass

                # {IpRange}
                if (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                    ruleDisplayString += "{IpRanges}".format(**rules)
                else:
                    pass

                #print ("display rule")
                print (ruleDisplayString)

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

