import boto3
import sys
import time

REGION = 'ap-south-1'
ec2_client = boto3.client('ec2', region_name=REGION)
s3_client = boto3.client('s3', region_name=REGION)
s3_resource = boto3.resource('s3', region_name=REGION)
iam_client = boto3.client('iam')

print("=" * 60)
print("      AWS INFRASTRUCTURE DESTRUCTION ENGINE v1.0.0      ")
print("=" * 60)

# 1. Terminate the EC2 Server
print("[PHASE 1] Scanning for automated compute instances...")
response = ec2_client.describe_instances(
    Filters=[{'Name': 'tag:Name', 'Values': ['Automated-Boto3-Server']}]
)

instances_to_term = []
for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        if instance['State']['Name'] != 'terminated':
            instances_to_term.append(instance['InstanceId'])

if instances_to_term:
    print(f"   └─ Found active nodes: {instances_to_term}")
    ec2_client.terminate_instances(InstanceIds=instances_to_term)
    print("   └─ Status: 🔴 TERMINATION COMMAND ISSUED")
else:
    print("   └─ Status: ⚪ No active compute nodes discovered.")

# 2. Scrub and Destroy S3 Buckets
print("\n[PHASE 2] Locating automated object storage instances...")
buckets = s3_client.list_buckets()
for b in buckets['Buckets']:
    if b['Name'].startswith('hs-automated-data-bucket-'):
        print(f"   └─ Purging storage contents: {b['Name']}")
        # S3 buckets must be entirely empty before they can be deleted
        bucket_obj = s3_resource.Bucket(b['Name'])
        bucket_obj.objects.all().delete()
        
        s3_client.delete_bucket(Bucket=b['Name'])
        print("   └─ Status: 🗑️ BUCKET PERMANENTLY DELETED")

# 3. Teardown IAM Security Configurations
print("\n[PHASE 3] Revoking identity system mappings...")
profile_name = 'EC2_S3_Instance_Profile_Auto'
role_name = 'EC2_S3_Access_Role_Auto'

try:
    # Remove role from instance profile first
    iam_client.remove_role_from_instance_profile(
        InstanceProfileName=profile_name,
        RoleName=role_name
    )
    iam_client.delete_instance_profile(InstanceProfileName=profile_name)
    print(f"   └─ Removed Instance Profile: {profile_name}")
except iam_client.exceptions.NoSuchEntityException:
    print("   └─ Profile clean.")

try:
    # Detach policy and delete role
    iam_client.detach_role_policy(
        RoleName=role_name,
        PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
    )
    iam_client.delete_role(RoleName=role_name)
    print(f"   └─ Destroyed IAM Identity Access Role: {role_name}")
except iam_client.exceptions.NoSuchEntityException:
    print("   └─ Role clean.")

print("\n" + "=" * 60)
print("🎯 TEARDOWN COMPLETELY SUCCESSFUL. CLOUD REALM IS CLEAN.")
print("=" * 60)