"""HTTP client and API integration tools."""

import json
from typing import Optional

import requests
from rich.console import Console

console = Console()


def http_request(
    url: str,
    method: str = "GET",
    headers: Optional[str] = None,
    body: Optional[str] = None,
    params: Optional[str] = None,
) -> str:
    """Make an HTTP request to any URL."""
    try:
        # Parse headers
        h = {"User-Agent": "AQUA/1.0"}
        if headers:
            h.update(json.loads(headers))

        # Parse params
        p = {}
        if params:
            p = json.loads(params)

        # Parse body
        data = None
        json_body = None
        if body:
            try:
                json_body = json.loads(body)
            except json.JSONDecodeError:
                data = body

        response = requests.request(
            method=method.upper(),
            url=url,
            headers=h,
            params=p,
            data=data,
            json=json_body,
            timeout=30,
        )

        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text[:5000],
        }

        # Try to parse as JSON
        try:
            result["json"] = response.json()
        except:
            pass

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"HTTP error: {e}"


def api_get(url: str, headers: Optional[str] = None) -> str:
    """Simple GET request to an API endpoint."""
    return http_request(url, method="GET", headers=headers)


def api_post(url: str, body: str, headers: Optional[str] = None) -> str:
    """Simple POST request with JSON body."""
    h = headers or '{"Content-Type": "application/json"}'
    return http_request(url, method="POST", headers=h, body=body)


def api_put(url: str, body: str, headers: Optional[str] = None) -> str:
    """Simple PUT request with JSON body."""
    h = headers or '{"Content-Type": "application/json"}'
    return http_request(url, method="PUT", headers=h, body=body)


def api_delete(url: str, headers: Optional[str] = None) -> str:
    """Simple DELETE request."""
    return http_request(url, method="DELETE", headers=headers)


def download_file(url: str, save_path: str) -> str:
    """Download a file from URL to local path."""
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        import os
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        size = os.path.getsize(save_path)
        return f"Downloaded {size} bytes to {save_path}"

    except Exception as e:
        return f"Download error: {e}"


HTTP_TOOLS = {
    "http_request": {
        "func": http_request,
        "schema": {
            "type": "function",
            "function": {
                "name": "http_request",
                "description": "Make an HTTP request (GET, POST, PUT, DELETE, etc.) to any URL with custom headers, params, and body.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Request URL"},
                        "method": {"type": "string", "description": "HTTP method (GET, POST, PUT, DELETE, PATCH)", "default": "GET"},
                        "headers": {"type": "string", "description": "JSON string of headers"},
                        "body": {"type": "string", "description": "Request body (JSON string or raw)"},
                        "params": {"type": "string", "description": "JSON string of query parameters"},
                    },
                    "required": ["url"],
                },
            },
        },
    },
    "api_get": {
        "func": api_get,
        "schema": {
            "type": "function",
            "function": {
                "name": "api_get",
                "description": "Make a GET request to an API endpoint.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "API endpoint URL"},
                        "headers": {"type": "string", "description": "JSON string of headers"},
                    },
                    "required": ["url"],
                },
            },
        },
    },
    "api_post": {
        "func": api_post,
        "schema": {
            "type": "function",
            "function": {
                "name": "api_post",
                "description": "Make a POST request with JSON body.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "API endpoint URL"},
                        "body": {"type": "string", "description": "JSON body string"},
                        "headers": {"type": "string", "description": "JSON string of headers"},
                    },
                    "required": ["url", "body"],
                },
            },
        },
    },
    "download_file": {
        "func": download_file,
        "schema": {
            "type": "function",
            "function": {
                "name": "download_file",
                "description": "Download a file from a URL to local path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "File URL"},
                        "save_path": {"type": "string", "description": "Local path to save file"},
                    },
                    "required": ["url", "save_path"],
                },
            },
        },
    },
}
