import PIL.Image
import pandas as pd
from pandasai import Agent, SmartDatalake
import matplotlib.pyplot as plt

import data_access.read_db
# from llm_access.qwen_access import llm
from llm_access.glm_access import llm
from output_parsing import parse_img
from input_process import input_process

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.ioff()

import pywebio


def main():

    pywebio.output.put_markdown("# Data Copilot")
    pywebio.output.put_markdown("## 自然语言数据库查询")

    dict_data = data_access.read_db.get_data_from_db()
    list_data = list(dict_data.values())
    pywebio.output.put_table([list(dict_data.keys())])

    dirty_data_lake = SmartDatalake(list_data, config={"llm": llm,
                                            "save_charts": False,
                                            "save_charts_path": "./tmp_imgs/",
                                            "open_charts": False,
                                            "enable_cache": False,
                                            "max_retries": 5})

    # 获取用户输入
    question = pywebio.input.input("请输入你的问题")
    pywebio.output.put_text(question)
    # ans = lake.chat('在哪 2 个国家销量最少？ ，同时画出它们的饼图')   # 同时给出pandas
    # ans = lake.chat('查询Liam 的工资')

    while 1:
        while 1:
            pywebio.output.popup("数据查询中", [
                pywebio.output.put_text(question),
                pywebio.output.put_text("数据查询"),
                pywebio.output.put_loading(),
            ])

            graph_type = input_process.get_chart_type(question)
            print(question, graph_type, "\n--------------------------------")

            clean_data_pd = dirty_data_lake.chat(question + "!!!return single pandas dataframe only!!! ")
            print(clean_data_pd, "\n--------------------------------")

            if not isinstance(clean_data_pd, pd.DataFrame):
                pywebio.output.popup("失败", [
                    pywebio.output.put_text("查询失败"),
                    pywebio.output.put_text(clean_data_pd),
                ])
                clean_data_pd = None
                break

            tb_data = [clean_data_pd.columns.to_list()] + clean_data_pd.values.tolist()
            print(tb_data)
            pywebio.output.popup("画图中", [
                pywebio.output.put_text(question),
                pywebio.output.put_text("数据查询成功"),
                pywebio.output.put_text("画图中"),
                pywebio.output.put_loading(),
                pywebio.output.put_table(tb_data),
            ])
            pywebio.output.put_table(tb_data),

            clean_data_lake = SmartDatalake([clean_data_pd], config={"llm": llm,
                                                     "save_charts": True,
                                                     "save_charts_path": "./tmp_imgs/",
                                                     "open_charts": False,
                                                     "enable_cache": False,
                                                     "max_retries": 5})

            img_ans = clean_data_lake.chat(question + graph_type)
            print(img_ans, "\n--------------------------------")

            img_path = parse_img.parse_output_img(img_ans)
            if img_path is not None:
                # print("img_path:", img_path)
                graph_img = PIL.Image.open(img_path)

                pywebio.output.popup("画图完成", [
                    pywebio.output.put_text("画图成功"),
                    # pywebio.output.put_text(img_ans),
                    pywebio.output.put_image(graph_img)
                ])
                pywebio.output.put_image(graph_img)
                break
            else:
                pywebio.output.popup("失败", [
                    pywebio.output.put_text("画图失败"),
                    pywebio.output.put_text(img_ans),
                ])
                break

        # 定义两个按钮的操作
        actions = [
            {'label': '重新查询', 'value': 'c'},
            {'label': '高级模式', 'value': 'g'}
        ]
        # 显示按钮并获取用户点击的结果
        selected_action = pywebio.input.actions('接下来', actions)

        if selected_action == 'g':
            from manuel_mode import pandas_html
            html = pandas_html.get_html(clean_data_pd)
            pywebio.output.clear()
            pywebio.output.put_text("高级模式 刷新以输入新的查询")
            pywebio.output.put_html('<div style="position: absolute; left: 0; right: 0;"> ' + html + "</div>")
            break

        if selected_action == 'c':
            continue
        else:
            break


if __name__ == "__main__":
    pywebio.start_server(main,
                         port=8087)
