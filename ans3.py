import boto3
from datetime import datetime, timedelta

def regions():
    ce = boto3.client('ce', region_name='eu-north-1')
    
    end = datetime.today().date()
    start = end - timedelta(days=90)
    
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start.strftime('%Y-%m-%d'),
            'End': end.strftime('%Y-%m-%d')
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'REGION'
            }
        ]
    )
    print (response)
    billed_regions = set()
    
    for result in response['ResultsByTime']:
        for group in result['Groups']:
            region = group['Keys'][0]
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            if amount > 0 and region not in ['NoRegion', 'global']:
                billed_regions.add(region)
    
    print("Regions are:", list(billed_regions))


if __name__ == "__main__":
    regions()
