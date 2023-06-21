# parse_paper_to_parts
解析PDF格式的论文（解析成文本、图、表格）

（我举的例子都下载自知网。如果它们侵犯了您的合法权益，请联系我删除）

v-0.0.1: 实现简单的提取文本和图表。缺点：①子图暂时只能处理子图上下分布的情况，左右分布的暂时无法处理 ②暂时仅考虑文本可编辑的情况，且仅在一篇论文上测试实现 ③有一些公式和表格无法通过PyMuPDF或者tabula-py提取，我猜应该还是需要用目标检测方法实现提取 

参考资料：
1. <https://github.com/Alihassan7212/PDF-extraction-and-dissection/blob/main/project.py>
