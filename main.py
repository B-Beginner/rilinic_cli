from modules.get_token import get_token

from modules.get_list import get_list
from modules.get_file_info import get_file_info
from modules.download_file import download_file

def main() -> None:
    token = get_token()
    print(f"token: {token}\n")

    content = get_list(token, path="/data")
    print(f"full_info: {content}\n")
    # 输出文件名、路径、修改时间
    for item in content:
        print(f"{item.get('name')}\t{item.get('path')}\t{item.get('modified')}")
    get_file_info(token, path="/data")
    download_file(token, path="/data")

if __name__ == "__main__":
    main()