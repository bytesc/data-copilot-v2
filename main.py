import base64

import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException

from ask_ai import ask_ai_for_pd, ask_ai_for_graph, ask_ai_for_echart, ask_api
import data_access.read_db

from pydantic import BaseModel

from utils.manuel_mode import pandas_html
from utils import path_tools
from llm_access.LLM import get_llm

import logging

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

logging.basicConfig(filename='./ask_ai.log', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', encoding="utf-8")


llm = get_llm()


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
    result, retries_used, all_prompt, success = ask_ai_for_pd.ask_pd(dict_data, request, llm)
    if result is None:
        return {
            "code": 504,
            "retries_used": retries_used,
            "msg": "gen failed",
            "answer": "",
            "prompt": all_prompt,
            "success": 0.0
        }
    return {"code": 200,
            "retries_used": retries_used,
            "answer": result.to_dict(),
            "prompt": all_prompt,
            "success": success
            }


@app.post("/ask/pd-walker")
async def ask_pd_walker(request: AskRequest):
    dict_data = fetch_data()
    try:
        result, retries_used, all_prompt, success = ask_ai_for_pd.ask_pd(dict_data, request, llm)
        if result is None:
            return {
                "code": 504,
                "retries_used": retries_used,
                "msg": "gen failed",
                "html": "",
                "file": "",
                "prompt": all_prompt,
                "success": 0.0
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
                "html": html_content,
                "file": file_path,
                "prompt": all_prompt,
                "success": success
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/graph")
async def ask_graph(request: AskRequest):
    dict_data = fetch_data()
    try:
        result, retries_used, all_prompt, success = ask_ai_for_graph.ask_graph(dict_data, request, llm)
        if result is None:
            return {
                "code": 504,
                "retries_used": retries_used,
                "msg": "gen failed",
                "image_data": "",
                "file": "",
                "prompt": all_prompt,
                "success": 0.0
            }
        with open(result, "rb") as image_file:
            image_data = base64.b64encode(image_file.read())
        return {
            "code": 200,
            "retries_used": retries_used,
            "image_data": image_data.decode('utf-8'),
            "file": result,
            "prompt": all_prompt,
            "success": success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/echart-block")
async def ask_echart_block(request: AskRequest):
    dict_data = fetch_data()
    try:
        result, retries_used, all_prompt, success = ask_ai_for_echart.ask_echart_block(dict_data, request, llm)
        if result is None:
            return {
                    "code": 504,
                    "retries_used": retries_used,
                    "msg": "gen failed",
                    "html": "",
                    "file": "",
                    "prompt": all_prompt,
                    "success": 0.0
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
            "html": html_content,
            "file": file_path,
            "prompt": all_prompt,
            "success": success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/echart-file")
async def ask_echart_file(request: AskRequest):
    dict_data = fetch_data()
    try:
        result, retries_used, all_prompt, success = ask_ai_for_echart.ask_echart_file(dict_data, request, llm)
        if result is None:
            return {
                "code": 504,
                "retries_used": retries_used,
                "msg": "gen failed",
                "html": "",
                "file": "",
                "prompt": all_prompt,
                "success": 0.0
            }
        with open(result, 'r', encoding='utf-8') as file:
            html_content = file.read()
        logging.info(request.question, result)
        return {
            "code": 200,
            "retries_used": retries_used,
            "html": html_content,
            "file": result,
            "prompt": all_prompt,
            "success": success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prompt/pd")
async def prompt_pd(request: AskRequest):
    dict_data = fetch_data()
    all_prompt = ask_api.get_final_prompt(dict_data, ask_ai_for_pd.get_ask_pd_prompt(request))
    return {"code": 200,
            "all_prompt": all_prompt}


@app.post("/prompt/graph")
async def prompt_graph(request: AskRequest):
    dict_data = fetch_data()
    all_prompt = ask_api.get_final_prompt(dict_data, ask_ai_for_graph.get_ask_graph_prompt(request, llm,
                                                                                           tmp_file=True,
                                                                                           img_type=False))
    return {"code": 200,
            "all_prompt": all_prompt}


@app.post("/prompt/echart-block")
async def prompt_echart_block(request: AskRequest):
    dict_data = fetch_data()
    all_prompt = ask_api.get_final_prompt(dict_data, ask_ai_for_echart.get_ask_echart_block_prompt(request))
    return {"code": 200,
            "all_prompt": all_prompt}


@app.post("/prompt/echart-file")
async def prompt_echart_file(request: AskRequest):
    dict_data = fetch_data()
    all_prompt = ask_api.get_final_prompt(dict_data, ask_ai_for_echart.get_ask_echart_file_prompt(request, tmp_file=True))
    return {"code": 200,
            "all_prompt": all_prompt}


if __name__ == "__main__":
    logging.info("server starting")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
