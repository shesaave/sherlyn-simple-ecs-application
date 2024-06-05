import requests
import json
import os

GITHUB_API_URL = "https://api.github.com"
REPO_NAME = os.getenv('REPO_NAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

headers = {
  "Authorization":f"token {GITHUB_TOKEN}"
}

url = f"{GITHUB_API_URL}/repos/amazreech/{REPO_NAME}/stats/contributors"
print(f"URL: {url}")
response = requests.get(url, headers=headers)
print(f"response: {response}")

if response.status_code == 202:
  print("Got 202, Wating...")
  time.sleep(30)
  response = requests.get(url, headers=headers)

if response.status_code == 200:
  stats = response.json()
  with open('repo_stats.json', 'w') as f:
    json.dump(stats, f)
else:
  print(f"Failed to fecth data: {response.status_code}")
  exit(1)
