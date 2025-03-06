import boto3

def get_billed_regions():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    regions = [region["RegionName"] for region in ec2_client.describe_regions()["Regions"]]
    
    active_regions = set()
    for region in regions:
        try:
            ec2_client = boto3.client("ec2", region_name=region)
            instances = ec2_client.describe_instances()
            if any(r["Instances"] for r in instances["Reservations"]):
                active_regions.add(region)
        except Exception as e:
            print(f"Skipping region {region} due to error: {e}")
    
    return active_regions

def main():
    billed_regions = get_billed_regions()
    print("Regions where customer has resources:", billed_regions)

if __name__ == "__main__":
    main()
