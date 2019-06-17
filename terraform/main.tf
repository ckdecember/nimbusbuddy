provider "aws" {
    region = "us-west-1"
}

resource "aws_vpc" "vpc_007" {
  cidr_block = "10.0.0.0/16"
  tags = {
      Name = "The Lich's Den"
  }
}

resource "aws_subnet" "forLiches" {
  vpc_id     = "${aws_vpc.vpc_007.id}"
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "lich's subnet"
  }
}

resource "aws_instance" "dracolich1" {
  instance_type = "t2.micro"
  #ami = "ami-06397100adf427136"
  ami = "${var.ami_id}"
  subnet_id = "${aws_subnet.forLiches.id}"

  tags = {
    Name = "${var.snoopdoggydog}"
  }
}

