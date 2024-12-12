import os
import re
import argparse
import csv
import pandas as pd

def count_permit_and_forbid(text):
    # 使用正则表达式匹配单词 permit 和 forbid 及其其他形式
    permit_count = len(re.findall(r'\bpermits?|permitted|permitting\b', text, re.IGNORECASE))
    forbid_count = len(re.findall(r'\bforbids?|forbidden|forbidding\b', text, re.IGNORECASE))

    return {
        'permit': permit_count,
        'forbid': forbid_count
    }

def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except Exception as e:
        print(f"无法读取文件 {file_path}，错误信息: {e}")
        return None

def process_folder(folder_path, output_csv):
    results = []
    
    # 遍历文件夹中的所有文件
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                file_path = os.path.join(root, file)
                text = read_txt_file(file_path)
                if text is not None:
                    counts = count_permit_and_forbid(text)
                    label = 'permit' if counts['permit'] >= counts['forbid'] else 'forbid'
                    results.append({
                        'index': int(''.join(filter(str.isdigit, file))),
                        'permit_count': counts['permit'],
                        'forbid_count': counts['forbid'],
                        'label': label
                    })

    # 将结果写入CSV文件
    results = pd.DataFrame(results)
    results.sort_index()
    results.to_csv(output_csv)
        

    print(f"结果已保存到 {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-folder_path", type=str, required=True, help="目标文件夹路径")
    parser.add_argument("-output_csv", type=str, required=True, help="输出的CSV文件路径")

    args = parser.parse_args()
    process_folder(args.folder_path, args.output_csv)