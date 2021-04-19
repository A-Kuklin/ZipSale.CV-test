from datetime import datetime, timezone

import requests


class GithubClient:
    def __init__(self, token, username):
        self.headers = {
            'Authorization': f'token {token}',
        }
        self.username = username

    def get_rate_limit_reset_time(self):
        response = requests.get('https://api.github.com/users/octocat')
        reset_time = datetime.fromtimestamp(
            int(response.headers.get('X-RateLimit-Reset', 0)), timezone.utc)
        return reset_time - datetime.now(timezone.utc)

    def get_repos(self):
        response = requests.get(
            f'https://api.github.com/users/{self.username}/repos',
            headers=self.headers)
        return response.json()

    def get_merged_pr(self, repos_name, owner):
        response = requests.get(
            f'https://api.github.com/search/issues?'
            f'q=is:pr+is:merged+repo:{owner}/{repos_name}',
            headers=self.headers,
        ).json()
        return response['items']

    def get_unmerged_pr(self, repos_name, owner):
        response = requests.get(
            f'https://api.github.com/search/issues?'
            f'q=is:pr+is:unmerged+repo:{owner}/{repos_name}',
            headers=self.headers,
        ).json()
        return response['items']

    def fork_approval(self, repos_name):
        response = requests.get(
            f'https://api.github.com/repos/{self.username}/{repos_name}',
            headers=self.headers,
        ).json()
        if response['fork']:
            owner = response['parent']['owner']['login']
            approval = requests.get(
                f'https://api.github.com/search/issues?'
                f'q=is:pr+is:merged+repo:{owner}/{repos_name}',
                headers=self.headers,
            ).json()
            try:
                if approval['items'][0]['user']['login'] == self.username:
                    return True
                else:
                    return False
            except Exception:
                return False
        else:
            return False

    def fork_owner(self, repos_name):
        response = requests.get(
            f'https://api.github.com/repos/{self.username}/{repos_name}',
            headers=self.headers,
        ).json()
        owner = response['parent']['owner']['login']
        owner_response = requests.get(
            f'https://api.github.com/repos/{owner}/{repos_name}',
            headers=self.headers
        )
        return owner_response.json()
