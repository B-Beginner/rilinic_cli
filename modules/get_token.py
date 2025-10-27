import requests  # type: ignore

from .read_env import BASE_URL, load_credentials


def get_token() -> str:
    """
    based on https://fox.oplist.org.cn/364155678e0
    """
    username, password = load_credentials()

    # Using json= so requests sets appropriate header
    resp = requests.post(
        BASE_URL + "api/auth/login",
        json={
            "username": username,
            "password": password,
            # "otp_code": "123456",
        },
    )
    resp.raise_for_status()

    body = resp.json()
    token = (body.get("data", {}).get("token") or "").strip()
    if not token:
        raise RuntimeError("登录失败，未获取到 token")
    return token
