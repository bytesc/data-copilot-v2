from llm_access import call_llm_test

from utils.output_parsing import parse_output

import time
import logging


def get_final_prompt(data, question):
    def slice_dfs(df_dict, lines=5):
        top_five_dict = {}
        for key, df in df_dict.items():
            top_five_dict[key] = df.head(min(lines, len(df)))
        return top_five_dict
    data_slice = slice_dfs(data)
    pre_prompt = """
    Write a Python function called process_data that takes only a pandas dataframe dict called data as input
    that performs the following operations:
    """

    data_prompt = """
    Here is the dataframe dict sample(it is just data structure samples not real data): 
    """

    end_prompt = """
    code should be completed in a single md code blocks without any additional comments, explanations or cmds.
    the function should not be called. do not print anything in the function.
    please import the module you need, modules must be imported inside the function.
    do not mock any data !!!
    """

    all_prompt = pre_prompt + question + "\n" + data_prompt + str(data_slice) + "\n" + end_prompt
    return all_prompt


def ask(data, question, llm, assert_func, retries=0):
    all_prompt = get_final_prompt(data, question)
    retries_times = 0
    error_msg = ""
    wrong_code = ""
    while retries_times <= retries:
        retries_times += 1

        ans = call_llm_test.call_llm(all_prompt + wrong_code + error_msg, llm)

        ans_code = parse_output.parse_generated_code(ans)

        print(f"\n {time.time()} \nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx \n retries_times:{retries_times} \n")
        print(ans_code)
        print("\nxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")

        if ans_code:
            try:
                local_namespace = {'data': data, 'result': None}
                exec(ans_code, globals(), local_namespace)
                result = local_namespace['process_data'](data)
                assert_result = assert_func(result)
                if assert_result:
                    raise Exception(assert_result)
                return result, retries_times-1, all_prompt
            except Exception as e:
                wrong_code = "the code was executed: ```python\n" + ans_code + "\n```"
                error_msg = "the code raise Exception:" + str(e) + """
                    please regenerate all the complete code again based on the above information. """
                print(f"An error occurred while executing the code: \n {e}")
        else:
            error_msg = """code should only be in md code blocks: 
            ```python
                # some python code
            ```
            without any additional comments, explanations or cmds !!!"""
            logging.error(all_prompt + ans + "No code was generated.")
            print("No code was generated.")

    logging.error(all_prompt + wrong_code + error_msg)
    return None, retries_times-1, all_prompt
