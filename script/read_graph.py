import xml.etree.ElementTree as ET
import os
import json
from datetime import datetime
from pymongo import MongoClient  # 需要先安装: pip install pymongo

# 定义树节点类
class TreeNode:
    def __init__(self, id, data=None):
        self.id = id
        self.data = data
        self.children = []
        self.parent = []  # 新增的父节点属性

    def add_child(self, child):
        child.parent.append(self)  # 设置子节点的父节点
        self.children.append(child)

    def __str__(self):
        return f"{{'id': '{self.id}', 'data': '{self.data}'}}"

# 解析 GraphML 文件
def parse_graphml(file_path):
    try:
        tree = ET.parse(file_path)
    except (ET.ParseError, FileNotFoundError) as e:
        print(f"Error parsing file: {e}")
        return None

    root = tree.getroot()
    nodes = {}
    
    # 创建节点
    for node in root.findall('.//{http://graphml.graphdrawing.org/xmlns}node'):
        node_id = node.get('id')
        data_element = node.find('{http://graphml.graphdrawing.org/xmlns}data')
        data = data_element.text if data_element is not None else None
        #print(f"id: {node_id}, data: {data}")
        nodes[node_id] = TreeNode(node_id, data)

    # 创建边并构建树
    for edge in root.findall('.//{http://graphml.graphdrawing.org/xmlns}edge'):
        source = edge.get('source')
        target = edge.get('target')
        if source in nodes and target in nodes:
            nodes[source].add_child(nodes[target])

    root = nodes["HIPAA"]
    #print(f"Potential roots: {root}")  # Debug print
    return root

# 打印树结构
def print_tree(node, level=0):
    if node is not None:
        print(' ' * level * 2 + f"{node.id}: {node.data}")  # 使用空格缩进表示层级
        for child in node.children:
            print_tree(child, level + 1)


Prompt_1 = """
Prompt:
Identify the key legal concepts and principles related to the provided laws.
I will provide a context, which will follow the label "Context:"
"""
Prompt_2 = """
Context: %s
"""

Prompt_3 = """
Output Struct:
{ 
	"key legal concepts": ["explanation of concept 1", "explanation of concept 2", ...], 
	"key legal principles": ["explanation of principle 1", "explanation of principle 2", ...],
	"application scenarios": ["something", "something"],
	"relationship to overall document argument": ["something", "something"]
}
"""

Prompt_4 = """
You should focus solely on explaining THIS LAW within the given context:
THIS LAW:
%s
You may now respond.
"""
Prompt_lst = [Prompt_1, Prompt_2, Prompt_3, Prompt_4]

def process_node(node):
    """处理单个节点，生成提示"""
    # 构建上下文
    context = []
    
    # 添加父节点信息
    for parent_one in node.parent:
        context.append(str(parent_one))
        
    # 添加子节点信息
    for child in node.children:
        context.append(str(child))
    
    # 构建提示字符串
    context_str = ', '.join(context) if context else "No context available"
    
    # 构建完整的提示
    prompts = [
        Prompt_1,
        Prompt_2 % context_str,
        Prompt_3,
        Prompt_4 % str(node)
    ]
    
    # 合并提示
    return '\n'.join(prompts)

def save_to_file(node_id, prompt_text):
    """将提示保存到文件"""
    # 创建输出目录
    output_dir = "prompts"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 创建文件名（使用时间戳避免重名）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/prompt_{node_id}_{timestamp}.txt"
    
    # 保存到文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(prompt_text)
    
    return filename

def save_to_mongodb(node_id, prompt_text):
    """将提示保存到MongoDB"""
    # 连接到MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['hipaa_db']
    collection = db['prompts']
    
    # 准备文档
    document = {
        'node_id': node_id,
        'prompt_text': prompt_text,
        'timestamp': datetime.now(),
        'processed': False  # 可以用来标记是否已经被处理
    }
    
    # 插入文档
    result = collection.insert_one(document)
    return result.inserted_id

# 主程序
if __name__ == "__main__":
    root_node = parse_graphml('HIPAA.graphml')
    if root_node:
        # 使用队列进行广度优先遍历
        nodes_to_process = [root_node]
        processed_nodes = set()  # 用于跟踪已处理的节点
        
        # 选择存储方式（可以同时使用两种方式）
        use_files = False 
        use_mongodb = True
        
        while nodes_to_process:
            current_node = nodes_to_process.pop(0)  # 获取当前节点
            
            # 如果节点已经处理过，跳过
            if current_node.id in processed_nodes:
                continue
                
            # 处理当前节点
            print(f"\n=== Processing Node: {current_node.id} ===")
            final_prompt = process_node(current_node)
            
            # 保存到文件
            if use_files:
                filename = save_to_file(current_node.id, final_prompt)
                print(f"Saved to file: {filename}")
            
            # 保存到MongoDB
            if use_mongodb:
                doc_id = save_to_mongodb(current_node.id, final_prompt)
                print(f"Saved to MongoDB with ID: {doc_id}")
            
            # 标记节点为已处理
            processed_nodes.add(current_node.id)
            
            # 将子节点添加到处理队列
            nodes_to_process.extend(current_node.children)
    else:
        print("Error: Could not parse graph or root node is None")