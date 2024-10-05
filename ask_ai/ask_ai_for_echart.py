import concurrent

import pandas as pd

from llm_access.LLM import llm
from output_parsing import parse_output
from ask_ai import input_process
from config.get_config import config_data
from ask_ai import ask_api

from utils import path_tools


def ask_echart(data, req):
    question = req.question
    graph_type = input_process.get_chart_type(question) + """
    use pyecharts. the Python function should return a string file path in ./tmp_imgs/ only 
    and the graph html generated should be stored in that path. 
    file path:
    """

    example_code = """
    here is an: 
    ```python
    import pandas as pd
    import math
    from pyecharts import options as opts
    from pyecharts.charts import *
    from pyecharts.globals import *

    def process_data(dataframes_dict):
        # generate code to perform operations here
        return html_string
    ```
    """
    tries = 1
    while 1:
        result_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(ask_api.ask, data,
                                       question + graph_type + path_tools.generate_html_path() + example_code
                                       , llm,
                                       str, req.retries) for _ in range(req.concurrent)]
            for future in concurrent.futures.as_completed(futures):
                result, retries_used = future.result()
                graph_path = parse_output.parse_output_html(result)
                if graph_path is not None:
                    result_list.append(graph_path)
                    print(graph_path, "\n*************************")
                    if len(result_list) >= config_data['ai']['wait']:
                        break

            if len(result_list) != 0:
                for graph_path in result_list:
                    return graph_path, retries_used
            else:
                if tries < config_data['ai']['tries']:
                    tries += 1
                    print(tries, "##############")
                    continue
                print("gen failed")
                return None, retries_used

