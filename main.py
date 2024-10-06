import base64

import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException

from ask_ai import ask_ai_for_pd, ask_ai_for_graph, ask_ai_for_echart, ask_api
import data_access.read_db

from pydantic import BaseModel

from utils.manuel_mode import pandas_html
from utils import path_tools

import logging

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

logging.basicConfig(filename='./ask_ai.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding="utf-8")


def fetch_data():
    dict_data = data_access.read_db.get_data_from_db()
    return dict_data

print(fetch_data())

logging.info("setting up")

app = FastAPI()


class AskRequest(BaseModel):
    question: str
    concurrent: int
    retries: int


@app.post("/ask/pd")
async def ask_pd(request: AskRequest):
    dict_data = fetch_data()
    result, retries_used, all_prompt = ask_ai_for_pd.ask_pd(dict_data, request)
    if result is None:
        return {
            "code": 504,
            "retries_used": retries_used,
            "all_prompt": all_prompt,
            "msg": "gen failed"
        }
    return {"code": 200,
            "retries_used": retries_used,
            "all_prompt": all_prompt,
            "answer": result.to_dict()}


@app.post("/ask/pd-walker")
async def ask_pd_walker(request: AskRequest):
    dict_data = fetch_data()
    try:
        result, retries_used, all_prompt = ask_ai_for_pd.ask_pd(dict_data, request)
        if result is None:
            return {
                "code": 504,
                "retries_used": retries_used,
                "all_prompt": all_prompt,
                "msg": "gen failed"
            }
        html = pandas_html.get_html(result)
        file_path = path_tools.generate_html_path()
        print(file_path)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(html)
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        logging.info(request.question, result)
        return {"code": 200,
                "retries_used": retries_used,
                "all_prompt": all_prompt,
                "html": html_content,
                "file": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/graph")
async def ask_graph(request: AskRequest):
    dict_data = fetch_data()
    try:
        result, retries_used, all_prompt = ask_ai_for_graph.ask_graph(dict_data, request)
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
            "all_prompt": all_prompt,
            "image_data": image_data.decode('utf-8'),
            "file": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/echart-block")
async def ask_echart_block(request: AskRequest):
    dict_data = fetch_data()
    try:
        result, retries_used, all_prompt = ask_ai_for_echart.ask_echart_block(dict_data, request)
        if result is None:
            return {
                    "code": 504,
                    "retries_used": retries_used,
                    "all_prompt": all_prompt,
                    "msg": "gen failed"
            }
        file_path = path_tools.generate_html_path()
        print(file_path)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(result)
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        logging.info(request.question, file_path)
        return {
            "code": 200,
            "retries_used": retries_used,
            "all_prompt": all_prompt,
            "html": html_content,
            "file": file_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/echart-file")
async def ask_echart_file(request: AskRequest):
    dict_data = fetch_data()
    try:
        result, retries_used, all_prompt = ask_ai_for_echart.ask_echart_file(dict_data, request)
        if result is None:
            return {
                "code": 504,
                "retries_used": retries_used,
                "all_prompt": all_prompt,
                "msg": "gen failed"
            }
        with open(result, 'r', encoding='utf-8') as file:
            html_content = file.read()
        logging.info(request.question, result)
        return {
            "code": 200,
            "retries_used": retries_used,
            "all_prompt": all_prompt,
            "html": html_content,
            "file": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logging.info("server starting")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
