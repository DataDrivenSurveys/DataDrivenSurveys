#!/usr/bin/env python3
"""@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch).
"""
from __future__ import annotations

import traceback
from functools import cached_property
from typing import TYPE_CHECKING, Any

from github import ApplicationOAuth, Auth, Github
from github.GithubException import BadCredentialsException, GithubException

from ddsurveys.data_providers.bases import FormField, OAuthDataProvider
from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.get_logger import get_logger
from ddsurveys.variable_types import VariableDataType

__all__ = ["GitHubDataProvider"]

if TYPE_CHECKING:
    from collections.abc import Callable

    from github.AccessToken import AccessToken

    from ddsurveys.typings.variable_types import TVariableFunction

logger = get_logger(__name__)


class Account(DataCategory):

    data_origin = [
        {
            "method": "get_user",
            "endpoint": "https://api.github.com/user",
            "documentation": "https://docs.github.com/en/rest/reference/users",
        }
    ]

    custom_variables_enabled = False

    api: Github = None

    def fetch_data(self) -> list[dict[str, Any]]:
        return self.api.get_user()

    cv_attributes = [
        CVAttribute(
            name="name",
            label="Users Name",
            description="The name of the user.",
            attribute="name",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="Username",
            info="The name of the user.",
        ),
        CVAttribute(
            label="Creation Date",
            description="The date the repository was created.",
            attribute="created_at",
            name="creation_date",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2023-01-10T12:00:00.000",
            info="The date the account was created.",
        ),
    ]

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="creation_date",
            label="Account creation date",
            description="The date the user created their account.",
            test_value_placeholder="2020-01-01",
            data_type=VariableDataType.DATE,
            info="The date the account was created. It will be in the format YYYY-MM-DD.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.account_creation_date,
            data_origin=[
                {
                    "method": "get_user_repositories",
                    "endpoint": "https://api.github.com/users/[username]/repos",
                    "documentation": "https://docs.github.com/en/rest/reference/repos#list-repositories-for-a-user",
                }
            ],
        )
    ]


