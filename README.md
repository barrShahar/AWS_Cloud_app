# AWS Resource Manager Application - Working Progress

## Overview

This project is an **AWS Resource Manager** that automates the creation, management, and cleanup of AWS cloud resources for deploying scalable applications. It integrates various AWS services such as EC2, VPC, S3, RDS, Lambda, and Auto Scaling, offering an efficient and robust infrastructure setup using **object-oriented programming** principles.

The application is designed to manage AWS infrastructure programmatically with **Python**, utilizing **boto3** to interact with AWS services. It follows **SOLID design principles** and emphasizes clean, modular code through classes that handle different AWS components.

## Key Features

### Automated AWS Resource Management:
- **VPC creation** with custom subnets and security groups.
- Launch and configure **EC2 instances** with custom user data scripts.
- Configure and manage **Application Load Balancers (ALB)** and target groups.
- Set up and manage **RDS databases**.
- **Auto Scaling** configuration for handling dynamic scaling requirements.
- Manage **S3 buckets** and **Lambda functions**.

### OOP-Based Design:
- Follows **SOLID principles** with specialized classes for different AWS services, such as:
  - `AppManager`
  - `VPCManager`
  - `RDSManager`
      - `S3Manager`
      - `DynamoDbManager`
  - `ALBManager`
  - `AutoScalingManager`
- Ensures **separation of concerns**, making the code easy to extend and maintain.

## Getting Started
Todo..

