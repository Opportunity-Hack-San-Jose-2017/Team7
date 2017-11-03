"""
* UshahidiClient: Subclass of HTTPClient with Ushahidi Auth stuff built in

"""
import os

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

from platobot.ushahidi.ds import Form, FormAttribute, Post
from platobot.ushahidi.http_base import HttpClient, RequestBuilder, Request


class UshahidiClient(HttpClient):
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

    def get_forms(self) -> [Form]:
        """
        Get list of forms
        """
        request = (self.get_request_builder()
                   .suburl('forms')
                   ).build()
        response = self.get(request=request)
        if response.status_code != 200:
            raise IOError('Failed request: {}'.format(request.__dict__))
        return [Form.deserialize(json_blob) for json_blob in response.json().get('results')]

    def get_attributes(self, form_id: any) -> [FormAttribute]:
        """
        :return:
        """
        request = (self.get_request_builder()
                   .suburl('forms')
                   .key(form_id)
                   .suburl('attributes')
                   ).build()
        response = self.get(request=request)
        if response.status_code != 200:
            raise IOError('Failed request: {}'.format(request.__dict__))
        return [FormAttribute.deserialize(json_blob) for json_blob in response.json().get('results')]

    def get_posts(self):
        """
        :param post:
        :return:
        """
        request = (self.get_request_builder()
                   .suburl('posts')
                   ).build()
        response = self.get(request=request)
        if response.status_code != 200:
            raise IOError('Failed request: {}'.format(request.__dict__))
        return [Post.deserialize(json_blob) for json_blob in response.json().get('results')]

    def get_post(self, key: int) -> Post:
        """
        :param post:
        :return:
        """
        request = (self.get_request_builder()
                   .suburl('posts')
                   .key(key=key)
                   ).build()
        response = self.get(request=request)
        if response.status_code != 200:
            raise IOError('Failed request: {}'.format(request.__dict__))
        return Post.deserialize(response.json())

    def save_post(self, post: Post):
        """
        :param post:
        :return:
        """
        request = (self.get_request_builder()
                   .suburl('posts')
                   .request_body(post.get_json())
                   ).build()
        response = self.post(request=request)
        if response.status_code != 200:
            raise IOError('Failed request: {}'.format(request.__dict__))
        return Post(**response.json())

    def update_post(self, post: Post):
        """
        :param post:
        :return:
        """
        if not post.id:
            raise ValueError('Post object should have an id since this is an update operation')
        request = (self.get_request_builder()
                   .suburl('posts')
                   .key(post.id)
                   .request_body(post.get_json())
                   ).build()
        response = self.put(request=request)
        if response.status_code != 200:
            raise IOError('Failed request: {}'.format(request.__dict__))
        return Post(**response.json())


if __name__ == '__main__':
    # Get Client
    client = UshahidiClient()
    # Get forms
    forms = client.get_forms()
    main_form = forms[0]
    # Get attributes (not being used, we will use it later)
    attributes = client.get_attributes(1)
    # Get posts
    post = client.get_post(15)
    post.title = 'Volience - Cats'
    post.content = 'Cats are being fed milk instead of fish'
    post.source = 'SMS'
    updated_post = client.update_post(post)
    # Create a new post and save it via API
    # post = Post(title='Violence incident', content="Halp me", source='SMS', status='published')
    # post.set_form(form=main_form)
    # saved_post = client.save_post(post)
    # # Update title of saved_post
    # updated_post = client.update_post(saved_post)
    # print(updated_post)
