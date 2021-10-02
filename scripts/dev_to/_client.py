from io import StringIO
import json, os, yaml
from ruamel.yaml import YAML
from re import I
from typing import Dict, List
from pydantic import parse_obj_as
import requests
from requests_toolbelt import sessions
from ._article import Article
from requests.packages.urllib3.util.retry import Retry

def str_presenter(dumper, data):
  if len(data.splitlines()) > 1:  # check for multiline string
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

class Client():

    class HttpAdapter(requests.adapters.HTTPAdapter):
        DEFAULT_TIMEOUT = 3

        def __init__(self, *args, **kwargs):
            self._timeout = self.DEFAULT_TIMEOUT
            if "timeout" in kwargs:
                self._timeout = kwargs["timeout"]
                del kwargs["timeout"]
            super().__init__(*args, **kwargs)

        def send(self, request, **kwargs):
            timeout = kwargs.get("timeout")
            if timeout is None:
                kwargs["timeout"] = self._timeout
            return super().send(request, **kwargs)


    BASE_URL = "https://dev.to/api"

    _session = None

    def __init__(self):
        self._api_token = os.environ.get("DEV_TO_API_TOKEN")
        if self._session is None:
            self._session = Client._create_session()

    @staticmethod
    def _create_session():
        session = sessions.BaseUrlSession(Client.BASE_URL)
        Client._configure_assert_status_hook(session)
        Client._configure_timeouts_and_retries(session)
        return session

    @staticmethod
    def _configure_assert_status_hook(session):
        session.hooks["response"] = [Client._assert_status_hook]

    @staticmethod
    def _assert_status_hook(response, *args, **kwargs):
        response.raise_for_status()

    @staticmethod
    def _configure_timeouts_and_retries(session):
        RETRY_STRATEGY = Retry(
            total = 3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=10
        )
        adapter = Client.HttpAdapter(max_retries=RETRY_STRATEGY)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

    def _get(self, url: str):
        return self._session.get(url, headers={'api_key': self._api_token})

    def _post(self, url:str, data: str):
        return self._session.post(url, data=data, headers={'api_key': self._api_token, 'Content-Type': 'application/json'})

    def _put(self, url:str, data: str):
        return self._session.put(url, data=data, headers={'api_key': self._api_token, 'Content-Type': 'application/json'})

    def _convert_to_body_markdown(self, article: Dict[str, str]) -> str:
        # TODO: This is duplicated in hugo_to_dev_to
        stream = StringIO()
        yaml = YAML()
        yaml.dump(article['preamble'], stream)
        preamble = stream.getvalue()
        return f"---\n{preamble}---\n{article['content']}\n"

    def get_articles(self):
        data = self._get("https://dev.to/api/articles/me/all")
        data = data.json()
        articles = parse_obj_as(List[Article], data)
        return articles

    def publish_article(self, article: Dict[str,str]):
        request_data = {
            "article": {
                "body_markdown": self._convert_to_body_markdown(article)
            }
        }
        self._post(f"https://dev.to/api/articles/", json.dumps(request_data))
    

    def update_article(self, id: int, article: Dict[str,str]):
        request_data = {
            "article": {
                "body_markdown": self._convert_to_body_markdown(article)
            }
        }
        self._put(f"https://dev.to/api/articles/{id}", json.dumps(request_data))
