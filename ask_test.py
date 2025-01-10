import os
import re
import shutil

from llm_access.LLM import get_llm
from config.get_config import config_data

import logging

import http.client
import json


llm = get_llm()

logging.info("setting up")

conn = http.client.HTTPConnection(f"127.0.0.1:8007")


def send_request(request_data):
    json_data = json.dumps(request_data)
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        conn.request("POST", "/ask/echart-file-2", body=json_data, headers=headers)
        response = conn.getresponse()
        return response.status, response.read()
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


if __name__ == "__main__":
    request = {
        "question": "List the top 10 countries where the official language has more than 50% speakers along with their capital and population.",
        "concurrent": [1, 1],
        "retries": [5, 5]
    }
    status_code, response = send_request(request)
    print(status_code)
    print(response)
    response=json.loads(response)
    print(response["file"])

    # 检查文件是否存在
    if os.path.exists(response["file"]):
        # 获取文件名和扩展名
        file_name = os.path.basename(response["file"])
        file_name_without_extension = os.path.splitext(file_name)[0]
        file_extension = os.path.splitext(file_name)[1]

        # 构建新的文件名
        new_file_name = f"temp{file_extension}"

        # 复制文件到当前目录并重命名
        shutil.copy(response["file"], os.path.join(os.getcwd(), new_file_name))
        print(f"File copied and renamed to {new_file_name}")
