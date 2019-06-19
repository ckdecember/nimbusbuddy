
class TerraformHandler():
    def __init__(self, mainConfigFileName='cloudbuddy-main.tf', variableFileName='cloudbuddy-var.tf'):
        self.mainConfigFileName = mainConfigFileName
        self.variableFileName = variableFileName
        self.resourceDictList = {}
    
    def terraformDump(self, region):
        # getSecurityGroups()
        # getGateways()
        resourceTypeList = ['vpc', 'subnet']

        # making the main.tf file equivalent        
        fp = open(self.mainConfigFileName, 'w')
        # you can change the region here
        # by default, no region, but maybe allow you to pass a new region here.
         
        tfcode = self.providerOutput(region=region)
        fp.write(tfcode)

        tfcode = ''

        for resourceType in resourceTypeList:
            tfcode = ''
            for data in self.resourceDictList[resourceType]:
                # can't always rely on this.  make it a new identifier tag during init
                tfcode += self.resourceOutput(resourceType, data.vpcid, data.uniqueid, data.tags, data.vpcid)
            fp.write(tfcode)
        fp.close()

        # ec2 instance, 

        fp = open(self.variableFileName, 'w')

        for resourceType in resourceTypeList:
            for data in self.resourceDictList[resourceType]:
                tfcode = self.variableOutput(resourceType, data.uniqueid, data.cidrblock, data.tags)
                fp.write(tfcode)
        fp.close()
        
    def providerOutput(self, provider="aws", region="us-west-1"):
        providerStr = """provider "{provider}" {{
            region = "{region}"
        }}\n""".format(provider=provider, region=region)
        #print (providerStr)
        return providerStr
    
    def resourceOutput(self, resourceType, resourceName, varName, resourceTag, vpcid):
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
        elif resourceType == 'instance':
            # need instance_type, ami_type, subnet needs to be pulled
            # needs 3 values instanceid, instancetype, subnetid
            resourceStr = """resource "{resource}" "{resource_name}" {{
                instance_type = "t2.micro"
                ami = "${{var.ami_id}}"
                subnet_id = "${{aws_vpc.{vpcid}.id}}"
                tags = {{
                    Name = "{tags}"
                }}
            }}\n"""
            # subnet id will be pulled
            #format(resource='aws_instance', resource_name=instanceid, instancetype=instancetype, subnet_id = subnet)
        #print (resourceStr)
        return resourceStr

    def variableOutput(self, resourceType, varName, typeValue, description):
        variableStr = ""
        if resourceType == 'vpc':
            variableStr = """variable "var_{varName}" {{
                description = "{tags}"
                default = "{cidr}"
            }}\n\n""".format(varName=varName, cidr=typeValue, tags=description)
        elif resourceType == 'subnet':
            variableStr = """variable "var_{varName}" {{
                description = "{tags}"
                default = "{cidr}"
            }}\n\n""".format(varName=varName, cidr=typeValue, tags=description)
        return variableStr
    
    def setDataList(self, dataList, resourceType):
        self.resourceDictList[resourceType] = dataList