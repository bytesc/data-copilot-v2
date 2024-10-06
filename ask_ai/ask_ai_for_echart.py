import concurrent

from llm_access.LLM import llm
from utils.output_parsing import parse_output
from ask_ai import input_process
from config.get_config import config_data
from ask_ai import ask_api

from utils import path_tools


def get_ask_echart_block_prompt(req):
    question = req.question
    graph_type = """
        use pyecharts 2.0. the Python function should only return a string of html. do not save it.
        no graph title
        """

    example_code = """
        here is an example: 
        ```python
        def process_data(dataframes_dict):
            import pandas as pd
            import math
            from pyecharts import options as opts
            from pyecharts.charts import *
            from pyecharts.globals import *

            # generate code to perform operations here

            html_string = chart.render_notebook().data # this returns a html string
            return html_string
        ```
        """
    return question + graph_type + example_code


def ask_echart_block(data, req):
    tries = 1
    while 1:
        result_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(ask_api.ask, data,
                                       get_ask_echart_block_prompt(req)
                                       , llm,
                                       str, req.retries) for _ in range(req.concurrent)]
            for future in concurrent.futures.as_completed(futures):
                result, retries_used, all_prompt = future.result()
                if result is not None:
                    result_list.append(result)
                    if len(result_list) >= config_data['ai']['wait']:
                        break

            if len(result_list) != 0:
                for result in result_list:
                    return result, retries_used, all_prompt
            else:
                if tries < config_data['ai']['tries']:
                    tries += 1
                    print(tries, "##############")
                    continue
                print("gen failed")
                return None, retries_used, all_prompt


def get_ask_echart_file_prompt(req):
    question = req.question
    graph_type = input_process.get_chart_type(question) + """
            use pyecharts 2.0. the Python function should return a string file path in ./tmp_imgs/ only 
            and the graph html generated should be stored in that path. 
            no graph title
            file path must be:
            """

    example_code = """
            here is an example: 
            ```python
            def process_data(dataframes_dict):
                import pandas as pd
                import math
                from pyecharts import options as opts
                from pyecharts.charts import *
                from pyecharts.globals import *
                # generate code to perform operations here
                return html_string
            ```
            """
    return question + graph_type + path_tools.generate_html_path() + example_code


def ask_echart_file(data, req):
    tries = 1
    while 1:
        result_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(ask_api.ask, data,
                                       get_ask_echart_block_prompt(req)
                                       , llm,
                                       str, req.retries) for _ in range(req.concurrent)]
            for future in concurrent.futures.as_completed(futures):
                result, retries_used, all_prompt = future.result()
                graph_path = parse_output.parse_output_html(result)
                if graph_path is not None:
                    result_list.append(graph_path)
                    print(graph_path, "\n*************************")
                    if len(result_list) >= config_data['ai']['wait']:
                        break

            if len(result_list) != 0:
                for graph_path in result_list:
                    return graph_path, retries_used, all_prompt
            else:
                if tries < config_data['ai']['tries']:
                    tries += 1
                    print(tries, "##############")
                    continue
                print("gen failed")
                return None, retries_used, all_prompt
