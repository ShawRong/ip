import os
import math
from collections import Counter
from six import iteritems
import nltk
from nltk.corpus import stopwords
import string

# 确保下载停用词
nltk.download('stopwords')

# BM25算法的参数
PARAM_K1 = 1.5  # 控制词频的影响
PARAM_B = 0.75  # 控制文档长度的影响
EPSILON = 0.25  # 用于处理负IDF的特殊值

class BM25:
    def __init__(self, documents):
        """
        初始化BM25类。

        Parameters
        ----------
        documents : list of list of str
            语料库，每个文档是一个单词列表。
        """
        self.documents = documents  # 存储文档
        self.doc_count = len(documents)  # 文档数量
        self.avg_doc_len = sum(len(doc) for doc in documents) / self.doc_count  # 平均文档长度
        self.k1 = PARAM_K1  # BM25参数k1
        self.b = PARAM_B  # BM25参数b
        self.doc_freqs = [Counter(doc) for doc in documents]  # 计算每个文档的词频

    def idf(self, term):
        """
        计算逆文档频率（IDF）。

        Parameters
        ----------
        term : str
            要计算IDF的词。

        Returns
        -------
        float
            该词的IDF值。
        """
        doc_freq = sum(1 for doc in self.documents if term in doc)  # 计算包含该词的文档数量
        return math.log((self.doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1)  # 计算IDF

    def score(self, document, term):
        """
        计算给定文档中某个词的BM25分数。

        Parameters
        ----------
        document : list of str
            要评分的文档。
        term : str
            要计算分数的词。

        Returns
        -------
        float
            该词在文档中的BM25分数。
        """
        term_freq = document.count(term)  # 计算词频
        doc_len = len(document)  # 文档长度
        return (self.idf(term) * (term_freq * (self.k1 + 1)) /
                (term_freq + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))))  # BM25分数计算公式

    def retrieve(self, keyword):
        """
        根据关键词检索文档。

        Parameters
        ----------
        keyword : str
            要检索的关键词。

        Returns
        -------
        list of tuple
            包含文档索引和对应分数的元组列表，按分数降序排列。
        """
        scores = [(i, self.score(doc, keyword)) for i, doc in enumerate(self.documents)]  # 计算每个文档的分数
        return sorted(scores, key=lambda x: x[1], reverse=True)  # 按分数降序排序

    def get_score(self, document, index):
        """
        计算给定文档相对于语料库中某个文档的BM25分数。

        Parameters
        ----------
        document : list of str
            要评分的文档。
        index : int
            语料库中要比较的文档索引。

        Returns
        -------
        float
            BM25分数。
        """
        score = 0
        doc_freqs = self.doc_freqs[index]  # 获取指定文档的词频
        for word in document:
            if word not in doc_freqs:  # 如果词不在文档中，跳过
                continue
            score += (self.idf(word) * doc_freqs[word] * (PARAM_K1 + 1)
                      / (doc_freqs[word] + PARAM_K1 * (1 - PARAM_B + PARAM_B * len(self.documents[index]) / self.avg_doc_len)))  # BM25分数计算
        return score

    def get_scores(self, document):
        """
        计算给定文档相对于语料库中所有文档的BM25分数。

        Parameters
        ----------
        document : list of str
            要评分的文档。

        Returns
        -------
        list of tuple
            包含分数和文档索引的元组列表。
        """
        scores = [(self.get_score(document, index), index) for index in range(self.doc_count)]  # 计算所有文档的分数
        return scores

    def get_words_score(self, document, index):
        """
        计算给定文档中每个词的BM25分数。

        Parameters
        ----------
        document : list of str
            要评分的文档。
        index : int
            语料库中要比较的文档索引。

        Returns
        -------
        list of tuple
            包含词和对应分数的元组列表，按分数降序排列。
        """
        words_score = {}
        doc_freqs = self.doc_freqs[index]  # 获取指定文档的词频
        for word in document:
            if word not in doc_freqs:  # 如果词不在文档中，跳过
                continue
            score = (self.idf(word) * doc_freqs[word] * (PARAM_K1 + 1)
                      / (doc_freqs[word] + PARAM_K1 * (1 - PARAM_B + PARAM_B * len(self.documents[index]) / self.avg_doc_len)))  # BM25分数计算
            words_score[word] = max(words_score.get(word, 0), score)  # 记录最高分数
        
        word_score_tuples = sorted(words_score.items(), key=lambda x: x[1], reverse=True)  # 按分数降序排序
        return word_score_tuples

    def get_top_n_documents(self, document, n=5):
        """
        获取与给定文档最相关的前N个文档。

        Parameters
        ----------
        document : list of str
            要评分的文档。
        n : int
            要返回的文档数量。

        Returns
        -------
        list of tuple
            包含分数和文档索引的元组列表，按分数降序排列。
        """
        scores = self.get_scores(document)  # 计算所有文档的分数
        top_n = sorted(scores, key=lambda x: x[0], reverse=True)[:n]  # 获取前N个文档
        return top_n

def load_documents(directory):
    """
    从指定目录加载文档并进行预处理。

    Parameters
    ----------
    directory : str
        文档所在目录。

    Returns
    -------
    list of list of str
        处理后的文档，每个文档是一个单词列表。
    """
    documents = []
    stop_words = set(stopwords.words('english'))  # 获取英语停用词
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):  # 只处理文本文件
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                # 读取文件内容
                text = file.read()
                # 文本处理
                text = text.lower()  # 转换为小写
                text = text.translate(str.maketrans('', '', string.punctuation))  # 去除标点符号
                words = text.split()  # 分词
                # 去除停用词
                filtered_words = [word for word in words if word not in stop_words]
                documents.append(filtered_words)  # 将处理后的单词列表添加到文档中
    return documents

if __name__ == "__main__":
    directory = './document'  # 更新为您的文档目录
    corpus = load_documents(directory)  # 加载并处理文档
    
    bm25 = BM25(corpus)  # 创建BM25实例
    document = ["genetic", "genetic"]  # 要评分的文档
    scores = bm25.get_scores(document)  # 计算分数
    print("BM25 Scores:", scores)  # 打印分数
    
    top_documents = bm25.get_top_n_documents(document, n=2)  # 获取前2个相关文档
    print("Top Documents:", top_documents)  # 打印相关文档
    print(corpus[top_documents[0][1]])