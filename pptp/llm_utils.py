from dotenv import load_dotenv
import os

from datetime import datetime

load_dotenv()

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OpenAI_API_KEY"), base_url=os.getenv("OpenAI_BASE_URL")
)

log_file_handle = open(
    os.path.join("llmlogs",datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "llm.log"), "a", encoding="utf-8"
)


def pure_predict(system_instruct: str, query: str):
    response = client.chat.completions.create(
        model=os.getenv("OpenAI_model", "gpt-3.5-turbo"),
        messages=[
            {"role": "system", "content": system_instruct},
            {"role": "user", "content": query},
        ],
    )
    response_message = response.choices[0].message.content
    log_file_handle.write(
        "instruction: "
        + system_instruct
        + "\nquery: "
        + query
        + "\nresponse: "
        + response_message
        + "\n\n\n*****************************\n\n\n"
    )
    return response_message


@retry(wait=wait_random_exponential(min=20, max=600), stop=stop_after_attempt(6))
def first_page_title(first_page_text):
    return pure_predict(
        "请直接输出如下文本中的中文论文标题，不要带其他任何内容", first_page_text
    )


@retry(wait=wait_random_exponential(min=20, max=600), stop=stop_after_attempt(6))
def from_catalog_extract_titles(catalog_text):
    return pure_predict(
        "请直接输出如下目录中的标题内容，要求从第一章绪论开始，格式类似于['第一章 绪论','1.1 研究背景及意义','1.2 实验数据集']这样的Python列表文本（可以直接用Python的`eval()`函数转换为列表对象的字符串），要求列表中的元素是完全出自原文的，包含序号（可能为第一章或者第1章等写法）和标题本体（如绪论或研究背景等）",
        catalog_text,
    )


@retry(wait=wait_random_exponential(min=20, max=600), stop=stop_after_attempt(6))
def from_image_text_extract_description_and_id(input_image):
    return pure_predict(
        "请根据输入的文本抽取对应的图片序号和标题。\n如果这段文本描述的是一张单图，则直接输出该图片的序号和标题。举例：文字内容是“图 1-2 Doc2vec 添加段落特征预测下一个词”，输出结果应为['图 1-2','图 1-2 Doc2vec 添加段落特征预测下一个词']，要求输出可以通过Python的eval()函数直接转化为列表对象的字符串，不要包含换行符，方括号外不要包含引号，序号完全和原文保持一致，不要多加或去掉空格。\n如果这段文本描述的是一张图片的多张子图，仅输出大图的文字内容和对应序号",
        input_image,
    )
