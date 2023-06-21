import fitz,os,re,json
import tabula

### 需要用户手动定义的部分
pdf_file_path="whj_code1/github_code2/parse_paper_to_parts/example1_文字可编辑版/基于深度学习的海关虚假贸易案件罚款金额预测_胡鑫.pdf"
output_folder="whj_code1/github_code2/parse_paper_to_parts/example1_文字可编辑版/extract_result"  #下次更新检验这个文件夹是否存在，现在请存在


### 执行代码部分
def process_text(text:str,body_titles:list=[]):
    """将PDF提取的文本转换为正常分段"""
    lines = text.split('\n')
    paragraph_segmentations=".。:："
        
    for i in range(len(lines)):
        if any([lines[i].endswith(paragraph_segmentation+" ") for paragraph_segmentation in paragraph_segmentations])\
            or any([body_title in lines[i] for body_title in body_titles]):
            
            lines[i]+="\n"
    return ''.join(lines)

def extract_id(description:str):
    """从图片描述文本中提取ID"""
    line_id=description.split()[0]
    if line_id=="图":
        return ' '.join(description.split()[:2])
    else:
        return line_id


doc = fitz.open(pdf_file_path)

#提取文字和图表
filename_with_extension=os.path.basename(pdf_file_path)
filename, _ = os.path.splitext(filename_with_extension)
output_text_file=open(os.path.join(output_folder,filename+"_text.txt"),"w")
output_image={}
output_table_file=open(os.path.join(output_folder,filename+"_table.json"),"w")

image_output_folder=os.path.join(output_folder,filename+"_pic")
if not os.path.exists(image_output_folder):
    os.makedirs(image_output_folder)

bio_status=0  #0前言，1摘要，2目录，3正文，4参考文献，5附录
body_titles=[]

for page_index in range(len(doc)):
    page=doc[page_index]

    texts=page.get_text()
    
    if bio_status==0 and not re.search(r"摘\s*要",texts) is None:
        output_text_file.write("摘要\n"+process_text(texts[re.search(r"摘\s*要",texts).span()[1]:]))
        bio_status=1
    elif bio_status==1:
        abstract=re.search("Abstract",texts)
        catalog=re.search(r"目\s*录",texts)
        if abstract is None and catalog is None:
            output_text_file.write(process_text(texts))
        elif catalog is not None:
            bio_status=2
            items=texts.split("\n")
            for item_index in range(len(items)):
                item=items[item_index].strip()
                if item.endswith("1") and not item.startswith("目录"):
                    break
            for item in items[item_index:]:
                body_title=item[:item.find("..")].strip()
                if len(body_title)>0:
                    body_titles.append(body_title)

        else:
            output_text_file.write("\n\nAbstract\n"+process_text(texts[abstract.span()[1]:]))
    elif bio_status==2:
        if not re.search(body_titles[0],texts) is None:
            bio_status=3
        else:
            items=texts.split("\n")
            for item_index in range(len(items)):
                item=items[item_index].strip()
                if item.endswith("1") and not item.startswith("目录"):
                    break
            for item in items[item_index:]:
                body_title=item[:item.find("..")].strip()
                if len(body_title)>0:
                    body_titles.append(body_title)
    
    if bio_status==3:
        output_text_file.write(process_text(texts,body_titles))

        #提取图片
        image_list = page.get_images(full=True)

        convert_names=[]
        for image_index, img in enumerate(image_list, start=1): # enumerate the image list
            y1=page.get_image_bbox(img)[3]  #下沿位置
            texts2=page.get_text("blocks",sort=True)

            for line_index in range(len(texts2)):
                line=texts2[line_index]
                if int(line[3])==int(y1):  #因为有误差所以不能精确相等
                    break
            
            line=texts2[line_index+2]
            description=line[4].strip()
            if not description.startswith("图"):  #子图
                if texts2[line_index+3][4].strip().startswith("图"):
                    pass #TODO: 合并图片

            line_id=extract_id(description)

            output_image[line_id]=line[4].strip()

            xref = img[0] # get the XREF of the image
            pix = fitz.Pixmap(doc, xref) # create a Pixmap

            if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                pix = fitz.Pixmap(fitz.csRGB, pix)

            pix.save(os.path.join(image_output_folder,line_id+".png"),output="png") # save the image as png
            pix = None
        
        #提取表格
        tables=tabula.read_pdf(pdf_file_path,pages=page_index,multiple_tables = True)
        if len(tables)>0:
            print(tables)
            break

json.dump(output_image,open(os.path.join(output_folder,filename+"_pic.json"),"w"),ensure_ascii=False)