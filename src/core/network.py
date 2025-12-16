import requests
import json
from requests.auth import HTTPBasicAuth


def send_http_request(method, url, params, headers, body_raw, auth_type, auth_data):
    """
    发送 HTTP 请求的核心纯函数
    :return: requests.Response 对象
    """
    # 1. 处理 Auth
    auth_obj = None
    if auth_type == "Bearer Token":
        token = auth_data.get("token", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    elif auth_type == "Basic Auth":
        u = auth_data.get("username", "").strip()
        p = auth_data.get("password", "").strip()
        auth_obj = HTTPBasicAuth(u, p)

    # 2. 处理 Body (JSON vs Raw)
    json_data = None
    data_payload = None

    if body_raw:
        try:
            # 尝试作为 JSON 解析
            json_data = json.loads(body_raw)
        except:
            # 解析失败则作为普通字符串字节流
            data_payload = body_raw.encode("utf-8")

    # 3. 智能判断 Content-Type
    user_ct = next((k for k in headers.keys() if k.lower() == "content-type"), None)

    # 如果用户没指定 Content-Type 且 body 是 JSON，requests 会自动处理 json 参数
    # 如果用户指定了 Content-Type，或者 body 不是 JSON，则使用 data 参数
    final_json = json_data if (json_data and not user_ct) else None
    final_data = (
        json.dumps(json_data).encode("utf-8")
        if (json_data and user_ct)
        else data_payload
    )

    if not url:
        raise Exception("Empty URL")
    if not url.startswith("http"):
        url = "http://" + url

    # 4. 发送请求
    return requests.request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        auth=auth_obj,
        json=final_json,
        data=final_data,
        timeout=15,
    )
