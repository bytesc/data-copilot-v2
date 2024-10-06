import concurrent

from utils.output_parsing import parse_output
from ask_ai import input_process
from config.get_config import config_data
from ask_ai import ask_api

from utils import path_tools


def get_ask_graph_prompt(req, llm):
    question = req.question
    graph_type = input_process.get_chart_type(question, llm) + """
        use matplotlib. the Python function should return a string file path in ./tmp_imgs/ only 
        and the image generated should be stored in that path. 
        file path must be:
        """

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
    return question + graph_type + path_tools.generate_img_path() + example_code


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
                    result_list.append(img_path)
                    print(img_path, "\n*************************")
                    if len(result_list) >= config_data['ai']['wait']:
                        break

            if len(result_list) != 0:
                for path in result_list:
                    print("img_path:", path)
                    return path, retries_used, all_prompt
            else:
                if tries < config_data['ai']['tries']:
                    tries += 1
                    print(tries, "##############")
                    continue
                print("gen failed")
                return None, retries_used, all_prompt

