import logging

import tabulate

import aws
import utils


logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

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

    def displayAllSecurityGroups(self):
        """ Displays all security groups """
        # ipprotocol -1 is ALL.
        # ip ranges is [], is that all?
        # if ippermissions is empty, it means no rules.  
        print ("\n")
        sgs = self.anb.getSecurityGroups(None)
        sgResource = aws.AWSResource(sgs, 'securitygroup')
        # if a list for type of output is around
        ['IpProtocol', 'IpRanges']
        ['FromPort', 'IpProtocol', 'IpRanges', 'ToPort']
        # fromport is start range of ports.  toport is end range of ports
        # 'IpRanges': [{'CidrIp': '104.247.55.102/32', 'Description': ''}, {'CidrIp': '69.115.177.236/32', 'Description': ''}]
        # IpRanges is a list of CidrIp/Description dicts.  
        # FromPort == icmp code when in icmp mode
        # ToPort == -1 for icmp
        
        # how to deal with ip ranges.  you can loop them somehow.  
        # work off of final string, loop off of IpRanges, iprange
        logger.debug(sgResource.resourceDictList)

        # get resourceDictList, then extract only resources
        # 

        ipPermissionsList = utils.stripDictList(sgResource.resourceDictList, ['Description', 'GroupName', 'IpPermissions', 'GroupId'])
        for ipPermission in ipPermissionsList:
            logger.debug("### START ###")

            print ("{GroupName} - {Description} - {GroupId}".format(**ipPermission))
            print ("_________________________________________")

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
                # expand IpRange somehow
                if (rules['IpProtocol'] == "-1") and (not rules['IpRanges']):
                    pass
                elif (rules['IpProtocol'] == "-1") and (rules['IpRanges']):
                    #[{'CidrIp': '104.247.55.102/32', 'Description': ''}, {'CidrIp': '1.2.3.4/30', 'Description': ''}]
                    cidrList = [ipRange['CidrIp'] for ipRange in rules['IpRanges']]
                    expandedCidrString = ", ".join(cidrList)
                    #ruleDisplayString += "{IpRanges}".format(**rules)
                    ruleDisplayString += "{}".format(expandedCidrString)
                elif (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                    ruleDisplayString += "{FromPort}".format(**rules)
                elif (rules['IpProtocol'] == "icmp"):
                    ruleDisplayString += "{FromPort}".format(**rules)
                else:
                    #cidrList = [ipRange['CidrIp'] for ipRange in rules['IpRanges']]
                    #expandedCidrString = ", ".join(cidrList)
                    
                    expandedCidrString = utils.flattenAndExpandList(rules['IpRanges'])
                    ruleDisplayString += "{}".format(expandedCidrString)
                    #ruleDisplayString += "{IpRanges}".format(**rules)
                
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
                # also expand ipRanges
                if (rules['ToPort'] == rules['FromPort']) and ((rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp")):
                    pass
                elif (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                    ruleDisplayString += "{ToPort}".format(**rules)
                elif (rules['IpProtocol'] == "icmp"):
                    expandedCidrString = utils.flattenAndExpandList(rules['IpRanges'])
                    ruleDisplayString += "{}".format(expandedCidrString)
                    #ruleDisplayString += "{IpRanges}".format(**rules)
                # From
                if (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                    ruleDisplayString += " from "
                else:
                    pass

                # {IpRange}
                # expand ip ranges if needed.
                if (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                    #cidrList = [ipRange['CidrIp'] for ipRange in rules['IpRanges']]
                    #expandedCidrString = ", ".join(cidrList)
                    #ruleDisplayString += "{}".format(expandedCidrString)
                    expandedCidrString = utils.flattenAndExpandList(rules['IpRanges'])
                    ruleDisplayString += "{}".format(expandedCidrString)
                    #ruleDisplayString += "{IpRanges}".format(**rules)
                else:
                    pass

                #print ("display rule")
                print (ruleDisplayString)
            logger.debug("### END ###")
            print ("\n\n\n")

        # pop one out of the list
        #logger.debug(ipPermissionsList)
        #print (tabulate.tabulate(ipPermissionsList, headers="keys"))
    
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
                expandedCidrString = utils.flattenAndExpandList(rules['IpRanges'])
                ruleDisplayString += "{}".format(expandedCidrString)

            # From
            if (rules['IpProtocol'] == "tcp") or (rules['IpProtocol'] == "udp"):
                ruleDisplayString += " from "
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
        return self.getSecurityGroupRules(sgs[0])
        
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

        # here copy the list of displayed instances
        # use it to feed the rules

        
