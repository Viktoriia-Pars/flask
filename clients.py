import requests

HOST = 'http://127.0.0.1:5000'

# response = requests.post(f'{HOST}/test/',
#                         json={'key': 'value'},
#                         params={'q1': 'v1'},
#                         headers={'custom_header_1': 'some_value'})

# response = requests.post(f'{HOST}/users/',
#                         json={'name': 'user_5', 'password': '12345678'},
#                          )
# response = requests.post(f'{HOST}/articles/',
#                         json={'header': 'The second post', 'description': 'The second post text', 'author': 1},
#                          )
# response = requests.post(f'{HOST}/articles/',
#                         json={'header': 'The first post', 'description': 'The first post text', 'author': 12},
#                          )
# response = requests.get(f'{HOST}/users/12')
# response = requests.get(f'{HOST}/articles/1')
response = requests.delete(f'{HOST}/articles/delete/1')
print(response.text)