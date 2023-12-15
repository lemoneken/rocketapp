import requests
import sys
import webbrowser
import random
import keyring

from urllib import parse

base_pocket_url = 'https://getpocket.com'
consumer_key = '##YOUR_CONSUMER_KEY##'

# Functions
def get_token():
    access_token = keyring.get_password("RocketApp", "PocketAccessToken")
    return access_token

def save_token(access_token):
    keyring.set_password("RocketApp", "PocketAccessToken", access_token)
    print('Token saved to keyring')

def request_token_from_pocket():
    # Authorize urls
    request_token_url = base_pocket_url + '/v3/oauth/request'
    authorize_url = base_pocket_url + '/auth/authorize'
    access_token_url = base_pocket_url + '/v3/oauth/authorize'

    # 1. Get Request token
    request_token_params = {
    'consumer_key': consumer_key,
    'redirect_uri': redirect_url
    }

    request_token_response = requests.get(request_token_url, request_token_params, verify=False)
    if request_token_response.status_code != 200:
        print('Error while getting request token from Pocket!')
        sys.exit()

    request_token = parse.parse_qs(request_token_response.text)['code'][0]

    # 2. Authorize request token
    authorize_token_params = {
    'request_token': request_token,
    'redirect_uri': redirect_url
    }

    full_authorize_url = authorize_url + '?' + parse.urlencode(authorize_token_params)

    print('Connecting to Pocket to authorize url.. Press any button once you connect the account')
    webbrowser.open(full_authorize_url)
    input()

    # 3. Get Pocket Access token
    access_token_params = {
    'consumer_key': consumer_key,
    'code': request_token
    }

    access_token_response = requests.get(access_token_url, access_token_params, verify=False)
    if access_token_response.status_code != 200:
        print('Error while getting access token from Pocket!')
        sys.exit()

    access_response_params = parse.parse_qs(access_token_response.text)
    access_token = access_response_params['access_token'][0]
    return access_token

def get_pocket_materials_and_output_random(access_token):
    get_materials_params = {
    'consumer_key': consumer_key,
    'access_token': access_token
    }

    materials_response = requests.get(get_materials_url, get_materials_params, verify=False)
    if materials_response.status_code != 200:
        print('Error while getting materials from Pocket!')
        return False
    
    materials_json = materials_response.json()

    # 5. Get and output random article
    articles = materials_json['list']
    articles_keys = list(articles)
    articles_count = len(articles_keys)

    random.seed()
    random_article_index = random.randrange(0, articles_count)
    random_article_key = articles_keys[random_article_index]

    article_url = read_url + '/' + random_article_key

    print('Your random article for today: ' + article_url)
    print('Opening an article..')

    webbrowser.open(article_url)
    return True

# API Urls
get_materials_url = base_pocket_url + '/v3/get'

# Other Urls
read_url = base_pocket_url + '/read'
redirect_url = 'https://example.com'

# 1. Get pre-saved access token from keychain
access_token = get_token()

# 2. Request new token if not present in keychain
if access_token is None:
    access_token = request_token_from_pocket()
    save_token(access_token)

# 3. Get Pocket materials
result = get_pocket_materials_and_output_random(access_token)

# 4. Retrieve new access token if request failed and retry
if result == False:
    # Refresh token and retry
    access_token = request_token_from_pocket()
    save_token(access_token)

    get_pocket_materials_and_output_random(access_token)
