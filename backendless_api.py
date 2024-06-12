import requests
from league import update_player_rating, event_parser
from creds import backendless_creds

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

event_url = 'https://www.pdga.com/tour/event/'
events_to_add = [77764, 77765, 77766]

events = [event_parser(event_url+str(e)) for e in events_to_add]

print(events[0].head())
print(events[1].head())
print(events[2].head())