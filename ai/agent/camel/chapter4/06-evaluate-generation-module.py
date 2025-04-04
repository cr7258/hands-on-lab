### 🔍 检索模块 vs 🧠 生成模块

# | 模块 | 主要作用 | 输入 | 输出 | 评估方式 |
# |------|----------|------|------|-----------|
# | **检索模块** | 从知识库/文档库中找出相关内容 | 查询（query） | 若干相关文档或段落 | 精确率、召回率、Top-K 命中率（e.g. Recall@5） |
# | **生成模块** | 根据查询+上下文生成回答 | 查询 + 检索到的文档 | 一个自然语言回答 | BLEU、ROUGE、人工评估（流畅性、相关性） |

from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize

# 示例数据
reference = "RAG combines retrieval and generation for QA."
generated = "RAG integrates retrieval and generation for question answering."

# 使用ROUGE评估
scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
scores = scorer.score(reference, generated)

# 使用BLEU评估
reference_tokens = word_tokenize(reference)
generated_tokens = word_tokenize(generated)
bleu_score = sentence_bleu([reference_tokens], generated_tokens)

print(f"ROUGE-1: {scores['rouge1'].fmeasure:.2f}")
print(f"ROUGE-L: {scores['rougeL'].fmeasure:.2f}")
print(f"BLEU Score: {bleu_score:.2f}")

# ROUGE-1: 0.67
# ROUGE-L: 0.67
# BLEU Score: 0.33