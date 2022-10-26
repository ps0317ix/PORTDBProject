import requests


def get_zendesk_ticket(email, subdomain, api_key):

    url = f'https://{subdomain}/api/v2/users.json'
    user = email + '/token'

    session = requests.Session()
    session.auth = (user, api_key)

    response = session.get(url)
    data = response.json()

    return data['users']
