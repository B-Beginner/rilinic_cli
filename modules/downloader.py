import os
import requests
from urllib.parse import urlparse


def download_file(url, save_path, headers=None, referer=None, timeout=30):
    """
    下载文件并保存到指定路径。默认会使用常见浏览器的 User-Agent，并允许传入自定义 headers 或 referer。

    :param url: 文件 URL
    :param save_path: 保存目录
    :param headers: 可选的额外请求头（dict），会覆盖默认头
    :param referer: 可选 Referer 字段，会加入请求头
    :param timeout: 请求超时（秒）
    :return: 文件保存路径
    :raises: Exception 如果下载失败
    """
    try:
        # 获取文件名
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = "downloaded_file"

        # 默认 headers，很多 CDN/站点会根据 User-Agent/Referer 限制访问
        default_headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
            )
        }
        if referer:
            default_headers["Referer"] = referer
        if headers:
            default_headers.update(headers)

        # 使用 Session 以便未来可扩展（cookie、重试等）
        session = requests.Session()
        response = session.get(url, stream=True, headers=default_headers, timeout=timeout)

        # 特殊处理 403，给出更明确的提示
        if response.status_code == 403:
            raise Exception(
                "下载失败: 403 Forbidden。服务器拒绝访问。尝试使用浏览器头(User-Agent)、设置 Referer 或检查该 URL 是否需要认证/签名。"
            )

        response.raise_for_status()

        # 保存文件
        file_path = os.path.join(save_path, filename)
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive chunks
                    file.write(chunk)

        return file_path
    except requests.exceptions.RequestException as e:
        raise Exception(f"下载失败: {e}")