import string
import random


def generate_random_string(length=8):
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for _ in range(length))
    return random_string


def generate_img_path():
    return "./tmp_imgs/"+generate_random_string()+".png"


def generate_html_path():
    return "./tmp_imgs/"+generate_random_string()+".html"
