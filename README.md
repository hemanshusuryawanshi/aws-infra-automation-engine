\# AWS Infrastructure Automation Engine 🚀



An enterprise-grade, fully automated \*\*Infrastructure-as-Code (IaC)\*\* provisioning and lifecycle destruction engine built entirely with Python and the \*\*AWS Boto3 SDK\*\*.



This project bypasses the manual AWS Management Console entirely, demonstrating programmatic cloud orchestration, dynamic resource lifecycle management, and tokenless identity access boundaries.



\---



\## 🏗️ Architecture Blueprint \& Workflows



The framework handles two complete decoupled pipelines: \*\*Provisioning (`app.py`)\*\* and \*\*Teardown (`teardown.py`)\*\*.



\### 1. Provisioning Lifecycle (`app.py`)

\* \*\*Dynamic Object Storage:\*\* Automatically provisions a globally unique Amazon S3 bucket. It appends a dynamic hex UUID to the bucket identifier to completely eliminate global naming collisions.

\* \*\*Tokenless Identity Boundary:\*\* Assembles an IAM Role and couples it to an EC2 Instance Profile with `AmazonS3FullAccess` authorization. This allows the compute server to talk directly to the storage container using rotating internal cryptographic tokens—eliminating the security risk of hardcoded AWS Access Keys.

\* \*\*SSM-Managed Compute:\*\* Programmatically queries the public AWS Systems Manager (SSM) Parameter Store to resolve the latest stable Amazon Linux 2 AMI ID live, booting it instantly on a Free Tier eligible `t3.micro` EC2 node mapped with custom project tags.



\### 2. Teardown Lifecycle (`teardown.py`)

\* \*\*Targeted Compute Termination:\*\* Scans the active region, identifies the custom tagged compute resource, and securely executes a termination sequence.

\* \*\*Force-Purge Storage scrubbing:\*\* S3 buckets cannot be deleted while containing data. The destruction script systematically targets the automated bucket, purges all stored target objects, and strips down the bucket resource.

\* \*\*IAM De-provisioning:\*\* Seamlessly detaches operational security policies from the identity container, detaches the link configuration, and scrubs the IAM profile cleanly from your global account dashboard.



\---



\## 🎯 Production Use Case



Manual cloud environment configuration introduces severe human configuration errors, security openings, and "configuration drift". 



This engine provides full \*\*structural idempotency\*\*. If a DevOps or engineering group requires a clean, completely secure sandbox environment to run background automated parsing pipelines, they run this script once. They receive a fully functional, secured machine-and-storage framework in seconds, and can tear it completely down at the end of the operation using the teardown routine—keeping AWS cloud billing down to exactly zero.



\---



\## 🛠️ Tech Stack \& Dependencies



\* \*\*Development Language:\*\* Python 3.x

\* \*\*Cloud SDK:\*\* AWS Boto3

\* \*\*Core AWS Frameworks Utilized:\*\*

&#x20; \* \*\*IAM\*\* (Identity \& Access Management)

&#x20; \* \*\*Amazon S3\*\* (Simple Storage Service)

&#x20; \* \*\*Amazon EC2\*\* (Elastic Compute Cloud)

&#x20; \* \*\*AWS Systems Manager\*\* (SSM Parameter Store)



\---



\## 🚀 Execution \& UI Telemetry



\### Prerequisites

1\. Ensure your local machine has active credentials configured via the AWS CLI (`aws configure`).

2\. Install the target Python library:

&#x20;  ```bash

&#x20;  pip install boto3

