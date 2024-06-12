import requests
from league import update_player_rating
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


update_player_ratings(domain=domain, table_name='Players', headers=headers)

# Note: json_data will not be serialized by requests
# exactly as it was in the original request.
#data = '{"email":"john.smith@foo.bar", "name":"John", "password":"123456seven"}'
#response = requests.post('https://api.backendless.com/<app-id>/<rest-api-key>/users/register', headers=headers, data=data)



