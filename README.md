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

## Current app description:
I launched an Employee Directory app that uses DynamoDB as a key-value database to store employee information, along with an S3 bucket to store employee photos. The application runs in a custom VPC environment with configured route tables and an internet gateway to ensure secure and scalable networking. When an HTTP request is made, it is routed through an Application Load Balancer (ALB) to EC2 instances hosting the app across multiple Availability Zones. In case of high CPU usage, AWS Auto Scaling automatically scales the number of instances to handle the increased load. The web app displays the Availability Zone you are using and features a CPU-Stress Button for testing auto-scaling functionality.
When initializing the app, a one-time Lambda function deploys employee photos to the S3 bucket.

<img width="1323" alt="Screenshot 2024-09-18 at 22 13 18" src="https://github.com/user-attachments/assets/514da6b2-5814-4615-85ee-372bb260f01a">

<img width="1382" alt="Screenshot 2024-09-18 at 21 42 27" src="https://github.com/user-attachments/assets/dd1a9f46-b65a-4e29-b552-eea9a21355cf">

<img width="1419" alt="Screenshot 2024-09-18 at 21 41 50" src="https://github.com/user-attachments/assets/b8c27a5b-9e2a-4170-9a54-602543e05e99">

## Room for Improvement

* **Interactive Menu:** Develop an interactive menu for scaling resources up and down.
* **Resource Data Persistence:** Implement a feature to save application resource data, allowing it to be reloaded in case of errors or unexpected events.
* **Go serverless** using Amazon S# for static website hosting and use AWS Lambda for backend Processing triggered via Amazon API Gateway
* **Documentation:** Create comprehensive documentation and tutorials to guide users in setting up and using the application effectively.
* **Error Handling and Recovery:** Enhance error handling mechanisms and implement automated recovery processes to improve the application's resilience.


## Getting Started
To run the app, you need to create an IAM role named `EmployeeWebApp` (the name can be changed in the configuration files) that allows EC2 instances to call AWS services on your behalf.

### Required IAM Permissions

Your IAM user must have the following permissions:

      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:CreateSecurityGroup",
      "ec2:CreateVpc",
      "ec2:CreateSubnet",
      "ec2:TerminateInstances",
      "ec2:CreateKeyPair",
      "ec2:RunInstances",
      "ec2:DescribeInstances",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeVpcs",
      "ec2:DescribeKeyPairs",
      "ec2:DescribeRouteTables",
      "ec2:DescribeInternetGateways",
      "ec2:DescribeLaunchTemplates",
      "ec2:DescribeLaunchTemplateVersions",
      "ec2:DescribeLaunchTemplates",
      "ec2:ModifyVpcAttribute",
      "ec2:CreateTags",
      "ec2:CreateInternetGateway",
      "ec2:AttachInternetGateway",
      "ec2:DetachInternetGateway",
      "ec2:CreateRouteTable",
      "ec2:CreateRoute",
      "ec2:AssociateRouteTable",
      "ec2:DeleteVpc",
      "ec2:DeleteSubnet",
      "ec2:DeleteInternetGateway",
      "ec2:DeleteRouteTable",
      "ec2:DeleteKeyPair",
      "ec2:DeleteSecurityGroup",
      "s3:CreateBucket",
      "s3:ListBucket",
      "s3:ListBucketVersions",
      "s3:PutBucketPolicy",
      "s3:PutObject",
      "s3:GetBucketVersioning",
      "s3:DeleteBucket",
      "s3:DeleteObject",
      "s3:DeleteObjectVersion",
      "dynamodb:CreateTable",
      "dynamodb:ListTables",
      "dynamodb:DescribeTable",
      "dynamodb:DeleteTable",
      "elasticloadbalancing:CreateLoadBalancer",
      "elasticloadbalancing:DescribeLoadBalancers",
      "elasticloadbalancing:CreateListener",
      "elasticloadbalancing:CreateTargetGroup",
      "elasticloadbalancing:RegisterTargets",
      "elasticloadbalancing:DescribeTargetGroups",
      "elasticloadbalancing:AddTags",
      "elasticloadbalancing:DeleteLoadBalancer",
      "elasticloadbalancing:DeleteListener",
      "elasticloadbalancing:DeleteTargetGroup",
      "autoscaling:CreateAutoScalingGroup",
      "autoscaling:UpdateAutoScalingGroup",
      "autoscaling:PutScalingPolicy",
      "autoscaling:DescribePolicies",
      "autoscaling:DescribeAutoScalingGroups",
      "autoscaling:DeleteAutoScalingGroup",
      "autoscaling:DeletePolicy",
      "autoscaling:PutNotificationConfiguration",
      "ec2:DescribeLaunchTemplates",
      "ec2:CreateLaunchTemplate",
      "ec2:DeleteLaunchTemplate",
      "sns:CreateTopic",
      "iam:CreateRole",
      "iam:AttachRolePolicy",
      "iam:PutRolePolicy",
      "iam:PassRole",
      "iam:GetRole",
      "iam:DetachRolePolicy",
      "iam:DeleteRole",
      "lambda:CreateFunction",
      "lambda:GetFunction",
      "lambda:UpdateFunctionCode",
      "lambda:AddPermission",
      "lambda:InvokeFunction",
      "lambda:CreateEventSourceMapping",
      "lambda:DeleteFunction"


