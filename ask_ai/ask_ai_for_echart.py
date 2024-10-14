import concurrent

from utils.output_parsing import parse_output
from ask_ai import input_process
from config.get_config import config_data
from ask_ai import ask_api

from utils import path_tools


def get_ask_echart_block_prompt(req):
    question = req.question
    graph_type = """
        use pyecharts 2.0. the Python function should only return a string of html. do not save it.
        please choose different graph type based on the question, do not always use bar. 
        no graph title no set theme! no theme! no theme ! 
        """

    example_code = """
        here is an example: 
        ```python
        def process_data(dataframes_dict):
            import pandas as pd
            import math
            from pyecharts import #
            # do not set theme!!!
            # generate code to perform operations here

            html_string = chart.render_notebook().data # this returns a html string
            return html_string
        ```
        """
    return question + graph_type + example_code


def ask_echart_block(data, req, llm):
    tries = 1
    while 1:
        result_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(ask_api.ask, data,
                                       get_ask_echart_block_prompt(req),
                                       llm,
                                       parse_output.assert_str
                                       , req.retries) for _ in range(req.concurrent)]
            for future in concurrent.futures.as_completed(futures):
                result, retries_used, all_prompt = future.result()
                if result is not None:
                    result_list.append([result, retries_used])
                    if len(result_list) >= config_data['ai']['wait']:
                        break

            if len(result_list) != 0:
                for item in result_list:
                    return item[0], item[1], all_prompt, len(result_list)/req.concurrent
            else:
                if tries < config_data['ai']['tries']:
                    tries += 1
                    print(tries, "##############")
                    continue
                print("gen failed")
                return None, retries_used, all_prompt, 0.0


def get_ask_echart_file_prompt(req, tmp_file=False):
    question = req.question
    graph_type = """
            use pyecharts 2.0. the Python function should return a string file path in ./tmp_imgs/ only 
            and the graph html generated should be stored in that path. 
            please choose different graph type based on the question, do not always use bar.  
            no graph title no set theme! no theme! no theme ! 
            file path must be:
            """

    example_code = """
            here is an example: 
            ```python
            def process_data(dataframes_dict):
                import pandas as pd
                import math
                from pyecharts import #
                # generate code to perform operations here
                chart.render(file_path)
                return file_path
            ```
            """
    if not tmp_file:
        return question + graph_type + path_tools.generate_html_path() + example_code
    else:
        return question + graph_type + "./tmp_imgs/tmp.html" + example_code


def ask_echart_file(data, req, llm):
    tries = 1
    while 1:
        result_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(ask_api.ask, data,
                                       get_ask_echart_file_prompt(req),
                                       llm,
                                       parse_output.assert_html_file,
                                       req.retries) for _ in range(req.concurrent)]
            for future in concurrent.futures.as_completed(futures):
                result, retries_used, all_prompt = future.result()
                graph_path = parse_output.parse_output_html(result)
                if graph_path is not None:
                    result_list.append([graph_path, retries_used])
                    print(graph_path, "\n*************************")
                    if len(result_list) >= config_data['ai']['wait']:
                        break

            if len(result_list) != 0:
                for item in result_list:
                    return item[0], item[1], all_prompt, len(result_list)/req.concurrent
            else:
                if tries < config_data['ai']['tries']:
                    tries += 1
                    print(tries, "##############")
                    continue
                print("gen failed")
                return None, retries_used, all_prompt, 0.0
