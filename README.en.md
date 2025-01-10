# data-copilot

✨ **Natural Language Database Query System (RAG) based on langchain and Large Language Models (LLM)**

Utilizing natural language queries, this system intelligently parses database structures using large language models, enabling intelligent multi-table structured queries and statistical computations on data. It also smartly generates various charts based on query results. Implemented with Pywebio interactive frontend web pages, without the need for OpenAI API, it's 100% pure Python code.

🚩[简体中文文档](./README.md)

[Personal website: www.bytesc.top](http://www.bytesc.top)

🔔 For project-related inquiries, feel free to raise an issue in this repository. I typically respond within 24 hours.


## Feature Overview

- 1. Natural language querying
- 2. Implementation of structured queries and statistical computations across multiple tables
- 3. Smart generation of various types of charts and interactive chart creation
- 4. Intelligent parsing of database structures, no additional configuration needed for different MySQL databases
- 5. Support for concurrent multithreaded queries
- 6. Ability to handle exceptions such as instability in large language model performance
- 7. Support for local offline deployment (GPU required) using Hugging Face format models (e.g., `qwen-7b`)
- 8. Support for API interfaces in OpenAI format and Dashscope's `qwen`


## Technological Innovations

- Enable retrying of questions by feeding back information from exceptions and assertions, improving the stability of outputs from LLM.
- Implement multi-threading for concurrent questioning to enhance response speed and stability.
- Utilize DataFrame mapping in databases to avoid the risk of SQL injection attacks by manipulating the LLM through induced queries.
- Introduce word embedding models and vector databases as a replacement for simple regular expressions, in order to address the challenge of mapping fuzzy outputs from LLM to specific system code executions.


- ✨ Utilize BERT (Bidirectional Encoder Representations from Transformers) to **vectorize** the question text and prompt, and then apply linear regression, logistic regression, neural networks (nn), and Transformer models for **regression**. **Predict** the appropriate concurrency levels and retry counts based on the question text, and compare the effectiveness of different models.


## Basic Technical Principles


### Basic flow of single-instance generation

![Basic Flow](./readme_img/t1.png)

1. After the natural language question is input into the system, it will be combined with the pre-set toolset description information to form a prompt and input into the LLM, allowing the LLM to select the appropriate tool for solving the problem.

2. Retrieve the structural information of the data from the database (Dataframe data summary).

3. Input the data summary and tool suggestion information into the LLM to write Python code to solve the problem.

4. Extract the code from the LLM's response and execute it with the Python interpreter.

5. If an exception occurs during code execution, combine the exception information with the problem code to form a new prompt and re-input it into the LLM for another attempt (return to step `3`). Continue until the code runs successfully or the maximum number of retries is exceeded.

6. If no exception occurs during code execution, assert the program output. If it is not the expected type, combine the assertion information with the problem code to form a new prompt and re-input it into the LLM for another attempt (return to step `3`). Continue until the assertion is successful or the maximum number of retries is exceeded.

7. Display the successful code execution output (charts) on the user interface and launch the interactive plotting interface based on the output data.

#### Learning for Retries

![](./readme_img/t10.png)

Using the BERT (Bidirectional Encoder Representation from Transformers) combined with `regression` , predict the optimal retries value based on the difficulty of the question. Find a balance between the success rate of generation and the number of retries to improve response speed.


### Concurrency generation control

![Concurrency Control](./readme_img/t3.png)

Repeated feedback of exceptions and assertions can cause the prompt to become increasingly long, causing the LLM to lose focus and affect the generation effect. The LLM's first incorrect response can also affect subsequent generations. Starting over may yield better results.

Therefore, multi-threaded concurrent execution is introduced to ask questions independently multiple times, reducing the probability of overall generation failure caused by unstable LLM outputs, and improving system stability and response speed.

#### Learning for Concurrent

![](./readme_img/t11.png)

Using BERT combined with `regression`, predict the best number of concurrent requests (Concurrent) based on the difficulty of the question. Find a balance between the success rate of generation and the cost of LLM (Large Language Model) invocation to improve response speed.


## How to Use

### Installing Dependencies

Python version 3.9

```bash
pip install -r requirement.txt
```

### Fill in Configuration Information

The configuration file is located at `./config/config.yaml`.

#### Database Configuration

Simply provide the connection information. The model will automatically read the database structure, so no additional configuration is needed.

```yaml
mysql: mysql+pymysql://root:123456@127.0.0.1/data_copilot
# mysql: mysql+pymysql://username:password@host:port/database
```

#### Large Language Model Configuration

If using the Dashscope `qwen` API (recommended):

```yaml
llm:
  model_provider: qwen #qwen #openai
  model: qwen1.5-110b-chat
  url: ""

# qwen1.5-72b-chat   qwen1.5-110b-chat
# qwen-turbo  qwen-plus   qwen-max   qwen-long
# https://dashscope.aliyun.com/
```

Also, in `llm_access/LLM.py`, uncomment the following line:


```yaml
llm:
  model_provider: openai
  model: glm-4
  url: "https://open.bigmodel.cn/api/paas/v4/"

# glm-4
# https://open.bigmodel.cn
```


If offline deployment is needed, relevant code is in `./llm_access/qwen_access.py`.

#### Obtaining API Key

If obtaining the API key from [Alibaba Cloud Dashscope](https://dashscope.console.aliyun.com/) for the `qwen` large language model,

save the API key to `llm_access/api_key_qwen.txt`.

If using the API key for the `openai` format API,

save the API key to `llm_access/api_key_openai.txt`.

### Running

`main.py` is the entry point of the project. Running this file will start the server.

```bash
python main.py
```

By default, you can access it via the browser at [http://127.0.0.1:8087/](http://127.0.0.1:8087/).

The current v2 version only provides an API and does not have a graphical interface. You can run `ask_test.py` for testing.

```bash
python ask_test.py
```

The generated charts will be saved to `.temp.html` or `.temp.png`.

### Potential Future Directions

The challenge of this project lies in mapping from **user's natural language vague queries** and **natural language responses from a large language model** to **deterministic data** that traditional non-AI computer code can handle.

At its current stage, this project, along with some other open-source implementations (such as `langchain agent`), relies on **repeated questioning** to elicit responses from the large language model that closely match the predefined format of natural language responses. Then, **regular expressions** are used to match the data.

While large language models offer high flexibility and can implement various complex intelligent database queries, statistics, and plotting functions, they face fatal bottlenecks in terms of input-output scale. They cannot directly handle extremely long texts or large datasets. Therefore, they may not perform well when faced with structural information of large-scale data (e.g., hundreds of tables).

Although large language models can to some extent control relatively deterministic output formats through prompts, they are fundamentally still natural language outputs, exhibiting unstable output characteristics and emergent problems. They cannot guarantee acceptable results or the rationality and accuracy of the results.

Thus, innovation in this area may be a possible future direction for this project.

#### Vector Databases and Word Embedding Models

![](./readme_img/t9.png)

Introducing word embedding models (such as `text2vec-base-multilingual`) and vector databases (such as `PGVector`) can improve the handling of large-scale data.

By transforming large-scale data into vectors on a per-item basis and mapping vocabulary into a lower-dimensional vector space, semantic relationships between words can be captured. By storing these vectors in a vector database, we can swiftly perform similarity queries, clustering, and other operations, facilitating effective processing of large-scale data.
Moreover, vector databases can match only predetermined results that are semantically closest, mitigating the instability and emergent issues often associated with large language models.

The integration of vector databases and word embedding models helps overcome the instability of large language models and their limitations in handling large-scale data. By combining the stability and reliability of vector databases with the intelligence and flexibility of large language models, efficient and stable processing and analysis of large-scale data can be achieved.

The relevant technical resources can be found in the `./pgv/` folder.

#### Related Links

Word Embedding Models:

- `text2vec-large-chinese` [huggingface](https://huggingface.co/GanymedeNil/text2vec-large-chinese) [hf-mirror](https://hf-mirror.com/GanymedeNil/text2vec-large-chinese)
- `text2vec-base-multilingual` [huggingface](https://huggingface.co/shibing624/text2vec-base-multilingual) [hf-mirror](https://hf-mirror.com/shibing624/text2vec-base-multilingual)

Vector Databases:

- `PGVector` [DockerHub](https://hub.docker.com/r/ankane/pgvector) [dockerproxy](https://dockerproxy.com/docs)

To be continued...

