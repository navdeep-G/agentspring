"""
Web & Search Tools for AgentSpring
Includes HTTP requests, web search, and scraping tools
"""
import requests
import os
import urllib.parse
from . import tool

@tool("http_get", "Make an HTTP GET request to a URL with enhanced features", permissions=[])
def http_get(url: str, headers: dict = {}, timeout: int = 30, verify_ssl: bool = True):
    try:
        response = requests.get(url, headers=headers, timeout=timeout, verify=verify_ssl)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text,
            "url": url,
            "encoding": response.encoding,
            "elapsed_time": response.elapsed.total_seconds()
        }
    except requests.RequestException as e:
        raise Exception(f"HTTP GET request failed: {e}")

@tool("http_post", "Make an HTTP POST request to a URL with enhanced features", permissions=[])
def http_post(url: str, data: dict = {}, headers: dict = {}, timeout: int = 30, verify_ssl: bool = True):
    try:
        response = requests.post(url, json=data, headers=headers, timeout=timeout, verify=verify_ssl)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text,
            "url": url,
            "encoding": response.encoding,
            "elapsed_time": response.elapsed.total_seconds()
        }
    except requests.RequestException as e:
        raise Exception(f"HTTP POST request failed: {e}")

@tool("http_put", "Make an HTTP PUT request to a URL with enhanced features", permissions=[])
def http_put(url: str, data: dict = {}, headers: dict = {}, timeout: int = 30, verify_ssl: bool = True):
    try:
        response = requests.put(url, json=data, headers=headers, timeout=timeout, verify=verify_ssl)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text,
            "url": url,
            "encoding": response.encoding,
            "elapsed_time": response.elapsed.total_seconds()
        }
    except requests.RequestException as e:
        raise Exception(f"HTTP PUT request failed: {e}")

@tool("http_delete", "Make an HTTP DELETE request to a URL with enhanced features", permissions=[])
def http_delete(url: str, headers: dict = {}, timeout: int = 30, verify_ssl: bool = True):
    try:
        response = requests.delete(url, headers=headers, timeout=timeout, verify=verify_ssl)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text,
            "url": url,
            "encoding": response.encoding,
            "elapsed_time": response.elapsed.total_seconds()
        }
    except requests.RequestException as e:
        raise Exception(f"HTTP DELETE request failed: {e}")

@tool("download_file", "Download a file from URL", permissions=[])
def download_file(url: str, local_path: str = "", headers: dict = {}):
    try:
        if not local_path:
            local_path = os.path.basename(urllib.parse.urlparse(url).path) or "downloaded_file"
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return {"success": True, "local_path": local_path}
    except Exception as e:
        raise Exception(f"Download failed: {e}") 