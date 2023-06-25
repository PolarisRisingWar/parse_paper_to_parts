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

import fitz,os,re,json,tabula

from io_utils import *
from pdf_utils import *
from llm_utils import *

### 需要用户手动定义的部分
pdf_file_path="whj_code1/github_code2/parse_paper_to_parts/examples/example1_文字可编辑版/基于深度学习的海关虚假贸易案件罚款金额预测_胡鑫.pdf"
output_folder="whj_code1/github_code2/parse_paper_to_parts/examples/example1_文字可编辑版/extract_result"  #可以不存在


### 执行代码部分
check_or_create_directory(output_folder)


doc = fitz.open(pdf_file_path)

#提取文字和图表
filename_with_extension=os.path.basename(pdf_file_path)
filename,_=os.path.splitext(filename_with_extension)
output_text_file=open(os.path.join(output_folder,filename+"_text.txt"),"w")
output_image={}
output_table={}

image_output_folder=os.path.join(output_folder,filename+"_pic")
check_or_create_directory(image_output_folder)

bio_status=0  #0前言，1摘要，2目录，3正文，4参考文献，5附录

body_titles=[]  #标题列表

for page_index in range(len(doc)):
    page=doc[page_index]

    texts=page.get_text()

    if page_index==0:
        title=first_page_title(texts)
        output_text_file.write("标题："+title+"\n\n")
        continue

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
            body_titles.extend(eval(from_catalog_extract_titles(texts)))

        else:
            output_text_file.write("\n\nAbstract\n"+process_text(texts[abstract.span()[1]:]))
    elif bio_status==2:
        if not re.search(body_titles[0],texts) is None:
            bio_status=3
        elif (re.search(r"插\s*图",texts) is not None) or (re.search(r"表\s*格",texts) is not None):
            bio_status=2.5
        else:
            body_titles.extend(eval(from_catalog_extract_titles(texts)))
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
            image_list=page.get_images(full=True)

            convert_names=[]
            for image_index, img in enumerate(image_list, start=1): # enumerate the image list
                y1=page.get_image_bbox(img)[3]  #下沿位置
                texts2=page.get_text("blocks",sort=True)

                for line_index in range(len(texts2)):
                    line=texts2[line_index]
                    if int(line[3])==int(y1):  #因为有误差所以不能精确相等
                        break
                
                if line_index<len(texts2)-5:
                    line="\n".join([x[4] for x in texts2[line_index+1:line_index+5]])
                else:
                    line="\n".join([x[4] for x in texts2[line_index+1:]])+"\n"+\
                        "\n".join([x[4] for x in doc[page_index+1].get_text("blocks",sort=True)[:5]])
                try:
                    id_n_description=from_image_text_extract_description_and_id(line)
                    if not id_n_description.startswith("["):
                        id_n_description="["+id_n_description
                    if not id_n_description.endswith("]"):
                        id_n_description+="]"
                    #print("返回值：")
                    #print(id_n_description)
                    #print("输入值：")
                    #print(line)
                    image_id,description=[x.strip() for x in eval(id_n_description)][:2]
                except (SyntaxError,ValueError) as e:
                    description=id_n_description
                    image_id=extract_id(description)
                if "\n" in description:
                    description=description.split("\n")[0]
                        
                output_image[image_id]=description

                xref = img[0] # get the XREF of the image
                pix = fitz.Pixmap(doc, xref) # create a Pixmap

                if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)

                picture_path=os.path.join(image_output_folder,image_id+".png")
                picture_path=deduplicate_insert_file(picture_path)

                try:
                    pix.save(picture_path,output="png") # save the image as png
                except RuntimeError as e:  #RuntimeError: pixmap must be grayscale or rgb to write as png
                    newpix = fitz.Pixmap(fitz.csRGB,pix)
                    newpix.save(picture_path,output="png")
                pix = None
            
            #提取表格
            if len(re.findall(r'表 \d+.\d+ ',texts))>0:
                for sentence in texts.split("\n"):
                    if re.match(r'表 \d+.\d+ ',sentence):
                        description=sentence
                        write_text_total=write_text_total.replace(description,"")
                        table_id=extract_id(description,"表")
                        output_table[table_id]={"description":description,"value":[]}
                tables=tabula.read_pdf(pdf_file_path,pages=page_index,multiple_tables=True)
                if len(tables)>0:
                    for table in tables:
                        for index, row in table.iterrows():
                            output_table[table_id]["value"].append(list(row))
                else:  #说明表格无法直接通过tabula-py提取
                    pass

            

            
            output_text_file.write(process_text(write_text_total,body_titles))

    if bio_status==4:
        output_text_file.write(process_text("\n".join(texts.split("\n")[3:-1]),body_titles,position="参考文献"))

json.dump(output_image,open(os.path.join(output_folder,filename+"_pic.json"),"w"),ensure_ascii=False)
json.dump(output_table,open(os.path.join(output_folder,filename+"_table.json"),"w"),ensure_ascii=False)

output_text_file.close()