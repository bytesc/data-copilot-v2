import re

import pandas


def parse_output_img(txt):
    try:
        # 定义正则表达式模式
        pattern = r"tmp_imgs/[^\s/]+\.png"
        matched_paths = re.findall(pattern, str(txt))
    except Exception as e:
        print("parsing err", e)
        matched_paths = []

    if len(matched_paths) == 0:
        return None

    return matched_paths[0]


def parse_output_html(txt):
    try:
        # 定义正则表达式模式
        pattern = r"tmp_imgs/[^\s/]+\.html"
        matched_paths = re.findall(pattern, str(txt))
    except Exception as e:
        print("parsing err", e)
        matched_paths = []

    if len(matched_paths) == 0:
        return None

    return matched_paths[0]


def parse_generated_code(txt):
    matches = []
    try:
        matches = re.findall(r'```python(.*?)```', txt, re.DOTALL)
    except Exception as e:
        print("parsing err", e)

    if len(matches) == 0:
        return None
    return matches[0]


def assert_png_file(txt):
    path = parse_output_img(txt)
    if path is None:
        return f"function should return a string png file path in ./tmp_imgs/ only, but get {txt}"
    else:
        return None


def assert_html_file(txt):
    path = parse_output_html(txt)
    if path is None:
        return f"function should return a string html file path in ./tmp_imgs/ only, but get {txt}"
    else:
        return None


def assert_pd(obj):
    try:
        assert isinstance(obj, pandas.DataFrame), \
            f"Expected result to be of type {pandas.DataFrame.__name__}, but got a {type(obj)}."
    except Exception as e:
        return str(e)
    return None


def assert_str(obj):
    try:
        assert isinstance(obj, str), \
            f"Expected result to be of type {str.__name__}, but got a {type(obj)}."
    except Exception as e:
        return str(e)
    return None
