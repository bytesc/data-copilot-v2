import concurrent

from llm_access.LLM import llm

from config.get_config import config_data
from ask_ai import ask_api

import pandas as pd
from utils.output_parsing import parse_output

def get_ask_pd_prompt(req):
    question = req.question
    example_code = """ 
       the Python function should return a single pandas dataframe only!!! 
       here is an example: 
       ```python
       def process_data(dataframes_dict):
           import pandas as pd
           import math
           # generate code to perform operations here
           return result
       ```
       """
    return question + example_code


def ask_pd(data, req):
    tries = 1
    while 1:
        clean_data_pd_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(ask_api.ask, data,
                                       get_ask_pd_prompt(req),
                                       llm,
                                       parse_output.assert_pd,
                                       req.retries) for _ in range(req.concurrent)]
            for future in concurrent.futures.as_completed(futures):
                result, retries_used = future.result()
                if result is not None:
                    clean_data_pd_list.append(result)
                    print(result, "\n*************************")
                    if len(clean_data_pd_list) >= config_data['ai']['wait']:
                        break

            if len(clean_data_pd_list) != 0:
                clean_data_pd = clean_data_pd_list[0]
                return clean_data_pd, retries_used
            else:
                if tries < config_data['ai']['tries']:
                    tries += 1
                    print(tries, "##############")
                    continue
                print("gen failed")
                return None, retries_used
