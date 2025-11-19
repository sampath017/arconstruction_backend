import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ---------- Config ----------
DEFAULT_COLLECTION_FILE = "ARConstruction-API.postman_collection.json"
# e.g. "http://localhost:8000" to override host/port
DEFAULT_BASE_URL = "http://localhost:8000"
TIMEOUT_SECONDS = 15
SAVE_RESPONSES = True
OUTPUT_DIR = Path("run_outputs")
VERIFY_SSL = True  # set False only for self-signed HTTPS in local dev


def make_session() -> requests.Session:
    """Create a session with retry strategy for transient network/server errors."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(
            ["HEAD", "GET", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"]),
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def override_base_url_if_provided(original_url: str, base_url: Optional[str]) -> str:
    """
    If base_url is provided, replace scheme+host+port in original_url with base_url,
    keeping the path and query string intact. Relative URLs get prefixed by base_url.
    """
    if not base_url:
        return original_url

    try:
        if original_url.startswith("http://") or original_url.startswith("https://"):
            # Find third slash after scheme://
            third_slash = original_url.find("/", original_url.find("//") + 2)
            if third_slash == -1:
                return base_url.rstrip("/")
            path = original_url[third_slash:]
            return base_url.rstrip("/") + path
        else:
            # Relative URL
            if not original_url.startswith("/"):
                return base_url.rstrip("/") + "/" + original_url
            return base_url.rstrip("/") + original_url
    except Exception:
        return original_url


def ensure_output_dir():
    if SAVE_RESPONSES:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_response(name: str, resp: requests.Response):
    if not SAVE_RESPONSES:
        return
    safe = (
        name.replace(" ", "_")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(":", "_")
    )
    meta_path = OUTPUT_DIR / f"{safe}.meta.txt"
    body_path = OUTPUT_DIR / f"{safe}.body"

    meta_lines = [
        f"URL: {resp.request.method} {resp.request.url}",
        f"Status: {resp.status_code}",
        f"Request headers: {dict(resp.request.headers)}",
    ]
    if resp.request.body:
        try:
            meta_lines.append(
                f"Request body: {resp.request.body.decode('utf-8') if hasattr(resp.request.body, 'decode') else resp.request.body}"
            )
        except Exception:
            meta_lines.append("Request body: <binary or non-decodable>")

    meta_lines.append(f"Response headers: {dict(resp.headers)}")
    meta_path.write_text("\n".join(meta_lines), encoding="utf-8")

    content_type = resp.headers.get("Content-Type", "")
    try:
        if "application/json" in content_type:
            body_path = body_path.with_suffix(".json")
            body_path.write_text(json.dumps(
                resp.json(), indent=2), encoding="utf-8")
        else:
            body_path = body_path.with_suffix(".txt")
            body_path.write_text(resp.text, encoding="utf-8")
    except Exception:
        body_path = body_path.with_suffix(".bin")
        body_path.write_bytes(resp.content)


def pretty_preview(resp: requests.Response, max_chars: int = 300) -> str:
    ct = resp.headers.get("Content-Type", "")
    try:
        if "application/json" in ct:
            text = json.dumps(resp.json(), indent=2)
        else:
            text = resp.text
    except Exception:
        return "<non-decodable response>"

    text = text.strip()
    return text[:max_chars] + ("... (truncated)" if len(text) > max_chars else "")


def run_item(session: requests.Session, item: Dict[str, Any], base_url: Optional[str] = None) -> None:
    name = item.get("name", "<unnamed>")
    req = item.get("request") or {}
    method = (req.get("method") or "GET").upper()
    url = req.get("url", "")
    headers_list = req.get("header") or []
    body = req.get("body") or {}

    # Build headers
    headers = {}
    for h in headers_list:
        key, val = h.get("key"), h.get("value")
        if key and val is not None:
            headers[key] = val

    # Resolve URL (optionally override scheme+host+port)
    final_url = override_base_url_if_provided(url, base_url)

    # Build payload
    data = None
    json_payload = None

    if body and body.get("mode") == "raw":
        raw = body.get("raw", "")
        content_type = headers.get("Content-Type", "")
        if "application/json" in content_type or raw.strip().startswith(("{", "[")):
            try:
                json_payload = json.loads(raw)
            except Exception:
                data = raw
        else:
            data = raw

    print(f"\n=== {name} ===")
    print(f"{method} {final_url}")

    try:
        resp = session.request(
            method=method,
            url=final_url,
            headers=headers,
            data=data,
            json=json_payload,
            timeout=TIMEOUT_SECONDS,
            verify=VERIFY_SSL,
        )
        print(f"→ Status: {resp.status_code}")
        print(pretty_preview(resp))
        save_response(name, resp)
    except requests.RequestException as e:
        print(f"Request failed: {e}")


def run_collection(collection_path: str, base_url: Optional[str] = DEFAULT_BASE_URL):
    ensure_output_dir()
    with open(collection_path, "r", encoding="utf-8") as f:
        col = json.load(f)

    items = col.get("item", [])
    session = make_session()

    # Optionally: add auth headers/cookies to session here.

    for item in items:
        run_item(session, item, base_url=base_url)
        time.sleep(0.2)  # small delay for readability


def main():
    # Usage:
    #   python run_postman_collection.py [collection_file] [base_url]
    # Examples:
    #   python run_postman_collection.py
    #   python run_postman_collection.py ARConstruction-API.postman_collection.json http://localhost:8000
    collection_file = sys.argv[1] if len(
        sys.argv) > 1 else DEFAULT_COLLECTION_FILE
    base_url = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_BASE_URL

    if not os.path.exists(collection_file):
        print(f"Collection not found: {collection_file}")
        sys.exit(1)

    run_collection(collection_file, base_url)


if __name__ == "__main__":
    main()
