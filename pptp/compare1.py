import fitz

doc = fitz.open(
    "whj_code1/github_code2/parse_paper_to_parts/example1_文字可编辑版/基于深度学习的海关虚假贸易案件罚款金额预测_胡鑫.pdf"
)

# 提取所有文本
with open(
    "whj_code1/github_code2/parse_paper_to_parts/example1_文字可编辑版/text2.txt", "w"
) as f:
    for page in doc:
        texts = page.get_text()
        f.write(texts)
