import requests


def get_github_repo_contents(repo_url, access_token=None):
    if repo_url.endswith("/"):
        repo_url = repo_url[:-1]
    parts = repo_url.replace("https://github.com/", "").split("/")
    if len(parts) != 2:
        return "Error: Incorrect URL format. It should be https://github.com/owner/repository"
    owner, repo = parts
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    headers = {}

    if access_token:
        headers["Authorization"] = f"token {access_token}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return generate_markdown(data, access_token=access_token)
    except requests.HTTPError as e:
        if e.response.status_code in [401, 403, 404]:
            print(
                "Access error or repository not found. The repository might be private or the URL is incorrect."
            )
            print(
                "Please enter your GitHub Access Token for access to a private repository:"
            )
            access_token = input("GitHub Access Token: ")
            if access_token:
                return get_github_repo_contents(repo_url, access_token)
            else:
                return "Error: No Access Token was entered."
        else:
            return f"Error communicating with GitHub API: {e}"
    except requests.RequestException as e:
        return f"Error communicating with GitHub API: {e}"


def generate_markdown(files, path="", level=0, access_token=None):
    markdown = ""
    for file in files:
        if file["type"] == "dir":
            markdown += f"{'  ' * level}- {file['name']}/\n"
            subdir_response = requests.get(
                file["url"],
                headers=(
                    {"Authorization": f"token {access_token}"} if access_token else {}
                ),
            )
            subdir_response.raise_for_status()
            subdir_data = subdir_response.json()
            markdown += generate_markdown(
                subdir_data, file["path"], level + 1, access_token
            )
        else:
            markdown += f"{'  ' * level}- {file['name']}\n"
    return markdown


def main():
    repo_url = input("Enter the URL of the GitHub repository: ")
    result = get_github_repo_contents(repo_url)
    print(result)


if __name__ == "__main__":
    main()
