import requests  # type: ignore

from .read_env import BASE_URL, load_credentials


def get_list(token: str, path: str = "/data") -> list[dict]:
    """
    based on https://fox.oplist.org.cn/364155732e0
    """
    headers = {"Authorization": token.strip()}

    _, password = load_credentials()

    response = requests.post(
        BASE_URL + "api/fs/list",
        headers=headers,
        json={
            "path": path,
            "password": password,
        },
    )
    response.raise_for_status()

    return response.json().get("data", {}).get("content", []) or []
