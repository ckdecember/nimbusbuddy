import logging

import aws

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)
logger.addHandler(ch)

class TerraformHandler():
    """ Manages Terraform Configuration Outputs"""
    def __init__(self, region, targetRegion, ami, mainConfigFileName='cloudbuddy-main.tf', variableFileName='cloudbuddy-var.tf'):
        """Can rename configuration files"""
        self.mainConfigFileName = mainConfigFileName
        self.variableFileName = variableFileName
        self.resourceDictList = {}
        self.amiOverride = ami

        self.anb = aws.AWSNimbusBuddy(region)
        self.targetRegion = targetRegion

        VPCList = self.anb.getVPCs()
        vpcs2 = aws.AWSResource(VPCList, 'vpc')
        self.resourceDictList['vpc'] = vpcs2.resourceDictList

        SubnetList = self.anb.getSubnets()
        subnets2 = aws.AWSResource(SubnetList, 'subnet')
        self.resourceDictList['subnet'] = subnets2.resourceDictList

        InstanceList = self.anb.getInstances()
        inst2 = aws.AWSResource(InstanceList, 'instance')
        self.resourceDictList['instance'] = inst2.resourceDictList
    
    def terraformDump(self):
        """Dumps out two configuration files.  Iterates through Provider, Resource, and Variable sections.
           Within the Resource section, specifically drop VPC, Subnet, Instance configuration.
        """
        # making the MAIN.TF file equivalent
        targetRegion = self.targetRegion

        fp = open(self.mainConfigFileName, 'w')

        tfcode = self.providerOutput(region=targetRegion)
        fp.write(tfcode)

        # for VPCS
        vpcForDefaultSubnet = ''
        tfcode = ''
        for data in self.resourceDictList['vpc']:
            if data['IsDefault']:
                vpcForDefaultSubnet = data['VpcId']
            else:
                tfcode += self.resourceOutput('vpc', data['VpcId'], data['VpcId'], data['Tags'], data['VpcId'])
        fp.write(tfcode)

        # for SUBNETS
        tfcode = ''
        for data in self.resourceDictList['subnet']:
            if data['VpcId'] == vpcForDefaultSubnet:
                continue
            tfcode += self.resourceOutput('subnet', data['VpcId'], data['SubnetId'], data['Tags'], data['VpcId'])
        fp.write(tfcode)
        
        # for INSTANCES
        tfcode = ''
        for data in self.resourceDictList['instance']:
            # check for tags, and set with a default or different output?
            # hack for now
            if 'Tags' not in data:
                data['Tags'] = ''

            if self.amiOverride:
                #tfcode = self.resourceInstanceOutput(data.instanceid, data.instancetype, self.amiOverride, data.subnetid, data.tags)
                tfcode = self.resourceInstanceOutput(data['InstanceId'], data['InstanceType'], self.amiOverride, data['SubnetId'], data['Tags'])
            else:
                logger.debug(data)
                tfcode = self.resourceInstanceOutput(data['InstanceId'], data['InstanceType'], data['ImageId'], data['SubnetId'], data['Tags'])
            fp.write(tfcode)
        fp.close()

        ### VARIABLES.TF
        fp = open(self.variableFileName, 'w')

        tfcode = ''
        resourceTypeList = ['vpc', 'subnet']

        #unclear if instances need variables 
        # duplicate variables being outputed here.

        #for resourceType in resourceTypeList:
        for data in self.resourceDictList['vpc']:
            tagValue = ''
            if 'Tags' in data:
                tagValue = data['Tags']
            tfcode = self.variableOutput('vpc', data['VpcId'], data['CidrBlock'], tagValue)
            fp.write(tfcode)
    
        for data in self.resourceDictList['subnet']:
            tagValue = ''
            if 'Tags' in data:
                tagValue = data['Tags']
            tfcode = self.variableOutput('subnet', data['SubnetId'], data['CidrBlock'], tagValue)
            fp.write(tfcode)
    
        fp.close()
        
    def providerOutput(self, provider="aws", region="us-west-1"):
        """ Terraform configuration snippet for Provider Section """
        providerStr = """provider "{provider}" {{
            region = "{region}"
        }}\n""".format(provider=provider, region=region)
        #print (providerStr)
        return providerStr
    
    def resourceOutput(self, resourceType, resourceName, varName, resourceTag, vpcid):
        """ Terraform configuration snippet for Resource Section """
        resourceStr = ''
        if resourceType == 'vpc':
            resourceStr = """resource "{resource}" "{resource_name}" {{
                cidr_block = "${{var.var_{varName}}}"
                tags = {{
                    Name = "{tags}"
                }}
            }}\n""".format(resource='aws_vpc', varName=varName, resource_name=resourceName,tags=resourceTag)
        elif resourceType == 'subnet': 
            resourceStr = """resource "{resource}" "{resource_name}" {{
                vpc_id = "${{aws_vpc.{vpcid}.id}}"
                cidr_block = "${{var.var_{varName}}}"
                tags = {{
                    Name = "{tags}"
                }}
            }}\n""".format(resource='aws_subnet', vpcid=vpcid, varName=varName, resource_name=varName,tags=resourceTag)
        #print (resourceStr)
        return resourceStr

    def variableOutput(self, resourceType, varName, typeValue, description):
        """ Terraform configuration snippet for Variable Section """
        variableStr = ""
        if resourceType == 'vpc':
            variableStr = """variable "var_{varName}" {{
                description = "{tags}"
                default = "{typeValue}"
            }}\n\n""".format(varName=varName, typeValue=typeValue, tags=description)
        elif resourceType == 'subnet':
            variableStr = """variable "var_{varName}" {{
                description = "{tags}"
                default = "{typeValue}"
            }}\n\n""".format(varName=varName, typeValue=typeValue, tags=description)
        elif resourceType == 'instance':
            variableStr = """variable "var_ami_{varName}" {{
                description = "{tags}"
                default = "{typeValue}"
            }}\n\n""".format(varName=varName, typeValue=typeValue, tags=description)

        return variableStr
    
    def resourceInstanceOutput(self, instanceid, instancetype, imageid, subnetid, tags):
        """ Terraform configuration snippet for Resource / Instances Section """
        resourceStr = ''
        # need instance_type, ami_type, subnet needs to be pulled
        # needs 3 values instance_type (as variable?)
        # need Name?tags?
        # instanceType?

        resourceStr = """resource "{resource}" "{resourceName}" {{
            instance_type = "{instanceType}"
            ami = "{imageid}"
            subnet_id = "${{aws_subnet.{subnetid}.id}}"
            tags = {{
                Name = "{tags}"
            }}
        }}\n""".format(resource="aws_instance", resourceName=instanceid, instanceType=instancetype, imageid=imageid, subnetid=subnetid, tags=tags)
        print (resourceStr)
        return resourceStr

    # -- UNUSED for now.  maybe not needed.  pending more tests
    def variableInstanceOutput(self, resourceType, varName, typeValue, description):
        """ Terraform configuration snippet for Variable / Instances Section """
        variableStr = ""
        variableStr = """variable "{prefix}_{varName}" {{
            description = "{tags}"
            default = "{cidr}"
        }}\n\n""".format(prefix="ami", varName=varName, tags=tags)
        return variableStr
    
    def securityGroup():
        """vpc_security_group_ids = ["sg-085696c3b2fafa552"]"""
        pass
        

    def setDataList(self, dataList, resourceType):
        """ Set the resource dict lists for later processing """
        self.resourceDictList[resourceType] = dataList
    
    def __repr__(self):
        return (f'{self.__class__.__name__}('
            f'{self.resourceDictList!r}, {self.amiOverride!r}')
    
    def __str__(self):
        return f'{self.resourceDictList}'
