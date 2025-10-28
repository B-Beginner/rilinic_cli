import requests  # type: ignore

from .read_env import BASE_URL, USERNAME, PASSWORD


def get_list(token: str, path: str = "/data") -> list[dict]:
    """
    based on https://fox.oplist.org.cn/364155732e0
    """
    headers = {"Authorization": token.strip()}


    response = requests.post(
        BASE_URL.rstrip("/") + "/api/fs/list",
        headers=headers,
        json={
            "path": path,
        },
    )
    response.raise_for_status()

    return response.json().get("data", {}).get("content", []) or []
