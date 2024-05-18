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

import os, re


def check_or_create_directory(directory: str):
    """检查文件夹是否存在，如不存在将自动创建"""
    assert not os.path.isfile(directory)  # 路径不能是文件夹
    if not os.path.exists(directory):
        os.makedirs(directory)


def deduplicate_insert_file(file_path: str):
    """该函数采用指定的文件路径，并检查是否存在具有相同名称的文件。
    如果文件存在，则在文件名后面加上一个后缀，如(1)、(2)等，直到找到一个不存在的文件名为止。"""
    directory, filename = os.path.split(file_path)
    basename, ext = os.path.splitext(filename)
    counter = 1

    while os.path.exists(file_path):
        new_basename = re.sub(
            r"\s*\(\d+\)$", "", basename
        )  # remove existing counter from basename
        new_basename = f"{new_basename} ({counter})"
        filename = f"{new_basename}{ext}"
        file_path = os.path.join(directory, filename)
        counter += 1

    return file_path
