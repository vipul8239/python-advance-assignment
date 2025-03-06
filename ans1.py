import boto3
import csv

def get_ec2_instance_types():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    regions = [region["RegionName"] for region in ec2_client.describe_regions()["Regions"]]
    
    all_instances = []
    for region in regions:
        ec2_client = boto3.client("ec2", region_name=region)
        try:
            paginator = ec2_client.get_paginator("describe_instance_type_offerings")
            response_iterator = paginator.paginate(LocationType='region')
            instance_types = set()
            for response in response_iterator:
                for instance in response["InstanceTypeOfferings"]:
                    instance_types.add(instance["InstanceType"])
            
            for instance_type in instance_types:
                all_instances.append([region, instance_type])
        except Exception as e:
            print(f"Error fetching instance types for region {region}: {e}")
    
    return all_instances

def save_to_csv(data, filename="ec2_instance_types.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["region", "instance_type"])
        writer.writerows(data)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    instance_data = get_ec2_instance_types()
    save_to_csv(instance_data)
