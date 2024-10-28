from urllib import response
import requests
import typing as t
from agent.helper import DiffFormatter

from composio import action

DIFF_URL = "https://github.com/{owner}/{repo}/pull/{pull_number}.diff"
PR_URL = "https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"


@action(toolname="github")
def get_pr_diff(owner: str, repo: str, pull_number: str, thought: str) -> str:
    """
    Get .diff data for a github PR.

    :param owner: Name of the owner of the repository.
    :param repo: Name of the repository.
    :param pull_number: Pull request number to retrive the diff for.
    :param thought: Thought to be used for the request.

    :return diff: .diff content for give pull request.
    """
    diff_text = requests.get(
        DIFF_URL.format(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
        )
    ).text
    return DiffFormatter(diff_text).parse_and_format()


@action(toolname="github")
def get_pr_metadata(owner: str, repo: str, pull_number: str, thought: str) -> t.Dict:
    """
    Get metadata for a github PR.

    :param owner: Name of the owner of the repository.
    :param repo: Name of the repository.
    :param pull_number: Pull request number to retrive the diff for.
    :param thought: Thought to be used for the request.

    :return metadata: Metadata for give pull request.
    """
    
    data = requests.get(
        PR_URL.format(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
        )
    ).json()

    response = {
        "title": data["title"],
        "comments": data["comments"],
        "commits": data["commits"],
        "additions": data["additions"],
        "deletions": data["deletions"],
        "changed_files": data["changed_files"],
        "head": {
            "ref": data["head"]["ref"],
            "sha": data["head"]["sha"],
        },
        "base": {
            "ref": data["base"]["ref"],
            "sha": data["base"]["sha"],
        }
    }
    return response