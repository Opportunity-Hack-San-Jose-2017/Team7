from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

if __name__ == '__main__':
    URL = 'https://plato1.api.ushahidi.io/oauth/token'
    CLIENT_ID = 'ushahidiui'
    CLIENT_SECRET = '35e7f0bca957836d05ca0492211b0ac707671261'
    USERNAME = 'nishgarg14@gmail.com'
    PASSWORD = 'plato12345'

    client = LegacyApplicationClient(client_id=CLIENT_ID)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=URL, client_id=CLIENT_ID,
                              client_secret=CLIENT_SECRET, username=USERNAME, password=PASSWORD,
                              scope="posts media forms api tags savedsearches sets users stats layers config messages notifications webhooks contacts roles permissions csv tos dataproviders")
    print(token)
    """
    Sample response
        {'access_token': 'P4xy3qcHal8hrRehxao4PgXsCvQCyNN8z71DKRZs', 'token_type': 'Bearer', 'expires_in': 1509582493,
     'refresh_token': 'WCcVfdyEgyCSpgWwvSbjMnZ9fOwaaKsqcy8S78Hl', 'refresh_token_expires_in': 604800,
     'expires_at': 3019161706.537249}
    """
