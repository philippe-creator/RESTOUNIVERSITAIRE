import urllib.request
import urllib.error
import json

try:
    req = urllib.request.Request(
        'http://localhost:5000/api/auth/connexion',
        data=json.dumps({'email': 'youssef@univ.ma', 'password': '1234'}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    print(urllib.request.urlopen(req).read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(e.read().decode('utf-8'))
