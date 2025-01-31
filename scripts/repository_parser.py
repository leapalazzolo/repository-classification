import json
import requests
import os

token = os.getenv("GITHUB_TOKEN")
repo_file = os.environ.get("REPOSITORY_JSON", "data/repository.json")
repo_full_file = os.environ.get("REPOSITORY_FULL_JSON", "data/repository_full.json")

headers = {
    "Authorization": f"Bearer {token}",
    "X-GitHub-Api-Version": "2022-11-28",
    "Accept": "application/vnd.github+json",
}
# Read the JSON file
with open(repo_file, "r", encoding="utf-8") as file:
    data = json.load(file)

# Add "project", "icon", "topics", "about", and "languages" properties to each object
for item in data["repositories"]:
    repository_url = item["repository_url"]
    item["value"] = repository_url.split("/")[-2] + "/" + repository_url.split("/")[-1]

    # Fetch the repository details to get additional information
    try:
        repo_details = requests.get(
            f'https://api.github.com/repos/{item["value"]}',
            headers=headers if token else {},
        )
        repo_details.raise_for_status()  # Raise an error for bad responses
        repo_data = repo_details.json()
        languages = requests.get(repo_data["languages_url"], headers=headers).json()
        languages_names = [l.lower() for l in languages.keys()]
        # Extracting topics, about, and languages
        item["topics"] = repo_data["topics"]
        item["about"] = repo_data["description"]
        item["languages"] = languages_names

        # Fetching the icon URL
        item["icon"] = repo_data["owner"]["avatar_url"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository details for {item['value']}: {e}")
        item["topics"] = []
        item["about"] = None
        item["languages"] = None
        item["icon"] = None

# Save the modified data to a new JSON file
with open(repo_full_file, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

print("Script executed successfully.")
