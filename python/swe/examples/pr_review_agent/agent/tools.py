import requests

from composio import action

DIFF_URL = "https://github.com/{owner}/{repo}/pull/{pull_number}.diff"


@action(toolname="github")
def get_diff(owner: str, repo: str, pull_number: str) -> str:
    """
    Get .diff data for a github PR.

    :param owner: Name of the owner of the repository.
    :param repo: Name of the repository.
    :param pull_number: Pull request number to retrive the diff for.

    :return diff: .diff content for give pull request.
    """
    return requests.get(
        DIFF_URL.format(
            owner=owner,
            repo=repo,
            pull_number=pull_number,
        )
    ).text


if __name__ == "__main__":
    print(get_diff.schema())
