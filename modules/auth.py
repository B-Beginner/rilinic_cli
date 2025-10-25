"""Authentication utilities for retrieving JWT tokens."""

from __future__ import annotations

import json
import logging
from typing import Optional, Tuple

import requests

LOGIN_URL = "https://list.beginner.center/api/auth/login"
logger = logging.getLogger(__name__)


def authenticate(username: str, password: str, timeout: int = 15) -> Tuple[Optional[str], Optional[str]]:
    """Attempt to log in and return a JWT token and optional error message."""
    payload_dict = {
        "username": username,
        "password": password,
        "otp_code": "",
    }
    payload = json.dumps(payload_dict, ensure_ascii=False)
    headers = {
        "Content-Type": "application/json",
    }

    try:
        logger.debug("Sending login request to %s", LOGIN_URL)
        response = requests.post(LOGIN_URL, headers=headers, data=payload, timeout=timeout)
        logger.debug("Login response status code: %s", response.status_code)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network path
        logger.error("Login request failed: %s", exc)
        return None, f"登录失败: {exc}"

    try:
        data = response.json()
    except ValueError:
        return None, "接口返回的不是有效的 JSON 数据"

    if isinstance(data, dict) and data.get("code") not in (None, 200):
        msg = data.get("message") or "登录接口返回错误"
        logger.warning("Login interface returned error code %s: %s", data.get("code"), msg)
        return None, f"登录失败: {msg}"

    token = _extract_token(data)
    if not token:
        logger.debug("Login response payload: %s", json.dumps(data, ensure_ascii=False))
        return None, "未在响应中找到 token 字段"

    if not isinstance(token, str):
        try:
            token = token.decode()  # type: ignore[call-arg]
        except AttributeError:
            token = str(token)

    logger.debug("Token retrieved successfully (length %s)", len(token))

    return token, None


def _extract_token(payload):
    """Extract token-like field from nested payload."""
    if isinstance(payload, str):
        return payload

    if isinstance(payload, dict):
        for key in ("token", "jwt", "access_token"):
            value = payload.get(key)
            if isinstance(value, (str, bytes)) and value:
                return value

        nested = payload.get("data") or payload.get("result")
        if nested is not None:
            return _extract_token(nested)

    if isinstance(payload, list):
        for item in payload:
            token = _extract_token(item)
            if token:
                return token

    return None
