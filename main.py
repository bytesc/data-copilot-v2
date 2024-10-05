import base64

import pygwalker as pyg
import pandas as pd
import matplotlib.pyplot as plt

from fastapi import FastAPI, HTTPException

from ask_ai import ask_ai_for_pd, ask_ai_for_graph
import data_access.read_db

from pydantic import BaseModel

from config.get_config import config_data
from manuel_mode import pandas_html

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def fetch_data():
    dict_data, merged_dict_data = data_access.read_db.get_data_from_db()
    list_data = list(dict_data.values())
    merged_list_data = list(merged_dict_data.values())
    return dict_data, merged_dict_data, list_data, merged_list_data


print(fetch_data()[0])


app = FastAPI()


class AskRequest(BaseModel):
    question: str
    concurrent: float
    retries: float


@app.post("/ask-pd")
async def ask_pd(request: AskRequest):
    dict_data, merged_dict_data, list_data, merged_list_data = fetch_data()
    try:
        result = ask_ai_for_pd.ask_pd(list_data + merged_list_data, request.question)
        return {"code": 200, "answer": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=508, detail=str(e))


@app.post("/ask-pd-walker")
async def ask_pd(request: AskRequest):
    dict_data, merged_dict_data, list_data, merged_list_data = fetch_data()
    try:
        result = ask_ai_for_pd.ask_pd(list_data + merged_list_data, request.question)
        html = pandas_html.get_html(result)
        return {"code": 200, "html": html}
    except Exception as e:
        raise HTTPException(status_code=508, detail=str(e))


@app.post("/ask-graph")
async def ask_graph(request: AskRequest):
    dict_data, merged_dict_data, list_data, merged_list_data = fetch_data()
    try:
        result = ask_ai_for_graph.ask_graph(list_data + merged_list_data, request.question)
        with open(result, "rb") as image_file:
            image_data = base64.b64encode(image_file.read())
        return {
            "code": 200,
            "image_data": image_data.decode('utf-8')
        }
    except Exception as e:
        raise HTTPException(status_code=508, detail=str(e))


if __name__ == "__main__":
    # ans1 = ask_graph("查询订单分布情况")
    # print(ans1)
    # ans2 = ask_pd("查询订单分布情况")
    # print(ans2)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
