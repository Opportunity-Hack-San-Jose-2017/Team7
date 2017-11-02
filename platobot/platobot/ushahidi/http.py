"""
Provides abstractions for making calls to Ushahidi instances

* Request: Instance of this type encapsulates all the data required for a http request
* RequestBuilder: Builder pattern based abstraction which returns an instance of Request type
* HttpClient: Encapsulates Base url for all requests, authorization headers
* UshahidiClient: Subclass of HTTPClient with Ushahidi Auth stuff built in

"""
import os

import requests
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session


class ImmutableRequest(Exception):
    pass


class Request:
    """
    Encapsulates suburl, query_params (url params), request-body, headers

    """

    def __init__(self, suburl: str, query_params: dict, headers: dict, request_body: dict):
        self.suburl = suburl
        self.query_params = query_params
        self.headers = headers
        self.request_body: dict = request_body


class RequestBuilder:
    """
    Provides a readable api for creating Request objects using builder pattern
    request = (RequestBuilder()
                .suburl('api/v3')
                .suburl('forms')
                .query_param('limit', 4)
                .build()
               )
    """

    def __init__(self):
        self._sub_urls = []
        self._query_params = dict()
        self._headers = dict()
        self._request_body = None
        self.__built = False

    def query_param(self, key: str, value: str):
        """
        :param key:
        :param value:
        :return:
        """
        if self.__built:
            raise ImmutableRequest
        self._query_params[key] = value
        return self

    def header(self, key: str, value: str):
        """
        :param key:
        :param value:
        :return:
        """
        if self.__built:
            raise ImmutableRequest
        self._headers[key] = value
        return self

    def suburl(self, url: str):
        """
        :param url:
        :return:
        """
        if self.__built:
            raise ImmutableRequest
        self._sub_urls.append(url.strip('/'))
        return self

    def key(self, key: any):
        """
        Alias for suburl, provide more readable api for specifying keys for http resources
        :param key:
        :return:
        """
        self.suburl(str(key))
        return self

    def set_content_type_as_json(self):
        self.header('Content-Type', 'application/json')
        return self

    def request_body(self, content: any):
        self._request_body = content
        return self

    def build(self) -> Request:
        """
        :return:
        """
        if self.__built:
            raise ImmutableRequest
        self.__built = True
        return Request(suburl=os.path.join(*self._sub_urls),
                       query_params=self._query_params,
                       headers=self._headers,
                       request_body=self._request_body)


class HttpClient:
    """
    Make http calls using Request objects
    """

    def __init__(self, base_url: str):
        self._base_url = base_url

    def get(self, request: Request) -> requests.Response:
        """
        :return:
        """
        return self._request(method='get', request=request)

    def post(self, request: Request) -> requests.Response:
        """
        :return:
        """
        return self._request(method='post', request=request)

    def put(self, request: Request) -> requests.Response:
        """
        :return:
        """
        return self._request(method='put', request=request)

    def _request(self, method: str, request: Request):
        """
        :param method:
        :param request:
        :return:
        """
        request_params = {
            'url': os.path.join(self._base_url, request.suburl),
            'params': request.query_params,
            'headers': request.headers,
            'data': str(request.request_body)
        }
        if method == 'get':
            return requests.get(**request_params)
        elif method == 'post':
            return requests.post(**request_params)
        else:
            raise NotImplementedError('Method: {} is not implemented yet')


class UdahishiClient(HttpClient):
    """
    Make requests to Ushahidi instance with authorization built in
    """

    INSTANCE = 'https://plato1.api.ushahidi.io'
    CLIENT_ID = 'ushahidiui'
    CLIENT_SECRET = '35e7f0bca957836d05ca0492211b0ac707671261'
    USERNAME = 'nishgarg14@gmail.com'
    PASSWORD = 'plato12345'
    SCOPE = ['posts', 'media', 'forms', 'api', 'tags', 'savedsearches', 'sets', 'users', 'stats', 'layers', 'config',
             'messages', 'notifications', 'webhooks', 'contacts', 'roles', 'permissions', 'csv', 'tos', 'dataproviders']

    def __init__(self):
        super().__init__(base_url=self.INSTANCE)

        self._client = LegacyApplicationClient(client_id=self.CLIENT_ID)
        self.oauth_session = OAuth2Session(client=self._client)
        self._token = self.oauth_session.fetch_token(token_url=self.token_url,
                                                     client_id=self.CLIENT_ID,
                                                     client_secret=self.CLIENT_SECRET,
                                                     username=self.USERNAME,
                                                     password=self.PASSWORD,
                                                     scope=' '.join(self.SCOPE))

    @property
    def token_url(self):
        return os.path.join(self.INSTANCE, 'oauth/token')

    def _request(self, method: str, request: Request):
        """
        :param method:
        :param request:
        :return:
        """
        request_params = {
            'url': os.path.join(self._base_url, request.suburl),
            'params': request.query_params,
            'headers': request.headers,
            'data': str(request.request_body)
        }
        if method in ('get', 'post', 'put'):
            return self.oauth_session.request(method=method, **request_params)
        raise NotImplementedError('Method: {} is not implemented yet')

    def get_request_builder(self) -> RequestBuilder:
        """
        returns Request builder instance with api version suburl
        """
        return RequestBuilder().suburl('api/v3')


if __name__ == '__main__':
    """
    Get list of surveys
    """
    client = UdahishiClient()
    request = (client
               .get_request_builder()
               .suburl('forms')
               ).build()
    response = client.get(request=request)
    surveys = response.json()
    # Get specific survey
    request = (client
               .get_request_builder()
               .suburl('forms')
               .key(1)
               ).build()
    response = client.get(request=request)
    survey = response.json()
    print(response)
