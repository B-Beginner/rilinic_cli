import json
import requests  # type: ignore

url = "https://list.beginner.center/"

payload = json.dumps({
   "username": "test",
   "password": "7h98NhZzuZ",
   # "otp_code": "123456",
})
headers = {
   "Content-Type": "application/json",
}

response = requests.post( url+"api/auth/login", headers=headers, data=payload)
print(response.text + '\n')


body = response.json()
token = body.get("data", {}).get("token")
print(token + '\n')



list_payload = json.dumps({
   "path": "/data",
   "password": "7h98NhZzuZ",
   # "force_root": False,
})
list_headers = {
   "Authorization": f"{token}",
   "Content-Type": "application/json",
}

list_response = requests.post(url + "api/fs/list", headers=list_headers, data=list_payload)
print(list_response.text + '\n')


listing = list_response.json()
content = listing.get("data", {}).get("content", [])

for item in content:
   print(f"{item.get('name')}	{item.get('path')}")