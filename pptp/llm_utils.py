import openai

from keys import *

openai.api_key=OPENAI_API_KEY
openai.proxy=OPENAI_PROXY

def first_page_title(first_page_text):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "请直接输出如下抽取文本中的中文论文标题，不要带其他任何内容："+first_page_text}
        ]
    )

    return completion.choices[0].message['content']

def from_catalog_extract_titles(catalog_text):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": "请直接输出如下目录中的标题内容，要求从第一章绪论开始，格式类似于['第一章 绪论','1.1 研究背景及意义','1.2 实验数据集']这样的Python列表文本（可以直接用Python的`eval()`函数转换为列表对象的字符串），要求列表中的元素是完全出自原文的，包含序号（可能为第一章或者第1章等写法）和标题本体（如绪论或研究背景等）\n"\
                        +catalog_text}
        ]
    )

    return completion.choices[0].message['content']