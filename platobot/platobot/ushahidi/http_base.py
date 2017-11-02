"""
Provides abstractions for making calls to Ushahidi instances

* Request: Instance of this type encapsulates all the data required for a http request
* RequestBuilder: Builder pattern based abstraction which returns an instance of Request type
* HttpClient: Encapsulates Base url for all requests, authorization headers

"""
import json
import os

import requests


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
        self._sub_urls.append(str(url).strip('/'))
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
        if type(content) == dict:
            self._request_body = json.dumps(content)
        else:
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
