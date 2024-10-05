import pywebio.output
from pyecharts.charts import Bar
from pyecharts import options as opts

# 定义 draw_chart 函数
def draw_chart(x_label, data):
    chart = (
        Bar()
        .add_xaxis(x_label)
        .add_yaxis("output_value", data)
        .set_global_opts(title_opts={"text": "模型输出", "subtext": ""})
    )
    return chart.render_notebook()

# 模拟数据
x_labels = ["数据1", "数据2", "数据3", "数据4", "数据5"]
data_values = [10, 20, 30, 40, 50]


res = draw_chart(x_labels, data_values)
print(res.data)

pywebio.output.put_html("""


""")
