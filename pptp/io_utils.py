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

import os

def check_or_create_directory(directory:str):
    """检查文件夹是否存在，如不存在将自动创建"""
    assert not os.path.isfile(directory)  #路径不能是文件夹
    if not os.path.exists(directory):
        os.makedirs(directory)
