import dashscope

from config.get_config import config_data
from llm_access import get_api


def get_llm():
    model_provider = config_data['llm']['model_provider']
    if model_provider == "qwen":
        from langchain_community.llms import Tongyi

        dashscope.api_key = get_api.get_api_key_from_file()
        llm = Tongyi(dashscope_api_key=get_api.get_api_key_from_file(),
                     model_name=config_data['llm']['model'])

        # path = r'D:\IDLE\big\qwen\models\Qwen-1_8B-Chat'
        # from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
        # from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        # # pip install tiktoken torch
        # # pip install transformers_stream_generator einops
        # # pip install accelerate
        # tokenizer = AutoTokenizer.from_pretrained(path, revision='master', trust_remote_code=True)
        # model = AutoModelForCausalLM.from_pretrained(path, revision='master', device_map="auto", trust_remote_code=True)
        # pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=10)
        # llm = HuggingFacePipeline(pipeline=pipe)

    else:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            temperature=0.95,
            model=config_data['llm']['model'],
            openai_api_key=get_api.get_api_key_from_file("./llm_access/api_key_openai.txt"),
            openai_api_base=config_data['llm']['url'],
        )
    return llm
