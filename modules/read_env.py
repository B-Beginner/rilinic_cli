from pathlib import Path


BASE_URL = "https://list.beginner.center/"


def load_credentials() -> tuple[str, str]:

    # 固定相对路径：modules/../.env（项目根目录）
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        raise RuntimeError("未找到 .env 文件: " + str(env_path))

    username: str | None = None
    password: str | None = None

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        value = raw_value.strip().strip('"').strip("'")
        if key.strip() == "USERNAME":
            username = value
        elif key.strip() == "PASSWORD":
            password = value

    if not username or not password:
        raise RuntimeError(".env 文件中缺少 USERNAME 或 PASSWORD")

    return username, password
