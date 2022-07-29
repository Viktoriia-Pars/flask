import requests

HOST = 'http://127.0.0.1:5000'

# response = requests.post(f'{HOST}/test/',
#                         json={'key': 'value'},
#                         params={'q1': 'v1'},
#                         headers={'custom_header_1': 'some_value'})

# response = requests.post(f'{HOST}/users/',
#                         json={'name': 'user_3', 'password': '12345678'},
#                          )
# response = requests.put(f'{HOST}/articles/update/24',
#                         json={'header': 'The forth post', 'description': 'The second post text', 'author': 1},
#                          )
# response = requests.post(f'{HOST}/articles/',
#                         json={'header': 'The third post', 'description': 'The third post text', 'author': 1},
#                         )
# response = requests.get(f'{HOST}/users/12')
response = requests.get(f'{HOST}/articles/24')
# response = requests.delete(f'{HOST}/articles/delete/23')
print(response.text)