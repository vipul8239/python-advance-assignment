import boto3
import csv

iam_client = boto3.client('iam')
ec2_client = boto3.client('ec2')

def check_iam_roles():
    roles = iam_client.list_roles()['Roles']
    flagged_roles = []

    for role in roles:
        role_name = role['RoleName']
        attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
        
        for policy in attached_policies:
            if policy['PolicyName'] == 'AdministratorAccess': 
                flagged_roles.append([role_name, policy['PolicyName']])


    with open('iam_roles_with_admin_access.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['IAMRoleName', 'Policy Name'])
        writer.writerows(flagged_roles)
    print("IAM Roles check completed. Output: iam_roles_with_admin_access.csv")


def check_mfa_enabled():
    users = iam_client.list_users()['Users']
    flagged_users = []

    for user in users:
        mfa_devices = iam_client.list_mfa_devices(UserName=user['UserName'])['MFADevices']
        if not mfa_devices:  
            flagged_users.append([user['UserName']])

    with open('iam_users_without_mfa.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['IAMUserName'])
        writer.writerows(flagged_users)
    print("IAM Users MFA check completed. Output: iam_users_without_mfa.csv")


def check_security_groups():
    security_groups = ec2_client.describe_security_groups()['SecurityGroups']
    flagged_sgs = []

    for sg in security_groups:
        for rule in sg.get('IpPermissions', []):
            for ip_range in rule.get('IpRanges', []):
                if ip_range.get('CidrIp') == '0.0.0.0/0':  
                    flagged_sgs.append([sg['GroupId'], rule.get('FromPort', 'All'), rule.get('ToPort', 'All'), rule['IpProtocol']])

    with open('publicly_accessible_security_groups.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SecurityGroupID', 'FromPort', 'ToPort', 'Protocol'])
        writer.writerows(flagged_sgs)
    print("Security Groups check completed. Output: publicly_accessible_security_groups.csv")

def check_unused_key_pairs():
    key_pairs = ec2_client.describe_key_pairs()['KeyPairs']
    used_keys = set()
    reservations = ec2_client.describe_instances()['Reservations']

    for reservation in reservations:
        for instance in reservation['Instances']:
            if 'KeyName' in instance:
                used_keys.add(instance['KeyName'])

    unused_keys = [[key['KeyName']] for key in key_pairs if key['KeyName'] not in used_keys]


    with open('unused_ec2_key_pairs.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['KeyName'])
        writer.writerows(unused_keys)
    print("EC2 Key Pairs check completed. Output: unused_ec2_key_pairs.csv")

if __name__ == "__main__":
    check_iam_roles()
    check_mfa_enabled()
    check_security_groups()
    check_unused_key_pairs()
    print("Security checks completed successfully!")
