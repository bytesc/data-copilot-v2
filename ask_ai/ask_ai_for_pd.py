import concurrent

from llm_access.LLM import llm
from manuel_mode import pandas_html

from config.get_config import config_data
from ask_ai import ask_api

import pandas as pd


def ask_pd(data, question):
    graph_type = """ 
    the Python function should return a single pandas dataframe only!!! 
    here is an example: 
    ```python
    import pandas as pd

    def process_data(dataframes_list):
        # generate code to perform operations here
        return result
    ```
    """
    question = question + graph_type
    tries = 1
    while 1:
        clean_data_pd_list = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(ask_api.ask, data,
                                       question, llm) for _ in range(tries*config_data['ai']['concurrent'])]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                print(result, "\n--------------------------------")
                if not isinstance(result, pd.DataFrame):
                    result = None
                if result is not None:
                    clean_data_pd_list.append(result)
                    print(result, "\n*************************")
                    if len(clean_data_pd_list) >= config_data['ai']['wait']:
                        break

            if len(clean_data_pd_list) != 0:
                clean_data_pd = clean_data_pd_list[0]
                tb_data = [clean_data_pd.columns.to_list()] + clean_data_pd.values.tolist()
                return tb_data
            else:
                if tries <= config_data['ai']['tries']:
                    tries += 1
                    print(tries, "##############")
                    continue
                print("gen failed")
                return None
