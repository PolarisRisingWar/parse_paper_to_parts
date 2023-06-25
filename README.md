# parse_paper_to_parts
解析PDF格式的论文（解析成文本、图、表格）

（我举的例子都下载自知网。如果它们侵犯了您的合法权益，请联系我删除）

实现简单的提取文本和图表。缺点：①子图暂时只能处理子图上下分布的情况，左右分布的暂时无法处理 ②暂时仅考虑文本可编辑的情况，且仅在一篇论文上测试实现。不可编辑的PDF（扫描件）应该必须要用OCR实现了 ③有一些公式和表格无法通过PyMuPDF或者tabula-py提取，我猜应该还是需要用目标检测方法实现提取（我用的PyMuPDF无法解析特殊字符，包括①②这种。有一些格式的论文PDF的公式可以解析为文本，但是只能复制而不是直接以LaTeX公式形式呈现所以……）  ④关于页眉页脚和页码的去除，应该需要针对每篇PDF计算其正文的box位置范围 ⑤使用AI的部分可能会出现无法预知的错误（有些可以预知的已经在处理了，不可预知的我也没办法了） 
v-0.0.2: 更新了使用ChatGPT获取标题、图片描述的功能；解决了子图无法处理的问题  
下个版本的更新计划：实现OCR（我得找服务器负责人安一下<https://tesseract-ocr.github.io/tessdoc/InstallationOpenSuse.html>，明天再说）；试用ScanSSD <https://ws-dl.blogspot.com/2020/06/2020-06-05-math-formula-extraction-from.html> 提取公式  
呼吁大家捐款给我买Aspose和mathpix的API，再捐点我去买个medium会员看一下这篇博文：<https://towardsdatascience.com/extracting-text-from-scanned-pdf-using-pytesseract-open-cv-cd670ee38052>（也可以直接等我到下个月看哈）

参考资料：
1. <https://github.com/Alihassan7212/PDF-extraction-and-dissection/blob/main/project.py>
