import fitz,os,re,json,tabula

### 需要用户手动定义的部分
pdf_file_path="whj_code1/github_code2/parse_paper_to_parts/example1_文字可编辑版/基于深度学习的海关虚假贸易案件罚款金额预测_胡鑫.pdf"
output_folder="whj_code1/github_code2/parse_paper_to_parts/example1_文字可编辑版/extract_result"  #下次更新检验这个文件夹是否存在，现在请存在


### 执行代码部分
def process_text(text:str,body_titles:list=[],position:str="正文"):
    """将PDF提取的文本转换为正常分段"""
    if position=="正文":
        text=re.sub(r'\[\d+\]', '', text)  #删除引用标
    lines = text.split('\n')
    paragraph_segmentations=".。:："
        
    for i in range(len(lines)):
        if any([lines[i].endswith(paragraph_segmentation+" ") or lines[i].endswith(paragraph_segmentation) \
                for paragraph_segmentation in paragraph_segmentations]):
            lines[i]+="\n"
        if any([lines[i].startswith(body_title) for body_title in body_titles]):
            lines[i]="\n\n"+lines[i]+"\n"
        if lines[i]=="!":
            lines[i]=""
    return ''.join(lines)

def extract_id(description:str,type:str="图"):
    """从图片描述文本中提取ID"""
    line_id=description.split()[0]
    if line_id==type:
        return ' '.join(description.split()[:2])
    else:
        return line_id


doc = fitz.open(pdf_file_path)

#提取文字和图表
filename_with_extension=os.path.basename(pdf_file_path)
filename, _ = os.path.splitext(filename_with_extension)
output_text_file=open(os.path.join(output_folder,filename+"_text.txt"),"w")
output_image={}
output_table={}

image_output_folder=os.path.join(output_folder,filename+"_pic")
if not os.path.exists(image_output_folder):
    os.makedirs(image_output_folder)

bio_status=0  #0前言，1摘要，2目录，2.5不需要的目录，3正文，4参考文献，5附录
body_titles=[]

zancun_id=set()
zancunlujing_list=[]
if_zancunlujing=False
for page_index in range(len(doc)):
    page=doc[page_index]

    texts=page.get_text()
    if texts.strip()=="":
        continue
    
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
                if "绪论" in item:
                    break
            for item in items[item_index:]:
                for p in re.finditer(r'\.\s*\.',item):
                    break
                body_title=item[:p.span()[0]].strip()
                if len(body_title)>0 and bool(re.search(r'[\u4e00-\u9fff]+',body_title)):
                    body_titles.append(body_title)

        else:
            output_text_file.write("\n\nAbstract\n"+process_text(texts[abstract.span()[1]:]))
    elif bio_status==2:
        if not re.search(body_titles[0],texts) is None:
            bio_status=3
        elif (re.search(r"插\s*图",texts) is not None) or (re.search(r"表\s*格",texts) is not None):
            bio_status=2.5
        else:
            items=texts.split("\n")
            for item_index in range(len(items)):
                item=items[item_index].strip()
                if item.endswith("1") and not item.startswith("目录"):
                    break
            for item in items[item_index:]:
                for p in re.finditer(r'\.\s*\.',item):
                    break
                body_title=item[:p.span()[0]].strip()
                if len(body_title)>0 and bool(re.search(r'[\u4e00-\u9fff]+',body_title)):
                    body_titles.append(body_title)
    elif bio_status==2.5:
        if not re.search(body_titles[0],texts) is None:
            bio_status=3
    
    if bio_status==3:
        if "参考文献 " in texts.split("\n"):
            bio_status=4
            output_text_file.write("\n\n")
        else:
            write_text_total=texts
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
                
                line=texts2[line_index+2]  #TODO: 这个位置我怎么决定是1还是2？
                description=line[4].strip()
                try:
                    line_id=extract_id(description)
                except IndexError as e:
                    line=texts2[line_index+3]
                    description=line[4].strip()
                    line_id=extract_id(description)
                write_text_total=write_text_total.replace(description,"")
                if not description.startswith("图"):  #子图
                    if_zancunlujing=True
                    for lineindex in range(line_index,len(texts2)):
                        bigger_description=texts2[lineindex][4].strip()
                        if bigger_description.startswith("图"):
                            line_id=extract_id(bigger_description)+" "+line_id
                            description=bigger_description+" "+description
                            if len(zancunlujing_list)>0:
                                for zancunlujing in zancunlujing_list:
                                    dir_name, file_name = os.path.split(zancunlujing)
                                    new_file_name=extract_id(bigger_description)+" "+file_name
                                    new_file_path=os.path.join(dir_name,new_file_name)
                                    os.rename(zancunlujing, new_file_path)
                            zancunlujing_list=[]
                            if_zancunlujing=False
                            break
                        
                output_image[line_id]=line[4].strip()

                xref = img[0] # get the XREF of the image
                pix = fitz.Pixmap(doc, xref) # create a Pixmap

                if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                picture_path=os.path.join(image_output_folder,line_id+".png")
                if if_zancunlujing:
                    zancunlujing_list.append(picture_path)
                try:
                    pix.save(picture_path,output="png") # save the image as png
                except RuntimeError as e:  #RuntimeError: pixmap must be grayscale or rgb to write as png
                    newpix = fitz.Pixmap(fitz.csRGB,pix)
                    newpix.save(picture_path,output="png")
                pix = None
            
            #提取表格
            if len(re.findall(r'表 \d+-\d+',texts))>0:
                for sentence in texts.split("\n"):
                    if re.match(r'表 \d+-\d+',sentence):
                        description=sentence
                        write_text_total=write_text_total.replace(description,"")
                        table_id=extract_id(description,"表")
                        output_table[table_id]={"description":description,"value":[]}
                tables=tabula.read_pdf(pdf_file_path,pages=page_index,multiple_tables=True)
                if len(tables)>0:
                    for table in tables:
                        for index, row in table.iterrows():
                            output_table[table_id]["value"].append(list(row))
                else:
                    pass #TODO: 说明有表格没有提取成功

            

            
            output_text_file.write(process_text(write_text_total,body_titles))

    if bio_status==4:
        output_text_file.write(process_text("\n".join(texts.split("\n")[3:-1]),body_titles,position="参考文献"))

json.dump(output_image,open(os.path.join(output_folder,filename+"_pic.json"),"w"),ensure_ascii=False)
json.dump(output_table,open(os.path.join(output_folder,filename+"_table.json"),"w"),ensure_ascii=False)

output_text_file.close()