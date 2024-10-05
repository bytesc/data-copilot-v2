import base64
import json

import pygwalker as pyg
import pandas as pd
import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException

from ask_ai import ask_ai_for_pd, ask_ai_for_graph,ask_ai_for_echart
import data_access.read_db

from pydantic import BaseModel

from config.get_config import config_data
from manuel_mode import pandas_html
from utils import path_tools

import logging

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

logging.basicConfig(filename='./ask_ai.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding="utf-8")


def fetch_data():
    dict_data, merged_dict_data = data_access.read_db.get_data_from_db()
    list_data = list(dict_data.values())
    merged_list_data = list(merged_dict_data.values())
    return dict_data, merged_dict_data, list_data, merged_list_data


print(fetch_data()[0])

logging.info("setting up")

app = FastAPI()



class AskRequest(BaseModel):
    question: str
    concurrent: int
    retries: int


@app.post("/ask-pd")
async def ask_pd(request: AskRequest):
    dict_data, merged_dict_data, list_data, merged_list_data = fetch_data()
    try:
        result, retries_used = ask_ai_for_pd.ask_pd(dict_data, request)
        if result is None:
            return {
                "code": 504,
                "retries_used": retries_used,
                "msg": "gen failed"
            }
        return {"code": 200,
                "retries_used": retries_used,
                "answer": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=508, detail=str(e))


@app.post("/ask-pd-walker")
async def ask_pd_walker(request: AskRequest):
    dict_data, merged_dict_data, list_data, merged_list_data = fetch_data()
    try:
        result, retries_used = ask_ai_for_pd.ask_pd(dict_data, request)
        if result is None:
            return {
                "code": 504,
                "retries_used": retries_used,
                "msg": "gen failed"
            }
        html = pandas_html.get_html(result)
        file_path = path_tools.generate_html_path()
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html)
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return {"code": 200,
                "retries_used": retries_used,
                "html": html_content}
    except Exception as e:
        raise HTTPException(status_code=508, detail=str(e))


@app.post("/ask-graph")
async def ask_graph(request: AskRequest):
    dict_data, merged_dict_data, list_data, merged_list_data = fetch_data()
    try:
        result, retries_used = ask_ai_for_graph.ask_graph(dict_data, request)
        if result is None:
            return {
                "code": 504,
                "retries_used": retries_used,
                "msg": "gen failed"
            }
        with open(result, "rb") as image_file:
            image_data = base64.b64encode(image_file.read())
        return {
            "code": 200,
            "retries_used": retries_used,
            "image_data": image_data.decode('utf-8')
        }
    except Exception as e:
        raise HTTPException(status_code=508, detail=str(e))


@app.post("/ask-echart")
async def ask_echart(request: AskRequest):
    dict_data, merged_dict_data, list_data, merged_list_data = fetch_data()
    try:
        result, retries_used = ask_ai_for_echart.ask_echart(dict_data, request)
        with open(result, 'r', encoding='utf-8') as file:
            html_content = file.read()
        if result is None:
            return {
                "code": 504,
                "retries_used": retries_used,
                "msg": "gen failed"
            }
        return {
            "code": 200,
            "retries_used": retries_used,
            "echart_html": html_content
        }
    except Exception as e:
        raise HTTPException(status_code=508, detail=str(e))

if __name__ == "__main__":
    logging.info("server starting")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
