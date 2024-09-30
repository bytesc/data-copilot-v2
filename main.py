import pandas as pd
import matplotlib.pyplot as plt

from ask_ai import ask_ai_for_pd, ask_ai_for_graph
import data_access.read_db

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

def ask_pd(question):
    dict_data, merged_dict_data, list_data, merged_list_data = fetch_data()
    try:
        result = ask_ai_for_pd.ask_pd(list_data + merged_list_data, question)
        print(result)
    except Exception as e:
        print(e)


def ask_graph(question):
    dict_data, merged_dict_data, list_data, merged_list_data = fetch_data()
    try:
        result = ask_ai_for_graph.ask_graph(list_data + merged_list_data, question)
        print(result)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    ask_graph("查询订单分布情况")
