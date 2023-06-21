import fitz

doc = fitz.open("whj_code1/github_code2/parse_paper_to_parts/example1_文字可编辑版/基于深度学习的海关虚假贸易案件罚款金额预测_胡鑫.pdf")

#提取所有文本
image_number=0
with open("whj_code1/github_code2/parse_paper_to_parts/example1_文字可编辑版/text.txt","w") as f:
    for page_index in range(len(doc)):
        page=doc[page_index]

        texts=page.get_text()
        f.write(texts)

        image_list = page.get_images()
        for image_index, img in enumerate(image_list, start=1): # enumerate the image list
            xref = img[0] # get the XREF of the image
            pix = fitz.Pixmap(doc, xref) # create a Pixmap

            if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                pix = fitz.Pixmap(fitz.csRGB, pix)

            pix.save("whj_code1/github_code2/parse_paper_to_parts/example1_文字可编辑版/pics/图"+str(image_number)+".png") # save the image as png
            pix = None
            image_number+=1