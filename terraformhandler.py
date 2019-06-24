
class TerraformHandler():
    """ Manages Terraform Configuration Outputs"""
    def __init__(self, ami, mainConfigFileName='cloudbuddy-main.tf', variableFileName='cloudbuddy-var.tf'):
        """Can rename configuration files"""
        self.mainConfigFileName = mainConfigFileName
        self.variableFileName = variableFileName
        self.resourceDictList = {}
        self.amiOverride = ami
    
    def terraformDump(self, region, targetRegion):
        """Dumps out two configuration files.  Iterates through Provider, Resource, and Variable sections.
           Within the Resource section, specifically drop VPC, Subnet, Instance configuration.
        """
        # making the MAIN.TF file equivalent        
        fp = open(self.mainConfigFileName, 'w')

        tfcode = self.providerOutput(region=targetRegion)
        fp.write(tfcode)

        # for VPCS
        vpcForDefaultSubnet = ''
        tfcode = ''
        for data in self.resourceDictList['vpc']:
            print ("right before error")
            print (data)
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
            if self.amiOverride:
                tfcode = self.resourceInstanceOutput(data.instanceid, data.instancetype, self.amiOverride, data.subnetid, data.tags)
            else:
                tfcode = self.resourceInstanceOutput(data.instanceid, data.instancetype, data.imageid, data.subnetid, data.tags)
            ## somehow this dupes it.
            fp.write(tfcode)
        fp.close()

        ### VARIABLES.TF
        fp = open(self.variableFileName, 'w')

        tfcode = ''
        resourceTypeList = ['vpc', 'subnet']

        #unclear if instances need variables 

        for resourceType in resourceTypeList:
            for data in self.resourceDictList['vpc']:
                tagValue = ''
                if 'Tags' in data:
                    tagValue = data['Tags']
                tfcode = self.variableOutput(resourceType, data['VpcId'], data['CidrBlock'], tagValue)
                fp.write(tfcode)
    
        #for data in self.resourceDictList['instance']:
            # for ami
        #    tfcode = self.variableOutput('instance', data.uniqueid, data.imageid, data.tags)
        #    fp.write(tfcode)
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
        #format(resource='aws_instance', resource_name=instanceid, instancetype=instancetype, subnet_id = subnet)
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
    
    def setDataList(self, dataList, resourceType):
        """ Set the resource dict lists for later processing """
        self.resourceDictList[resourceType] = dataList
    
    def __repr__(self):
        return (f'{self.__class__.__name__}('
            f'{self.resourceDictList!r}, {self.amiOverride!r}')
    
    def __str__(self):
        return f'{self.resourceDictList}'