variable "ami_id" {
    description = "incoming ami id"
    default = "ami-06397100adf427136"
}

variable "snoopdoggydog" {
    description = "hmmm"
    default = "I'm a lich! A dracoLich!"
}

variable "vpc_cidr" {
    description = "VPC's CIDR address"
    default = "10.0.0.0/16"
}

variables "subnet_cidr" {
    description = "Subnet's CIDR address"
    default = "10.0.1.0/24"
}

variables "region" {
    description = "AWS Region"
    default = "us-west-1"
}

variables "instance_type" {
    description = "AWS cpu/power type"
    default = "t2.micro"
}