import json
from urllib.parse import parse_qs


def parse_query(environ):
    return {k: v[0] for k, v in parse_qs(environ.get("QUERY_STRING", "")).items()}


def parse_body(environ):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""
    ctype = environ.get("CONTENT_TYPE", "")
    if "application/json" in ctype:
        return json.loads(body.decode("utf-8") or "{}")
    return {k: v[0] for k, v in parse_qs(body.decode("utf-8")).items()}


def text_resp(text, status="200 OK"):
    return status, [("Content-Type", "text/html; charset=utf-8")], text


def json_resp(data, status="200 OK"):
    return status, [("Content-Type", "application/json; charset=utf-8")], json.dumps(data, ensure_ascii=False).encode("utf-8")


def tr(gettext, key, lang=None):
    return gettext(key, lang)
