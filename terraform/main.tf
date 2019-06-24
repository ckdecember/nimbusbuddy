provider "aws" {
            region = "us-west-1"
        }
resource "aws_vpc" "vpc-02e38283227fffc09" {
                cidr_block = "${var.var_vpc-02e38283227fffc09}"
                tags = {
                    Name = "new VPC"
                }
            }
resource "aws_subnet" "subnet-0ae683a4fe4e3cabc" {
                vpc_id = "${aws_vpc.vpc-02e38283227fffc09.id}"
                cidr_block = "${var.var_subnet-0ae683a4fe4e3cabc}"
                tags = {
                    Name = "Land of Robots"
                }
            }
resource "aws_instance" "i-081e3897ada7d1d9c" {
            instance_type = "t2.micro"
            ami = "ami-06397100adf427136"
            subnet_id = "${aws_subnet.subnet-0ae683a4fe4e3cabc.id}"
            tags = {
                Name = "drone3"
            }
        }
resource "aws_instance" "i-0e121504fea1f41ff" {
            instance_type = "t2.micro"
            ami = "ami-06397100adf427136"
            subnet_id = "${aws_subnet.subnet-0ae683a4fe4e3cabc.id}"
            tags = {
                Name = "drone2"
            }
        }
resource "aws_instance" "i-051c348cacd7b49ea" {
            instance_type = "t2.micro"
            ami = "ami-06397100adf427136"
            subnet_id = "${aws_subnet.subnet-0ae683a4fe4e3cabc.id}"
            tags = {
                Name = "drone1"
            }
        }
