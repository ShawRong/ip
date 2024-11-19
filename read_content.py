# read_json.py

import json
import os

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def clean_content(content):
    # 清理空白符
    return content.replace('\n', ' ').replace('\t', ' ')

def create_paragraph(sentences):
    # 将句子列表连接成一个段落
    paragraph = ' '.join(sentences)
    return paragraph

def process_filename(filename):
    # 去除前面的'prompt_'和后面的'_202410...'部分
    if filename.startswith("prompt_"):
        filename = filename[7:]  # 去掉'prompt_'
    
    # 找到最后一个'_'的位置
    last_underscore_index = filename.rfind('_')
    if last_underscore_index != -1:
        second_last_index = filename.rfind('_', 0, last_underscore_index)
        filename = filename[:second_last_index]  # 去掉'_202410...'及其后面的部分
    
    return filename

document_name = 'document_19_2'
def write_to_file(filename, content):
    # 将内容写入文件，确保在'document'子文件夹中
    os.makedirs(document_name, exist_ok=True)  # 创建'document'文件夹（如果不存在）
    file_path = os.path.join(document_name, filename)  # 生成完整的文件路径
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def main():
    file_path = './response_content_19_2.json'  # 更新为您的文件路径
    json_data = load_json(file_path)

    # 打印解析后的数据
    for index, item in enumerate(json_data):
        print(f"Item {index + 1}:")
        try:
            content = parse_json_string(item['content'])
        except json.JSONDecodeError:
            # 如果parse_json_string出现错误，使用parse_json_string_handle_str处理
            content = parse_json_string_handle_str(item['content'])
        
        # 准备输出内容
        output_content = (
            f"# Law\n"
            f"{process_filename(item['prompt_file'])}\n"
            f"# Key Legal Concepts\n"
            f"{create_paragraph(content['key legal concepts'])}\n"
            f"# Key Legal Principles\n"
            f"{create_paragraph(content['key legal principles'])}\n"
            f"# Application Scenarios\n"
            f"{create_paragraph(content['application scenarios'])}\n"
            f"# Relationship to Overall Document Argument\n"
            f"{create_paragraph(content['relationship to overall document argument'])}\n"
        )

        # 使用item['prompt_file']作为文件名
        output_filename = process_filename(item['prompt_file']) + '.txt'
        write_to_file(output_filename, output_content)

def parse_json_string(json_string):
    # 将字符串转换为合法的JSON对象
    json_string = json_string.replace('\n', '').replace('\t', '')  # 清理空白符
    return json.loads(json_string)

def parse_json_string_handle_str(json_string):
    # 去除前后的```json```标记
    if json_string.startswith("```json"):
        json_string = json_string[7:].strip()  # 去掉开头的```json
    if json_string.endswith("```"):
        json_string = json_string[:-3].strip()  # 去掉结尾的```
    
    # 清理空白符
    json_string = json_string.replace('\n', '').replace('\t', '')  
    return json.loads(json_string)

if __name__ == "__main__":
    main()