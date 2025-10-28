from pathlib import Path

# 读取 .env 文件
env_path = Path(__file__).resolve().parent.parent / ".env"
if not env_path.exists():
    raise RuntimeError("未找到 .env 文件: " + str(env_path))

env_vars: dict[str, str] = {}

for raw_line in env_path.read_text().splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, raw_value = line.split("=", 1)
    value = raw_value.strip().strip('"').strip("'")
    env_vars[key.strip()] = value

# 导出变量
BASE_URL = env_vars.get("BASE_URL")
USERNAME = env_vars.get("USERNAME")
PASSWORD = env_vars.get("PASSWORD")

# 验证必需的变量
if not BASE_URL:
    raise RuntimeError(".env 文件中缺少 BASE_URL")
if not USERNAME:
    raise RuntimeError(".env 文件中缺少 USERNAME")
if not PASSWORD:
    raise RuntimeError(".env 文件中缺少 PASSWORD")
