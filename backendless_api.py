import requests
from league import update_player_rating, event_parser
from api_updates import add_or_update_event
from creds import backendless_creds
import urllib.parse as ulp

api_creds = backendless_creds()
domain = api_creds['domain']
app_id = api_creds['app_id']
api_key = api_creds['api_key']
email = api_creds['email']
name = api_creds['user_name']
password = api_creds['password']
user_token = api_creds['user_token']

headers = {
    'content-type': 'application/json',
    'user-token': user_token,
}

# REGISTER
# url = f'https://api.backendless.com/{app_id}/{api_key}/users/register'
# data = '{"email":"'+email+'","name":"'+name+'","password":"'+password+'"}'

# LOGIN
# url = f'https://api.backendless.com/{app_id}/{api_key}/users/login'
# data = '{"login":"'+email+'","password":"'+password+'"}'

# r = requests.post(url=url, data=data, headers=headers)

# UPDATE PLAYER RATINGS
# update_player_ratings(domain=domain, table_name='Players', headers=headers)

events_to_add = [77764, 77765, 77766]
response = add_or_update_event(domain, headers, events_to_add[0], table_name='EventResults')
print(response)
