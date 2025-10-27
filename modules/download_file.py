from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import os
import platform

import requests  # type: ignore

from .read_env import BASE_URL
from .get_list import get_list


def download_file(token: str, file_path: str, dest_dir: str | Path | None = None) -> Path:

	# OpenList raw download path uses "/d/" prefix
	url = BASE_URL.rstrip("/") + "/d/" + file_path.lstrip("/")
	
	headers = {"Authorization": token.strip()}

	if dest_dir is None:
		# 按操作系统选择默认下载目录
		if platform.system() == "Windows":
			# Windows: 通常位于 %USERPROFILE%\Downloads
			user_home = Path(os.environ.get("USERPROFILE", str(Path.home())))
			dest_root = user_home / "Downloads"
		else:
			# macOS/Linux: ~/Downloads
			dest_root = Path.home() / "Downloads"
	else:
		dest_root = Path(dest_dir)
	dest_root.mkdir(parents=True, exist_ok=True)

	filename = Path(file_path).name
	dest_path = dest_root / filename

	with requests.get(url, headers=headers, stream=True) as r:
		r.raise_for_status()
		with open(dest_path, "wb") as f:
			for chunk in r.iter_content(chunk_size=1024 * 256):  # 256KB chunks
				if not chunk:
					continue
				f.write(chunk)

	return dest_path


def _parse_version(name: str) -> Optional[Tuple[int, int, int]]:
	"""Parse 'vMAJOR.MINOR.PATCH' from beginning of name.

	Examples: 'v1.2.3-20250101.zip' -> (1,2,3)
	"""
	if not name or not name.startswith("v"):
		return None
	try:
		ver_part = name[1:].split("-", 1)[0]
		major_s, minor_s, patch_s = ver_part.split(".")
		return int(major_s), int(minor_s), int(patch_s)
	except Exception:
		return None


def download_latest(token: str, path: str = "/data", dest_dir: str | Path | None = None) -> tuple[Path, dict]:

	content = get_list(token, path=path)
	best_item: Optional[dict] = None
	best_ver: Optional[Tuple[int, int, int]] = None
	for item in content:
		name = (item.get("name") or "").strip()
		ver = _parse_version(name)
		if ver is None:
			continue
		if best_ver is None or ver > best_ver:
			best_ver = ver
			best_item = item

	if not best_item:
		raise RuntimeError("列表中未找到符合 vMAJOR.MINOR.PATCH 的文件，无法选择最新版本。")

	file_path = best_item.get("path")
	if not isinstance(file_path, str) or not file_path:
		raise RuntimeError("选中的条目缺少有效的路径字段 'path'")

	saved = download_file(token, file_path, dest_dir=dest_dir)
	return saved, best_item

