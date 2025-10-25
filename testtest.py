import json
import os
from pathlib import Path

import requests  # type: ignore

BASE_URL = "https://list.beginner.center/"


def _load_env_values() -> dict[str, str]:
    env_path = Path(__file__).resolve().parent / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        value = raw_value.strip().strip('"').strip("'")
        values[key.strip()] = value
    return values


env_values = _load_env_values()

USERNAME = os.environ.get("USERNAME") or env_values.get("USERNAME") or env_values.get("username")
PASSWORD = os.environ.get("PASSWORD") or env_values.get("PASSWORD") or env_values.get("password")

if not USERNAME or not PASSWORD:
    raise RuntimeError("用户名或密码未在环境变量或 .env 文件中找到")


login_payload = json.dumps({
    "username": USERNAME,
    "password": PASSWORD,
    # "otp_code": "123456",
})
login_headers = {
    "Content-Type": "application/json",
}

login_response = requests.post(BASE_URL + "api/auth/login", headers=login_headers, data=login_payload)
print(login_response.text + "\n")

login_body = login_response.json()
token = login_body.get("data", {}).get("token")
print(f"{token}\n")

list_payload = json.dumps({
    "path": "/data",
    "password": PASSWORD,
})
list_headers = {
    "Authorization": f"{token}",
    "Content-Type": "application/json",
}

list_response = requests.post(BASE_URL + "api/fs/list", headers=list_headers, data=list_payload)
print(list_response.text + "\n")

listing = list_response.json()
content = listing.get("data", {}).get("content", [])

for item in content:
    print(f"{item.get('name')}\t{item.get('path')}\t{item.get('modified')}")