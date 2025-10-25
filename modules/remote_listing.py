"""Utilities for retrieving and formatting remote directory listings."""

from __future__ import annotations

import json
import logging
from typing import Optional, Tuple

import requests

LIST_URL = "https://list.beginner.center/api/fs/dirs"
logger = logging.getLogger(__name__)


def fetch_remote_listing(
    *,
    token: str,
    path: str,
    password: str,
    force_root: bool,
    timeout: int = 15,
) -> Tuple[Optional[str], Optional[str], bool]:
    """Fetch remote listing and return (text, error, token_invalid)."""
    payload_dict = {
        "path": path,
        "password": password or "",
        "force_root": bool(force_root),
    }
    payload = json.dumps(payload_dict, ensure_ascii=False)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        logger.debug(
            "Posting directory request to %s with path=%s force_root=%s password_provided=%s",
            LIST_URL,
            path,
            bool(force_root),
            bool(password),
        )
        response = requests.post(LIST_URL, headers=headers, data=payload, timeout=timeout)
        logger.debug("Directory response status code: %s", response.status_code)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network path
        logger.error("Directory listing request failed: %s", exc)
        return None, f"获取目录失败: {exc}", False

    try:
        data = response.json()
    except ValueError:
        return None, "目录接口返回的不是有效的 JSON 数据", False

    if isinstance(data, dict) and data.get("code") not in (None, 200):
        err_msg = data.get("message") or "目录接口返回错误"
        body = json.dumps(data, ensure_ascii=False, indent=2)
        if data.get("code") == 401:
            logger.warning("目录接口返回 401，token 失效: %s", err_msg)
            return body, err_msg, True
        logger.warning("目录接口返回错误码 %s: %s", data.get("code"), err_msg)
        return body, err_msg, False

    listing_text = _format_listing(data)
    logger.debug("目录数据解析完成，输出字符长度 %s", len(listing_text) if listing_text else 0)
    return listing_text, None, False


def _format_listing(payload) -> str:
    """Convert API payload into a human-readable listing string."""
    target = payload
    if isinstance(payload, dict):
        for key in ("data", "result"):
            if key in payload:
                target = payload[key]
                break

    items = None
    extra_lines = []
    if isinstance(target, dict):
        for key in ("content", "items", "children"):
            value = target.get(key)
            if isinstance(value, list):
                items = value
                break
        else:
            return json.dumps(payload, ensure_ascii=False, indent=2)

        total = target.get("total")
        readme = target.get("readme")
        header = target.get("header")
        if total is not None:
            extra_lines.append(f"总计: {total}")
        if header:
            extra_lines.append(f"Header: {header}")
        if readme:
            extra_lines.append(f"Readme: {readme}")
    elif isinstance(target, list):
        items = target
    else:
        return json.dumps(payload, ensure_ascii=False, indent=2)

    lines = []
    if items is not None:
        for entry in items:
            if isinstance(entry, dict):
                name = (
                    entry.get("name")
                    or entry.get("filename")
                    or entry.get("path")
                    or "未命名"
                )
                is_dir = (
                    entry.get("is_dir")
                    or entry.get("dir")
                    or entry.get("type") in {"dir", "folder"}
                )
                suffix = "/" if is_dir else ""
                size = entry.get("size")
                if size is not None:
                    lines.append(f"{name}{suffix}\t{size}")
                else:
                    lines.append(f"{name}{suffix}")
            else:
                lines.append(str(entry))

    display_lines = extra_lines + (["---"] if extra_lines and lines else []) + lines
    return "\n".join(display_lines) if display_lines else "列表为空"
