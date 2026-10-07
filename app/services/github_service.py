import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def get_pull_request(owner, repo, pr_number):
    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/pulls/{pr_number}"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15,
    )

    if response.status_code == 404:
        raise ValueError("Pull request not found.")

    response.raise_for_status()

    return response.json()


def get_pull_request_files(owner, repo, pr_number):
    url = (
        f"{GITHUB_API_URL}/repos/"
        f"{owner}/{repo}/pulls/{pr_number}/files"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15,
    )

    response.raise_for_status()

    return response.json()