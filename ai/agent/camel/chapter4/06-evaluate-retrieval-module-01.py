from camel.embeddings import SentenceTransformerEncoder
from camel.retrievers import VectorRetriever
from camel.storages.vectordb_storages import QdrantStorage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
import numpy as np

# 初始化嵌入模型
embedding_model = SentenceTransformerEncoder(model_name='intfloat/e5-large-v2')

# 初始化向量存储
vector_storage = QdrantStorage(
    vector_dim=embedding_model.get_output_dim(),
    collection="test_collection",
    path="test_storage",
    collection_name="CAMEL AI 文档"
)

# 初始化检索器
vr = VectorRetriever(embedding_model=embedding_model, storage=vector_storage)

# # 处理文档并构建向量数据库
# vr.process(
#     content="example_document.pdf",
# )

test_queries = [
    {
        "query": "什么是CAMEL AI？",
        "expected_answers": ["CAMEL AI 是一个开源的、社区驱动的AI框架。"]
    },
    {
        "query": "如何开始使用CAMEL AI？",
        "expected_answers": ["首先安装框架：`pip install camel-ai`，然后引入必要的模块。"]
    },
    {
        "query": "CAMEL AI 的主要特点是什么？",
        "expected_answers": ["模块化设计、易用性和扩展性。"]
    }
]

# 定义评估指标
def calculate_precision(retrieved, relevant, threshold=0.5):
    """计算精确率（Precision），当相似度超过阈值时认为是正确的"""
    correct = 0
    for r in retrieved:
        for rel in relevant:
            similarity = compute_similarity(rel, r)
            if similarity >= threshold:
                correct += 1
                break
    return correct / len(retrieved) if retrieved else 0

def calculate_recall(retrieved, relevant, threshold=0.5):
    """计算召回率（Recall），当相似度超过阈值时认为是正确的"""
    correct = 0
    for rel in relevant:
        for r in retrieved:
            similarity = compute_similarity(rel, r)
            if similarity >= threshold:
                correct += 1
                break
    return correct / len(relevant) if relevant else 0

def calculate_f1(precision, recall):
    """计算F1值"""
    return 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0

def compute_similarity(expected, retrieved):
    """计算预期答案与检索结果的相似度"""
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([expected, retrieved])
    similarity_matrix = cosine_similarity(tfidf, tfidf)
    return similarity_matrix[0, 1]

def evaluate_retrieval(query, expected_answers, threshold=0.5, top_k=1):
    """评估单个查询的检索质量"""
    results = vr.query(query=query, top_k=top_k)
    retrieved_texts = [result["text"] for result in results]
    
    # 计算精确率、召回率和F1值
    precision = calculate_precision(retrieved_texts, expected_answers, threshold)
    recall = calculate_recall(retrieved_texts, expected_answers, threshold)
    f1 = calculate_f1(precision, recall)
    
    # 计算平均相似度
    similarities = []
    for expected, retrieved in zip(expected_answers, retrieved_texts):
        similarities.append(compute_similarity(expected, retrieved))
    avg_similarity = np.mean(similarities) if similarities else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "avg_similarity": avg_similarity,
        "retrieved_texts": retrieved_texts
    }

# 执行评估
evaluation_results = []
for test_case in test_queries:
    query = test_case["query"]
    expected_answers = test_case["expected_answers"]
    
    evaluation = evaluate_retrieval(query, expected_answers)
    
    evaluation_results.append({
        "query": query,
        "expected_answers": expected_answers,
        "evaluation": evaluation
    })
    
    # 打印详细结果
    print(f"Query: {query}")
    print(f"Expected Answers: {expected_answers}")
    print(f"Retrieved Results: {evaluation['retrieved_texts']}")
    print(f"Precision: {evaluation['precision']:.4f}")
    print(f"Recall: {evaluation['recall']:.4f}")
    print(f"F1 Score: {evaluation['f1']:.4f}")
    print(f"Average Similarity: {evaluation['avg_similarity']:.4f}")
    print("-" * 100)

