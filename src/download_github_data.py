''' This script downloads recent commits and issues from the CPython GitHub repository
    using the GitHub API and saves them as JSON files locally.'''
import requests
import json
import time
import os

TOKEN = os.getenv("GITHUB_API_TOKEN")
REPO = "python/cpython"
HEADERS = {"Authorization": f"token {TOKEN}"}

def fetch_commits():
    '''function to fetch recent commits from the CPython GitHub repository and save them to a JSON file.'''
    url = f"https://api.github.com/repos/{REPO}/commits"
    commits = []
    params = {"per_page": 100}
    for page in range(1, 21):
        params['page'] = page
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code != 200:
            print(resp.json())
            break
        data = resp.json()
        if not data:
            break
        commits.extend(data)
        time.sleep(1)
    with open("data/json/git_commits.json", "w", encoding="utf-8") as f:
        json.dump(commits, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(commits)} commits")

def fetch_issues():
    '''function to fetch recent issues from the CPython GitHub repository and save them to a JSON file.'''
    url = f"https://api.github.com/repos/{REPO}/issues"
    issues = []
    params = {"state": "all", "per_page": 100}
    for page in range(1, 6):
        params['page'] = page
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code != 200:
            print(resp.json())
            break
        data = resp.json()
        issues.extend(data)
        time.sleep(1)
    with open("data/json/git_issues.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(issues)} issues")

if __name__ == "__main__":
    fetch_commits()
    fetch_issues()
