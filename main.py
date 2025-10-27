from modules.get_token import get_token
from modules.download_file import download_latest
from modules.get_list import get_list


def main() -> None:
    token = get_token()
    print(f"token: {token}\n")

    content = get_list(token, path="/data")
    print(f"full_info: {content}\n")
    # 输出文件名、路径、修改时间
    for item in content:
        print(f"{item.get('name')}\t{item.get('path')}\t{item.get('modified')}")
    download_latest(token)

if __name__ == "__main__":
    main()