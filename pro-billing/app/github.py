import time

from django.conf import settings

import jwt
import requests


def get_github_session():
    """
    Gets an authenticated session as the specific app installation
    with access to the forgepackages repo
    """
    time_since_epoch_in_seconds = int(time.time())

    payload = {
        "iat": time_since_epoch_in_seconds,
        "exp": time_since_epoch_in_seconds + (10 * 60),
        "iss": settings.GITHUB_APP_ID,
    }

    actual_jwt = jwt.encode(payload, settings.GITHUB_APP_PRIVATE_KEY, algorithm="RS256")

    response = requests.post(
        f"https://api.github.com/app/installations/{settings.GITHUB_APP_INSTALLATION_ID}/access_tokens",
        headers={"Authorization": f"Bearer {actual_jwt}"},
    )
    response.raise_for_status()
    token = response.json()["token"]

    session = requests.Session()
    session.headers.update(
        {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    )
    return session


# TODO staff view to show outstanding invitations?
# https://docs.github.com/en/rest/reference/collaborators#invitations


def invite_username_to_repo(username, repo):
    """
    You are limited to sending 50 invitations to a repository per 24 hour period.
    https://docs.github.com/en/rest/reference/collaborators#add-a-repository-collaborator
    """
    response = get_github_session().put(
        f"https://api.github.com/repos/{repo}/collaborators/{username}",
        json={"permission": "pull"},
    )
    response.raise_for_status()


def remove_username_from_repo(username, repo):
    response = get_github_session().delete(
        f"https://api.github.com/repos/{repo}/collaborators/{username}",
    )
    response.raise_for_status()