class Repositories(DataCategory):

    data_origin = [
        {
            "method": "get_user_repositories",
            "endpoint": "https://api.github.com/users/[username]/repos",
            "documentation": "https://docs.github.com/en/rest/reference/repos#list-repositories-for-a-user",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        return self.data_provider.get_user_repositories

    cv_attributes = [
        CVAttribute(
            name="name",
            label="Repository Name",
            description="The name of the repository.",
            attribute="name",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="MyRepo",
            info="The name of the repository.",
        ),
        CVAttribute(
            name="description",
            label="Description",
            description="The description of the repository.",
            attribute="description",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="A repository for XYZ project.",
            info="The description of the repository.",
        ),
        CVAttribute(
            label="Creation Date",
            description="The date the repository was created.",
            attribute="created_at",
            name="creation_date",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2023-01-10T12:00:00.000",
            info="The date the repository was created.",
        ),
        CVAttribute(
            name="stars",
            label="Star Count",
            description="The number of stars the repository has.",
            attribute="stargazers_count",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="100",
            info="The number of stars the repository has.",
            unit="stars",
        ),
        CVAttribute(
            label="Repository URL",
            description="The URL of the repository.",
            attribute="html_url",
            name="url",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="https://github.com/user/repo",
            info="The URL of the repository.",
        ),
        CVAttribute(
            label="Open Issues",
            description="The number of open issues the repository has.",
            attribute="open_issues",
            name="open_issues",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="10",
            info="The number of open issues the repository has.",
            unit="issues",
        ),
    ]

    builtin_variables = [
        # BuiltInVariable.create_instances(
        #     name="by_stars",
        #     label="Repositories by Stars",
        #     description="Repositories sorted from most stars to least stars. "
        #                 "Index 1 is the repository with the most stars, index 2 has the second most, and so on.",
        #     test_value_placeholder="MyTopRepo",
        #     data_type=VariableDataType.TEXT,
        #     info="Repositories sorted from most stars to least stars.",
        #     is_indexed_variable=True,
        #     index_start=1,
        #     index_end=5,
        #     extractor_func=lambda self, idx: self.repositories_by_stars(idx),
        #     data_origin=[{
        #         "method": "get_user_repositories",
        #         "endpoint": "https://api.github.com/users/[username]/repos",
        #         "documentation": "https://docs.github.com/en/rest/reference/repos#list-repositories-for-a-user",
        #     }]
        # )
    ]


class GitHubDataProvider(OAuthDataProvider):
    # Class attributes that need be re-declared or redefined in child classes
    # The following attributes need to be re-declared in child classes.
    # You can just copy and paste them into the child class body.
    all_initial_funcs: dict[str, Callable] = {}
    factory_funcs: dict[str, Callable] = {}
    variable_funcs: dict[str, TVariableFunction] = {}
    fields: list[dict[str, Any]] = {}

    token: AccessToken = None

    app_creation_url: str = "https://github.com/settings/apps/new"
    # instructions_helper_url: str = "https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app"

    # Unique class attributes go here
    _scopes = []

    _categories_scopes = {
        "Account": "read_user",
        "account": "read_user",
        "Repositories": "repo",
        "repositories": "repo",
    }

    form_fields = [
        FormField(
            name="client_id",
            type="text",
            required=True,
            data={
                # "helper_url": "https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app"
            },
        ),
        FormField(
            name="client_secret",
            type="text",
            required=True,
            data={
                # "helper_url": "https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app"
            },
        ),
    ]

    data_categories = [Account, Repositories]

    def __init__(self, **kwargs):
        """Args:
        client_id:
        client_secret:
        access_token:
        refresh_token:
        **kwargs:
        """
        super().__init__(**kwargs)
        self.api_client: Github
        self.oauth_client: ApplicationOAuth
        self.redirect_uri = self.get_redirect_uri()

        self.init_oauth_client()

        if self.access_token is not None and self.refresh_token is not None:
            self.init_api_client(self.access_token, self.refresh_token)

    # OAuthBase methods
    def init_api_client(
        self, access_token: str | None = None, refresh_token: str | None = None, code: str | None = None
    ) -> None:
        if access_token is not None:
            self.access_token = access_token
        if refresh_token is not None:
            self.refresh_token = refresh_token
        if code is not None:
            self.code = code

        auth = Auth.Token(access_token)

        self.api_client: Github = Github(auth=auth)

    def init_oauth_client(self, *args, **kwargs) -> None:
        g = Github()

        app = g.get_oauth_application(
            client_id=self.client_id, client_secret=self.client_secret
        )

        self.oauth_client: ApplicationOAuth = app

    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] | None = None
    ) -> str:
        # required_scopes = self.get_required_scopes(builtin_variables, custom_variables)
        #
        # if len(required_scopes) == 0:
        #     required_scopes = self.__class__._scopes
        #
        # required_scopes_str = "%20".join(required_scopes)
        # # For GitHub, you'd typically redirect users to a URL like below:
        # return f"https://github.com/login/oauth/authorize?client_id={self.client_id}&scope={required_scopes_str}"
        return f"https://github.com/login/oauth/authorize?client_id={self.client_id}"

    def get_client_id(self) -> str:
        return self.client_id

    def request_token(self, code: str) -> dict[str, Any]:

        try:

            g = Github()

            app = g.get_oauth_application(
                client_id=self.client_id, client_secret=self.client_secret
            )

            token = app.get_access_token(code)

            g = Github(auth=app.get_app_user_auth(token))

            user = g.get_user()

            return {
                "success": True,
                "access_token": token.token,
                "refresh_token": token.refresh_token,
                "user_id": user.id,
                "user_name": user.login,
            }
        except GithubException as e:
            logger.exception(f"Failed to request token: {e}")
            logger.debug(traceback.format_exc())
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.general_error",
            }

    def revoke_token(self, token: str) -> bool:
        # Revoking a token might be more involved and isn't directly supported by PyGithub.
        # One way is to delete a token using GitHub's Apps API, or you might just let it expire.
        # This is a placeholder, and you'd need to implement based on the exact requirements.
        return True

    # DataProvider methods
    def test_connection_before_extraction(self) -> bool:
        return self.test_connection()

    def test_connection(self) -> bool:
        """We try to send a wrong code to get_access_token and check if we get a BadCredentialsException
        If the request fails for bad_verification_code then the connection is valid
        If the request fails for any other reason, then the connection is not valid.

        Returns:
            True if the connection is valid, False otherwise.
        """
        try:
            self.oauth_client.get_access_token("wrong_code")
            return True

        except BadCredentialsException as e:
            reason = e.data

            if reason.get("error") == "bad_verification_code":
                return True

            logger.exception(
                f"Failed to connect to GitHub BadCredentialsException: {e}"
            )
            return False
        except GithubException as e:
            logger.exception(f"Failed to connect to GitHub: {e}")
            return False

    @cached_property
    def get_user_repositories(self) -> list:
        repos = self.api_client.get_user().get_repos()
        """
            Repository: https://pygithub.readthedocs.io/en/stable/github_objects/Repository.html
        """
        return [
            {
                "name": repo.name,
                "description": repo.description,
                "created_at": repo.created_at.isoformat(),  # "2021-08-10T12:00:00.000"
                "html_url": repo.html_url,
                "open_issues": repo.open_issues_count,
                "stargazers_count": repo.stargazers_count,
            }
            for repo in repos
        ]

    def repositories_by_stars(self, idx: int) -> str:
        repos = self.get_user_repositories
        # Sort the repositories by stars
        repos.sort(key=lambda repo: repo["stargazers_count"], reverse=True)
        return repos[idx - 1]["name"] if idx <= len(repos) else None

    @cached_property
    def account_creation_date(self) -> str:
        user = self.api_client.get_user()
        return user.created_at.isoformat().split("T")[0]
