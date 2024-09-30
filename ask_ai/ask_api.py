from config.get_config import config_data

from llm_access import call_llm_test

from output_parsing import parse_output

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import PIL


def top_five_dfs(df_list):
    top_fives = []
    for df in df_list:
        top_fives.append(df.head(min(5, len(df))))
    return top_fives


def ask(data, question, llm):
    data_slice = top_five_dfs(data)
    pre_prompt = """
    Write a Python function called process_data that takes only a pandas dataframe list called data as input
    that performs the following operations:
    """

    prompt = """
    code should be in md code blocks without any additional comments or explanations.
    the function should not be called. 
    """

    end_prompt = """
    please import the module you need.
    do not mock any data !!!
    """

    all_prompt = pre_prompt + "\n" + str(data_slice) + "\n" + question + "\n" + prompt + end_prompt

    print(all_prompt)

    ans = call_llm_test.call_llm(all_prompt, llm)

    ans_code = parse_output.parse_generated_code(ans)

    print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")
    print(ans_code)

    if ans_code:
        try:
            local_namespace = {'data': data, 'result': None}
            exec(ans_code, globals(), local_namespace)
            result = local_namespace['process_data'](data)
            return result
        except Exception as e:
            print(f"An error occurred while executing the code: {e}")
            return None
    else:
        print("No code was generated.")
        return None

