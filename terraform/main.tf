provider "aws" {
    region = "${var.region}"
}

resource "aws_vpc" "vpc_007" {
  cidr_block = "${var.vpc_cidr}"
  tags = {
      Name = "The Lich's Den"
  }
}

resource "aws_subnet" "forLiches" {
  vpc_id     = "${aws_vpc.vpc_007.id}"
  cidr_block = "${var.subnet_cidr"

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

