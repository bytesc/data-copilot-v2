import concurrent

import pandas as pd

from llm_access.LLM import llm
from output_parsing import parse_output
from ask_ai import input_process
from config.get_config import config_data
from ask_ai import ask_api

import random
import string


def generate_random_string(length=8):
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for _ in range(length))
    return random_string


def generate_img_path():
    return "./tmp_imgs/"+generate_random_string()+".png"


def ask_graph(data, req):
    question = req.question
    graph_type = input_process.get_chart_type(question) + """
    the Python function should a string file path in ./tmp_imgs/ only 
    and the image generated should be stored in that path. 
    file path:
    """

    example_code = """
    here is an: 
    ```python
    import pandas as pd
    import math
    import matplotlib.pyplot as plt
    import matplotlib
    import PIL

    def process_data(dataframes_dict):
        # generate code to perform operations here
        return path
    ```
    """
    tries = 1
    while 1:
        result_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(ask_api.ask, data,
                                       question + graph_type + generate_img_path() + example_code
                                       , llm,
                                       str, req.retries) for _ in range(req.concurrent)]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                img_path = parse_output.parse_output_img(result)
                if img_path is not None:
                    result_list.append(img_path)
                    print(img_path, "\n*************************")
                    if len(result_list) >= config_data['ai']['wait']:
                        break

            if len(result_list) != 0:
                for path in result_list:
                    print("img_path:", path)
                    return path
            else:
                if tries <= config_data['ai']['tries']:
                    tries += 1
                    print(tries, "##############")
                    continue
                print("gen failed")
                return None

