# nimbus buddy

# What is it?

A tool to help visualize your cloud infrastructure and also allows you to output terraform configurations on your existing AWS.  Currently it supports VPCs, Subnets, and Instances.  

Support for Security Groups and Internet Gateways are on the short list.

In the future, I would like to extend nimbus buddy to work with other major cloud services such as Azure and Google Cloud Platform.  Another wish list feature would be a way to migrate between AWS and Azure or Google Cloud Platform.

# Tech Specs
It is a python script that utilizes boto3 to make AWS requests and transforms it into nice ASCII tables (pending support for HTML).  It also outputs configuration files for terraform (https://www.terraform.io/) which is a really powerful infrastructure as code tool.  I highly suggest you take a look at it if you are into doing mass deployments.

# ... but why?

I found AWS can be pretty daunting even if you have a background in networking.  It seemed pretty hard to get a quick overview of what was going on network-wise and possible security settings between hosts.  This tool will help automate the process of drilling down 3-4 clicks just to get the key network information you need.  

The ability to output terraform configuration files can help people migrate their existing cloud networks more easily, transition from prototype to full-scale automated deployments, or just have a backup of your AWS.

# Why not call it AWS Buddy?

I plan to extend the code so it will work with other cloud technologies, so I'd rather have a more agnostic name.  Currently I am most familiar with AWS.

# Requirements

- python3
- boto3
- tabulate

# Installation on Ubuntu 18

```
sudo apt install awscli  
aws configure  
sudo apt install python3-pip  
  
echo "boto3" >> requirements.txt  
echo "tabulate" >> requirements.txt  
  
pip install -r requirements.txt  
```

# Configuration
A valid AWS account and proper passing of credentials is required for this application to work.

You can either set three AWS environment variables with the proper credentials or you can run "aws configure"

``
export AWS_ACCESS_KEY_ID=[ACCESSKEY]  
export AWS_SECRET_ACCESS_KEY=[SECRETACCESSKEY]  
export AWS_DEFAULT_REGION=[DEFAULTREGION]  
``  
  
# Command Line
``python main.py [command] [region] --ami=[AMI-OVERRIDE]``  
(--ami is optional)  

valid commands are "display" and "terraform".  
  
Display will reveal your VPCs/Subnets/Instances  
Terraform will output your AWS network into a main.tf and variable.tf file.  

--ami overrides the terraform output to use this AMI for all instances.  This is handy when your previous AMI does NOT exist in the target AWS zone.  
--targetregion changes the "region" in the terraform configuration so you can target a different region than the one you backed up from.

Example:  
``python main.py terraform us-west-1  ``
This will login to your us-west-1 region, extract the configuration, and output a terraform configuration file that matches your us-west-1 cloud.  

# File Structure
├── aws.py  
├── LICENSE  
├── main.py  
├── nimbusdisplay.py  
├── README.md  
├── runtest.sh  
├── terraform  
│   ├── main.tf  
│   └── variables.tf  
├── terraformhandler.py  
├── test.sh  
├── TODO  
└── utils.py  

