# nimbus buddy

# What is it?

A tools to help visualize your cloud infrastrructure and also allows you to output terraform configurations on your existing AWS.  Currently it supports VPCs, Subnets, and Instances.  

Support for Security Groups and Internet Gateways are on the short list.

In the future, I would like to extend nimbus buddy to work with other major cloud services such as Azure and Google Cloud Platform.  Another wishlist feature would be a way to migrate between AWS and Azure or Google Cloud Platform.

# ... but why?

I found AWS can be pretty daunting even if you have a background in networking.  It seemed pretty hard to get a quick overview of what was going on network-wise and possible security settings between hosts.  This tool will help automate the process of drilling down 3-4 clicks just to get the key network information you need.  

The ability to output terraform configuration files can help people migrate their existing cloud networks more easily, transition from prototype to full-scale automated deployments, or just have a backup of your AWS.

# Why not call it AWS Buddy?

I plan to extend the code so it will work with other cloud technologies, so I'd rather have a more agnostic name.  Currently I am most familiar with AWS.

# Requirements

- python3
- boto3
- tabulate

