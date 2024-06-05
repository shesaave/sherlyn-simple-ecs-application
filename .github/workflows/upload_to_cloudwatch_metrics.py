import boto3
import os
import json

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
NAMESPACE = os.getenv('NAMESPACE')

client = boto3.client(
  'cloudwatch',
  aws_access_key_id = AWS_ACCESS_KEY_ID,
  aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
  region_name = AWS_REGION  
)

with open('repo_stats.json', 'r') as f:
  data = json.load(f)

metric_data = []
for contributor in data:
  contributor_name = contributor['author']['login']
  print(f"weeks {weeks}")
  print("********************************************")
  for week in contributor['weeks']:
    print(f"week {week}")
    print("********************************************")
    metric_data.append({
      'MetricName': 'Commits',
      'Dimensions': [
        {'Name': 'Contributor',
        'Value': contributor_name}
      ],
      'Timestamp': int(week['w']),
      'Value': week['c'],
      'Unit': 'Count'
    })

response = client.put_metric_data(
  Namespace = NAMESPACE,
  MetricData = metric_data
)

print(f"Data uploaded to CloudWatch namespace {NAMESPACE}")
