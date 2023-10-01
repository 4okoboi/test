import requests
import json

url = "http://127.0.0.1:5000/api/user/register"

payload = json.dumps({
  "username": "Hero",
  "email": "email@email.email",
  "password": "Password1@"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
