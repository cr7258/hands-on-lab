from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# load documents with deterministic IDs
documents = SimpleDirectoryReader("./06-data", filename_as_id=True).load_data()

pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(),
        HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    ],
    docstore=SimpleDocumentStore(),
)

nodes = pipeline.run(documents=documents)
for node in nodes:
    print(f"Node: {node.text}")
# Docstore strategy set to upserts, but no vector store. Switching to duplicates_only strategy.
# Node: This is a test file: one
# Node: This is a test file: two

pipeline.persist("./06-pipeline_storage")
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(),
        HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    ]
)
