import redis, json, requests
from urllib.parse import urlparse

r = redis.Redis(host="redis", port=6379, decode_responses=True)

# ------------------ Proxy 기능 ------------------


# store proxy data
def store_proxy_data(task_id, request_data, response_data):
    data = {
        "request": request_data,
        "response": response_data
    }
    r.set(task_id, json.dumps(data))


# get proxy data
def get_proxy_data(task_id):
    data = r.get(task_id)
    return json.loads(data) if data else {}


# modify request
def modify_request(task_id, new_request):
    data = get_proxy_data(task_id)
    if not data:
        raise ValueError("No proxy data found for this task")
    data["edited_request"] = new_request
    r.set(task_id, json.dumps(data))
    return {
        "before_request": data["request"],
        "after_request": new_request
    }


# modify response
def send_modified_request(task_id):
    data = get_proxy_data(task_id)
    if not data or "edited_request" not in data:
        raise ValueError("No edited request data found for this task")

    modified_request = data["edited_request"]
    parsed_request = parse_http_request(modified_request)
    url = parsed_request["url"]
    method = parsed_request["method"]
    headers = parsed_request["headers"]
    body = parsed_request["body"]

    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, data=body)
    else:
        raise ValueError("Unsupported HTTP method")

    data["modified_response"] = response.text
    r.set(task_id, json.dumps(data))
    return {
        "modified_request": modified_request,
        "modified_response": response.text
    }


# ------------------ HTTP Request Parsing ------------------
def parse_http_request(raw_request):
    print("[DEBUG] raw_request =", repr(raw_request))  # 여기
    lines = raw_request.split("\\n")  # 중요!

    #
    method, url, _ = lines[0].split(" ")
    headers = {}
    body = None
    is_body = False

    for line in lines[1:]:
        if line == "":
            is_body = True
            continue
        if is_body:
            body = line
        else:
            key, value = line.split(": ", 1)
            headers[key] = value

    parsed_url = urlparse(url)
    return {
        "method": method,
        "url": f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}",
        "headers": headers,
        "body": body
    }
