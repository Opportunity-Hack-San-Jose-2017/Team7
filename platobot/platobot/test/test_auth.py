import os

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

os.environ['DEBUG'] = '1'

if __name__ == '__main__':
    CLIENT_ID = 'ushahidiui'
    CLIENT_SECRET = '35e7f0bca957836d05ca0492211b0ac707671261'

    client = BackendApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url='https://35.203.151.94/platform/api/v3/oauth/token', client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET)
