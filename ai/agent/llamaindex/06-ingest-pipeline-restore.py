from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader

# 执行代码前先写入一条新文档，更新一条已存在的文档
# echo "This is a test file: three" > 06-data/test3.txt
# echo "This is a NEW test file: one" > 06-data/test1.txt

pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(),
        HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    ]
)
documents = SimpleDirectoryReader("./06-data", filename_as_id=True).load_data()

# restore the pipeline
pipeline.load("./06-pipeline_storage")

nodes = pipeline.run(documents=documents)
# 只会影响更新的文档，test2.txt 不受影响
# Docstore strategy set to upserts, but no vector store. Switching to duplicates_only strategy.
# Node: This is a NEW test file: one
# Node: This is a test file: three

for node in nodes:
    print(f"Node: {node.text}")

print(len(pipeline.docstore.docs))
# 3