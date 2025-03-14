import concurrent

from utils.output_parsing import parse_output
from ask_ai import input_process
from config.get_config import config_data
from ask_ai import ask_api

from utils import path_tools


def get_ask_graph_prompt(req, llm, tmp_file=False, img_type=True):
    question = req.question
    graph_type = """
        use matplotlib. the Python function should return a string file path in ./tmp_imgs/ only 
        and the image generated should be stored in that path. 
        file path must be:
        """
    if img_type:
        graph_type = input_process.get_chart_type(question, llm) + graph_type
    example_code = """
        here is an example: 
        ```python
        def process_data(dataframes_dict):
            import pandas as pd
            import math
            import matplotlib.pyplot as plt
            import matplotlib
            import PIL
            # generate code to perform operations here
            return path
        ```
        """
    if not tmp_file:
        return question + graph_type + path_tools.generate_img_path() + example_code
    else:
        return question + graph_type + "./tmp_imgs/tmp.png" + example_code


def ask_graph(data, req, llm):
    tries = 1
    while 1:
        result_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(ask_api.ask, data,
                                       get_ask_graph_prompt(req, llm),
                                       llm,
                                       parse_output.assert_png_file
                                       , req.retries) for _ in range(req.concurrent)]
            for future in concurrent.futures.as_completed(futures):
                result, retries_used, all_prompt = future.result()
                img_path = parse_output.parse_output_img(result)
                if img_path is not None:
                    result_list.append([img_path,retries_used])
                    print(img_path, "\n*************************")
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
