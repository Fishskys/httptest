import json
from urllib.parse import urlencode, urlparse, parse_qsl
import uncurl  # 需要 pip install uncurl


def generate_curl_command(method, url, params, headers, body):
    """根据请求信息生成 cURL 字符串"""
    if params:
        if "?" not in url:
            url += "?"
        else:
            url += "&"
        url += urlencode(params)

    cmd = f"curl -X {method} '{url}'"
    for k, v in headers.items():
        cmd += f" \\\n  -H '{k}: {v}'"

    if body and method in ["POST", "PUT", "PATCH"]:
        body_escaped = body.replace("'", "'\\''")
        cmd += f" \\\n  -d '{body_escaped}'"

    return cmd


def parse_curl_command(curl_cmd):
    """解析 cURL 字符串为 Python 对象"""
    ctx = uncurl.parse_context(curl_cmd)
    p_url = urlparse(ctx.url)

    # 整理 Body
    body_str = ""
    if ctx.data:
        if isinstance(ctx.data, str):
            body_str = ctx.data
        else:
            body_str = json.dumps(ctx.data, indent=4)

    return {
        "method": ctx.method.upper(),
        "url": f"{p_url.scheme}://{p_url.netloc}{p_url.path}",
        "params": parse_qsl(p_url.query),
        "headers": ctx.headers,
        "body": body_str,
    }
