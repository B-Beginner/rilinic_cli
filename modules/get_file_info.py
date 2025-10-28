import requests
from .read_env import BASE_URL, PASSWORD
from .get_list import get_list


def get_file_info(token: str, path: str = "/data") -> dict:
	"""
	获取文件列表中最后一个文件的详细信息
	"""
	# 获取文件列表
	file_list = get_list(token, path=path)
	
	if not file_list:
		raise RuntimeError("文件列表为空")
	
	# 获取最后一个文件
	last_item = file_list[-1]
	filename = last_item.get("name", "")
	file_path = last_item.get("path", "")
	modified = last_item.get("modified", "")
	
	print(f"选中的文件: {filename}")
	print(f"文件路径: {file_path}")
	print(f"修改时间: {modified}\n")
	
	# 调用 /api/fs/get API
	url = BASE_URL.rstrip("/") + "/api/fs/get"
	
	headers = {
		'Authorization': token.strip(),
		'Content-Type': 'application/json'
	}
	
	payload = {
		"path": file_path,
		"password": PASSWORD
	}
	
	response = requests.post(url, headers=headers, json=payload)
	response.raise_for_status()
	
	print("API 响应:")
	print(response.text)
	
	return response.json()


if __name__ == "__main__":
	# 用于测试
	from .get_token import get_token
	token = get_token()
	get_file_info(token)