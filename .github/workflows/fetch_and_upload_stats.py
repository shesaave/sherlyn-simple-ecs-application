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

def fetch_num_open_issues(current_date, all_issues):  
  today = current_date
  start_of_day = datetime.combine(today, datetime.min.time())
  end_of_day = datetime.combine(today, datetime.max.time())
  
  open_issues_count = 0
  
  for issue in all_issues:
    created_at = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    closed_at = issue[ 'closed_at']
    if closed_at:
      closed_at = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ")
    if created_at <= end_of_day and (closed_at is None or closed_at >= start_of_day):
      open_issues_count += 1
  
  return open_issues_count

def fetch_num_open_prs(current_date, url_prs):
  today = current_date
  today = current_date
  start_of_day = datetime.combine(today, datetime.min.time())
  end_of_day = datetime.combine(today, datetime.max.time())
  
  open_prs_count = 0
  
  for pr in all_prs:
    created_at = datetime.strptime(pr['created_at'], "%Y-%m-%dT%H:%M:%SZ")
    closed_at = pr['closed_at']
    if closed_at:
      closed_at = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ")
    if created_at <= end_of_day and (closed_at is None or closed_at >= start_of_day):
      open_prs_count += 1
  
  return open_prs_count


if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("Usage: python fetch_and_upload_stats.py <start_date> <end_date>")
    sys.exit(1)

  start_date = datetime.fromisoformat(sys.argv[1])
  end_date = datetime.fromisoformat(sys.argv[2])

  url_issues = f"{GITHUB_API_URL}/repos/aws-actions/{REPO_NAME}/issues?state=all"
  all_issues = fetch_data(url_issues)

  url_prs = f"{GITHUB_API_URL}/repos/aws-actions/{REPO_NAME}/pulls?state=all"
  all_prs = fetch_data(url_prs)

  current_date = start_date
  output = "|  |  |  | + "\n" + |--|--|--|" +"\n" + "| Date | Number of PRs | Number of Issues |"
  while current_date <= end_date:
    num_open_issues = fetch_num_open_issues(current_date, all_issues)
    num_open_prs = fetch_num_open_prs(current_date, all_prs)
    # num_closed_prs = fetch_num_closed_prs_yesterday()

    # output = output + "\nDate:" + current_date.strftime("%M:%D:%Y")
    output = output + "\n" + "| " + str(num_open_prs) + " |" + "| " +  str(num_open_issues- num_open_prs)+ " |"    
    current_date += timedelta(days=1)
  print(output)
