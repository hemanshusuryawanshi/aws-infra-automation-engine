import boto3
import json
import time
import uuid
import sys

# Targeting Mumbai region as the baseline infrastructure zone
REGION = 'ap-south-1'

# Initialize low-level AWS service clients via boto3
try:
    ec2_client = boto3.client('ec2', region_name=REGION)
    s3_client = boto3.client('s3', region_name=REGION)
    iam_client = boto3.client('iam')
except Exception as e:
    print(f"❌ Initialization Failed: Verify local AWS credentials. Error: {e}")
    sys.exit(1)

def print_banner():
    """Outputs a clean, professional CLI interface banner."""
    print("=" * 60)
    print("      AWS INFRASTRUCTURE AUTOMATION ENGINE v1.0.0      ")
    print("=" * 60)
    print("📍 Region Target : ap-south-1 (Mumbai)")
    print("🛠️ Runtime       : Python 3 / Boto3 SDK")
    print("=" * 60 + "\n")

def create_s3_bucket():
    """Generates a globally unique S3 bucket for data storage."""
    bucket_name = f"hs-automated-data-bucket-{uuid.uuid4().hex[:8]}"
    print(" [PHASE 1] Deploying Global Storage Instance...")
    print(f"   └─ Target Identifier: {bucket_name}")
    
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': REGION}
        )
        print("   └─ Status: 🟢 DEPLOYED SUCCESSFUL\n")
        return bucket_name
    except Exception as e:
        print(f"   └─ Status: 🔴 FAILED to create S3 bucket: {e}")
        sys.exit(1)

def create_iam_role_and_profile():
    """Assembles the security boundaries: IAM role & EC2 instance profile."""
    role_name = 'EC2_S3_Access_Role_Auto'
    profile_name = 'EC2_S3_Instance_Profile_Auto'
    
    print(" [PHASE 2] Establishing Identity & Access Management...")
    print(f"   └─ Provisioning IAM Role: {role_name}")
    
    # Trust policy blueprint letting EC2 assume this identity safely
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }
    
    try:
        # 1. Create the IAM Role
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy)
        )
        
        # 2. Attach managed policy for S3 permissions
        iam_client.attach_role_policy(
            RoleName=role_name,
            PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
        )
        print("   └─ Policy Status: 🔐 Linked AmazonS3FullAccess")

        # 3. Create and bind Instance Profile container for the EC2 node
        iam_client.create_instance_profile(InstanceProfileName=profile_name)
        iam_client.add_role_to_instance_profile(
            InstanceProfileName=profile_name,
            RoleName=role_name
        )
        print(f"   └─ Instance Profile Created: {profile_name}")
        print("   └─ Status: ⏳ Synchronizing cluster permissions (10s)...")
        time.sleep(10) # Essential to allow policy propagation across global AWS layers
        print("   └─ Status: 🟢 SYNCHRONIZED\n")
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        print("   └─ Status: ⚠️ Resources exist. Re-using operational roles.\n")
    except Exception as e:
        print(f"   └─ Status: 🔴 IAM Configuration Failed: {e}")
        sys.exit(1)

    return profile_name

def launch_ec2_instance(profile_name):
    """Dynamically resolves the newest Amazon Linux image and deploys the instance."""
    print(" [PHASE 3] Orchestrating Elastic Compute Cloud (EC2)...")
    print("   └─ Querying AWS Systems Manager for latest stable AMI...")
    
    try:
        # Dynamically query the public systems manager path for the optimal image ID
        ssm_client = boto3.client('ssm', region_name=REGION)
        ami_response = ssm_client.get_parameter(
            Name='/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
        )
        ami_id = ami_response['Parameter']['Value']
        print(f"   └─ Resolved Image ID: {ami_id}")

        # Deploy the virtual machine tied to our IAM profile
        instances = ec2_client.run_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType='t3.micro',
            IamInstanceProfile={'Name': profile_name},
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': 'Automated-Boto3-Server'}]
            }]
        )
        
        instance_id = instances['Instances'][0]['InstanceId']
        print(f"   └─ Instance Reference: {instance_id}")
        print("   └─ Status: 🟢 BOOTING INITIALIZATION\n")
        return instance_id
    except Exception as e:
        print(f"   └─ Status: 🔴 Compute Deployment Failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print_banner()
    
    bucket = create_s3_bucket()
    iam_profile = create_iam_role_and_profile()
    ec2_id = launch_ec2_instance(iam_profile)
    
    print("=" * 60)
    print("🎯 DEPLOYMENT ORCHESTRATION COMPLETE")
    print("=" * 60)
    print(f"📦 Storage Endpoint : {bucket}")
    print(f"🛡️ Security Profile : {iam_profile}")
    print(f"🖥️ Virtual Server   : {ec2_id}")
    print("=" * 60)