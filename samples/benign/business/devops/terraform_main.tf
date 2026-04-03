# Generated: 2026-04-02 11:55:15.209950
# Type: Benign DevOps Sample

# Terraform AWS 配置 - 良性
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {
    Name = "web-server"
  }
}

resource "aws_s3_bucket" "data" {
  bucket = "my-data-bucket"
}
