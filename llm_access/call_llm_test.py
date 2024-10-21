from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
# pip install -U langchain-community
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
# pip install dashscope

from langchain.globals import set_llm_cache

set_llm_cache(None)


def call_llm(question, llm):
    prompt = PromptTemplate(template="{question}", input_variables=["question"])
    llm_chain = prompt | llm
    ans = llm_chain.invoke(question)
    return ans