# 计算整体评估结果
total_precision = sum(result["evaluation"]["precision"] for result in evaluation_results) / len(evaluation_results)
total_recall = sum(result["evaluation"]["recall"] for result in evaluation_results) / len(evaluation_results)
total_f1 = sum(result["evaluation"]["f1"] for result in evaluation_results) / len(evaluation_results)
total_similarity = sum(result["evaluation"]["avg_similarity"] for result in evaluation_results) / len(evaluation_results)

print("\n整体评估结果:")
print(f"Average Precision: {total_precision:.4f}")
print(f"Average Recall: {total_recall:.4f}")
print(f"Average F1 Score: {total_f1:.4f}")
print(f"Average Similarity: {total_similarity:.4f}")

# Query: 什么是CAMEL AI？
# Expected Answers: ['CAMEL AI 是一个开源的、社区驱动的AI框架。']
# Retrieved Results: ['# CAMEL AI 介绍\n\nCAMEL AI 是一个开源的、社区驱动的 AI 框架，旨在简化 AI 应用的开发和部署。该框架提供 了多种功能模块，包括数据加载、特征工程、模型训练和部署等。\n\n## 主要特点\n\n模块化设计：用户可以根据需求选择性地加载不同的功能模块。 - 易用性：提供了简单易用的 API 接口，降低了开发门槛。 - 拓展性：支持多种模型和后端服务，方便用户根据需求进行扩展。\n\n## 常见问题\n\n1. 如何开始使用 CAMEL AI？\n\n首先安装框架：pip install camel-ai - 引入必要的模块：from camel import * - 参考官方文档：CAMEL AI 官方文档']
# Precision: 1.0000
# Recall: 1.0000
# F1 Score: 1.0000
# Average Similarity: 0.5173
# ----------------------------------------------------------------------------------------------------
# Query: 如何开始使用CAMEL AI？
# Expected Answers: ['首先安装框架：`pip install camel-ai`，然后引入必要的模块。']
# Retrieved Results: ['# CAMEL AI 介绍\n\nCAMEL AI 是一个开源的、社区驱动的 AI 框架，旨在简化 AI 应用的开发和部署。该框架提供 了多种功能模块，包括数据加载、特征工程、模型训练和部署等。\n\n## 主要特点\n\n模块化设计：用户可以根据需求选择性地加载不同的功能模块。 - 易用性：提供了简单易用的 API 接口，降低了开发门槛。 - 拓展性：支持多种模型和后端服务，方便用户根据需求进行扩展。\n\n## 常见问题\n\n1. 如何开始使用 CAMEL AI？\n\n首先安装框架：pip install camel-ai - 引入必要的模块：from camel import * - 参考官方文档：CAMEL AI 官方文档']
# Precision: 1.0000
# Recall: 1.0000
# F1 Score: 1.0000
# Average Similarity: 0.5026
# ----------------------------------------------------------------------------------------------------
# Query: CAMEL AI 的主要特点是什么？
# Expected Answers: ['模块化设计、易用性和扩展性。']
# Retrieved Results: ['# CAMEL AI 介绍\n\nCAMEL AI 是一个开源的、社区驱动的 AI 框架，旨在简化 AI 应用的开发和部署。该框架提供 了多种功能模块，包括数据加载、特征工程、模型训练和部署等。\n\n## 主要特点\n\n模块化设计：用户可以根据需求选择性地加载不同的功能模块。 - 易用性：提供了简单易用的 API 接口，降低了开发门槛。 - 拓展性：支持多种模型和后端服务，方便用户根据需求进行扩展。\n\n## 常见问题\n\n1. 如何开始使用 CAMEL AI？\n\n首先安装框架：pip install camel-ai - 引入必要的模块：from camel import * - 参考官方文档：CAMEL AI 官方文档']
# Precision: 0.0000
# Recall: 0.0000
# F1 Score: 0.0000
# Average Similarity: 0.0382
# ----------------------------------------------------------------------------------------------------

# 整体评估结果:
# Average Precision: 0.6667
# Average Recall: 0.6667
# Average F1 Score: 0.6667
# Average Similarity: 0.3527