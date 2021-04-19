import logging
import os

from django.http import Http404
from django.shortcuts import render
from dotenv import load_dotenv

from pull_request_info.utils.github_client import GithubClient

from .forms import GitHubUserForm

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s, %(message)s'))
logger.addHandler(handler)


def index(request):
    form = GitHubUserForm()
    return render(request, 'index.html', {'form': form})


def collect_data(username):
    token = os.getenv('GitHub_Token')
    client = GithubClient(token, username)
    repos = client.get_repos()
    data = []
    logger.debug('logging is started')
    if not isinstance(repos, list):
        reset_time = client.get_rate_limit_reset_time()
        raise Exception(
            f'API rate limit reached. {reset_time} hours until next request'
        )

    for repository in repos:
        if client.fork_approval(repository['name']):
            response = client.fork_owner(repository.get('name'))
            rep_data = {
                'github_login': repository['owner']['login'],
                'github_login_url': repository['owner']['html_url'],
                'name': repository['name'],
                'link': response['html_url'],
                'stars': response['stargazers_count']
            }

            pull_requests = client.get_merged_pr(
                repository['name'], response['owner']['login']
            )
            rep_data['merged_pull_requests'] = [
                {
                    'number': item['number'],
                    'url': item['html_url'],
                    'num_of_comments': item['comments']
                } for item in list(filter(
                    lambda n: n['user']['login'] == username, pull_requests
                ))
            ]

            pull_requests = client.get_unmerged_pr(
                repository['name'], response['owner']['login']
            )
            rep_data['unmerged_pull_requests'] = [
                {
                    'number': item['number'],
                    'url': item['html_url'],
                    'num_of_comments': item['comments']
                } for item in list(filter(
                    lambda n: n['user']['login'] == username, pull_requests
                ))
            ]

            data.append(rep_data)
    logger.debug(data)
    return data


def result(request):
    form = GitHubUserForm(request.POST)
    if form.is_valid():
        context = {
            'data': collect_data(form.cleaned_data['GitHubUser'])
        }
        return render(request, 'result.html', context)
    raise Http404
