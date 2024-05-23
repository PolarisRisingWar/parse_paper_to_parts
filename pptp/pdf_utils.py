#    Copyright 2023 Wang Huijuan

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import re


def process_text(text: str, body_titles: list = [], position: str = "正文"):
    """
    将PDF提取的文本转换为正常分段，指将奇怪的换行删掉，用标签符号换行。
    正文同时删除引用标，暂时只支持类似[12]的情况
    """
    if position == "正文":
        text = re.sub(r"\[\d+\]", "", text)  # 删除引用标
    lines = text.split("\n")
    paragraph_segmentations = ".。:："

    for i in range(len(lines)):
        if any(
            [
                lines[i].endswith(paragraph_segmentation + " ")
                or lines[i].endswith(paragraph_segmentation)
                for paragraph_segmentation in paragraph_segmentations
            ]
        ):
            lines[i] += "\n"
        if any([lines[i].startswith(body_title) for body_title in body_titles]):
            lines[i] = "\n\n" + lines[i] + "\n"
        if lines[i] == "!":
            lines[i] = ""
    return "".join(lines)


def extract_id(description: str, type: str = "图"):
    """从图表描述文本中提取ID，如图1-1等"""
    line_id = description.split()[0]
    if line_id == type:
        return " ".join(description.split()[:2])
    else:
        return line_id

def zhengwen_open_page(introduction_title,block_text):
    if introduction_title.split()[1] in block_text[0][4]:
        return True
    else:
        return False