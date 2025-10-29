from .get_file_info import get_file_info
import requests
from pathlib import Path
import platform
import os
from typing import Optional





def download_file(token: str, path: str = "/data", save_dir: Optional[str] = None) -> str:
	# 获取文件信息
	response = get_file_info(token, path)
	
	# 打印完整的响应数据以便调试
	# print(f"\n完整响应数据: {response}")
	# print(f"响应数据的键: {response.keys()}")
	
	def _default_download_dir() -> Path:
		"""根据操作系统返回默认的下载目录。
		- macOS: ~/Downloads
		- Windows: %USERPROFILE%/Downloads (回退到 Path.home()/Downloads)
		"""
		system = platform.system()
		home = Path.home()

		if system == "Darwin":
			return home / "Downloads"
		elif system == "Windows":
			userprofile = os.environ.get("USERPROFILE")
			base = Path(userprofile) if userprofile else home
			return base / "Downloads"
		else:
			return ('暂不支持macOS、Windows以外的系统')

	# 尝试从响应的 data 字段中获取信息
	data = response.get("data", {})
	
	file_name = data.get("name") 
	raw_url = data.get("raw_url")
	

	print(f"\n开始下载文件: {file_name}")
	print(f"下载链接: {raw_url}")
	
	"""
	下面的代码测试使用，暂时不需要开启
	"""
	# if not raw_url:
	# 	raise RuntimeError("响应中未找到 raw_url")
	# if not file_name:
	# 	raise RuntimeError("响应中未找到文件名")

	# 解析保存目录（默认使用系统下载目录）
	if save_dir is None or str(save_dir).strip() == "":
		save_path = _default_download_dir()
	else:
		save_path = Path(save_dir)
	
	# 创建保存目录（如果不存在）
	save_path.mkdir(parents=True, exist_ok=True)
	
	# 完整的文件保存路径
	file_path = save_path / file_name
	# 创建保存目录
	print(f"正在下载到: {file_path}")
	
	with requests.get(raw_url, stream=True) as r:
		r.raise_for_status()
		
		# 获取文件大小
		total_size = int(r.headers.get('content-length', 0))
		
		# 写入文件
		downloaded = 0
		chunk_size = 8192
		
		with open(file_path, 'wb') as f:
			for chunk in r.iter_content(chunk_size=chunk_size):
				if chunk:
					f.write(chunk)
					downloaded += len(chunk)
					
					# 显示下载进度
					if total_size > 0:
						progress = (downloaded / total_size) * 100
						print(f"\r下载进度: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')
	
	print(f"\n\n文件下载完成: {file_path}")
	return str(file_path)


