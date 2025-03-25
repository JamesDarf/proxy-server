from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils import store_proxy_data, get_proxy_data, modify_request, send_modified_request

proxy_router = APIRouter()

class ProxyEditRequest(BaseModel):
    task_seq_num: str
    edit_packet_data: str


# /proxy/store
@proxy_router.post("/proxy/store/{task_id}")
def store_proxy(task_id: str, request: str, response: str):
    store_proxy_data(task_id, request, response)
    return {"message": "Stored successfully"}



# /proxy/get
@proxy_router.get("/proxy/get/{task_id}")
def get_proxy(task_id: str):
    data = get_proxy_data(task_id)
    if not data:
        raise HTTPException(status_code=404, detail="No proxy data found")
    return data


# /proxy/edit
@proxy_router.post("/proxy/edit/{task_id}")
def edit_proxy(task_id: str, request_data: ProxyEditRequest):
    result = modify_request(task_id, request_data.edit_packet_data)
    return result


# /proxy/send
@proxy_router.post("/proxy/send/{task_id}")
def send_proxy(task_id: str):
    result = send_modified_request(task_id)
    return result
