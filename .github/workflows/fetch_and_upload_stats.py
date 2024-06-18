import requests
import time
import boto3
import json
import os
import sys
from datetime import datetime, timedelta

# GitHub API details
GITHUB_API_URL = "https://api.github.com"
REPO_NAME = os.getenv('REPO_NAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# AWS CLoudwatch details
AWS_REGION = os.getenv('AWS_REGION')
NAMESPACE = os.getenv('NAMESPACE')

# Initialize CloudWatch client with specified region
client = boto3.client(
  'cloudwatch',
  aws_access_key_id = AWS_ACCESS_KEY_ID,
  aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
  region_name = AWS_REGION  
)

# Headers for GitHub API request
headers = {
  "Authorization":f"token {GITHUB_TOKEN}"
}

def fetch_data(url):
  print(f"URL: {url}")
  items = []
  while url:
    while True:
      response = requests.get(url, headers=headers)
      if response.status_code == 200:
        items.extend(response.json())
        url = response.links.get('next', {}).get('url')
        break
        # stats = response.json()
        # num_data = len(stats)
        # return num_data
      elif response.status_code == 202:
        print("Got 202, Wating...")
        time.sleep(30)
      else:
        print(f"Failed to fecth data: {response.status_code}")
        return None
  return items

def fetch_num_open_issues(current_date):  
  today = current_date
  start_of_day = datetime.combine(today, datetime.min.time())
  end_of_day = datetime.combine(today, datetime.max.time())
  
  url_issues = f"{GITHUB_API_URL}/repos/aws-actions/{REPO_NAME}/issues"
  all_issues = fetch_data(url_issues)

  open_issues_count = 0
  
  for issue in all_issues:
    created_at = datetime.strptime(issue['created_at'])
    closed_at = issue[ 'closed_at']
    if closed_at:
      closed_at = datetime.strptime(closed_at)
    if created_at <= end_of_day and (closed_at is None or closed_at >= start_of_day):
      open_issues_count += 1
  
  return open_issues_count

def fetch_num_open_prs(current_date):
  today = current_date
  today = current_date
  start_of_day = datetime.combine(today, datetime.min.time())
  end_of_day = datetime.combine(today, datetime.max.time())
  
  url_prs = f"{GITHUB_API_URL}/repos/aws-actions/{REPO_NAME}/pulls

  all_prs = fetch_data(url_prs)

    open_prs_count = 0
  
  for pr in all_prs:
    created_at = datetime.strptime(issue['created_at'])
    closed_at = issue['closed_at']
    if closed_at:
      closed_at = datetime.strptime(closed_at)
    if created_at <= end_of_day and (closed_at is None or closed_at >= start_of_day):
      open_prs_count += 1
  
  return open_prs_count

def fetch_num_closed_issues():
  url_closed_issues = f"{GITHUB_API_URL}/repos/aws-actions/{REPO_NAME}/issues?state=closed"
  return fetch_data(url_closed_issues)

# def fetch_num_closed_prs_yesterday():
#   today = datetime.utcnow().date()
#   yesterday = today - timedelta(days=1)
#   start_of_yesterday = datetime.combine(yesterday, datetime.min.time())
#   end_of_yesterday = datetime.combine(yesterday, datetime.max.time())
#   url_closed_prs_yesterday = f"{GITHUB_API_URL}/repos/aws-actions/{REPO_NAME}/issues?state=closed&since={start_of_yesterday.isoformat()}&until={end_of_yesterday.isoformat()}"
#   return fetch_data(url_closed_prs_yesterday)

def upload_metrics_to_cloudwatch(metrics):
  metric_data = []
  for metric_name, value in metrics.items():
    metric_data.append({
      'MetricName':metric_name,
      'Value':value,
      'Unit':'Count',
      'Timestamp':metrics['Timestamp']
    })
    response = client.put_metric_data(Namespace = NAMESPACE, MetricData = metric_data)
    print("Uploaded metrics to cloudwatch:", response)

  # if num_issues is not None and num_prs_open is not None:
  #   # put metric data to CloudWatch
  #   print(f"Number of PRs: {num_prs_open}")
  #   print(f"Number of Issues: {num_issues}")
  #   response = client.put_metric_data(
  #     Namespace = NAMESPACE,
  #     MetricData = [
  #       {
  #         'MetricName':f'NumberOfOpenIssues.{REPO_NAME}',
  #         'Value':num_issues,
  #         'Unit':'Count'
  #       },
  #       {
  #         'MetricName':f'NumberOfOpenPRs.{REPO_NAME}',
  #         'Value':num_prs_open,
  #         'Unit':'Count'
  #       },
  #       {
  #         'MetricName':f'NumberOfPRsClosed.{REPO_NAME}',
  #         'Value':num_prs_closed_yesterday,
  #         'Unit':'Count'
  #       }
  #     ]
  #   )
  #   print("Uploaded metrics to cloudwatch:", response)
  # else:
  #   print("No metrics to Upload")

if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("Usage: python fetch_and_upload_stats.py <start_date> <end_date>")
    sys.exit(1)

  start_date = datetime.fromisoformat(sys.argv[1])
  end_date = datetime.fromisoformat(sys.argv[2])

  current_date = start_date
  output = ""
  while current_date <= end_date:
    num_open_issues = fetch_num_open_issues(current_date)
    num_open_prs = fetch_num_open_prs(current_date)
    # num_closed_prs = fetch_num_closed_prs_yesterday()

    output = output + "\nDate:" + current_date.strftime("%M:%D:%Y")
    output = output + "\nOpen PRs:" + str(num_open_prs) + "\nOpen Issues:" + str(num_open_issues- num_open_prs)
    output = output + "\n"
    

    # metrics = {
    #   'NumberOfOpenIssues': num_open_issues - num_open_prs,
    #   'NumberOfOpenPRs': num_open_prs,
    #   'Timestamp': current_date
    # }
    
    # upload_metrics_to_cloudwatch(metrics)
    current_date += timedelta(days=1)
  print(output)
