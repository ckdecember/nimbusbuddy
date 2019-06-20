
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
        
        tfcode = ''
        for data in self.resourceDictList['instance']:
            tfcode = self.resourceInstanceOutput(data.instanceid, data.instancetype, data.imageid, data.subnetid, data.tags)
            ## somehow this dupes it.
            fp.write(tfcode)
        fp.close()

        ### VARIABLES.TF
        fp = open(self.variableFileName, 'w')

        tfcode = ''
        for resourceType in resourceTypeList:
            for data in self.resourceDictList[resourceType]:
                tfcode = self.variableOutput(resourceType, data.uniqueid, data.cidrblock, data.tags)
                fp.write(tfcode)

        #for data in self.resourceDictList['instance']:
            # for ami
        #    tfcode = self.variableOutput('instance', data.uniqueid, data.imageid, data.tags)
        #    fp.write(tfcode)
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
        #print (resourceStr)
        return resourceStr

    def variableOutput(self, resourceType, varName, typeValue, description):
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
        variableStr = ""
        variableStr = """variable "{prefix}_{varName}" {{
            description = "{tags}"
            default = "{cidr}"
        }}\n\n""".format(prefix="ami", varName=varName, tags=tags)
        return variableStr

    
    def setDataList(self, dataList, resourceType):
        self.resourceDictList[resourceType] = dataList