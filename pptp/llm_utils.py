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