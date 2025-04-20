import json, os
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from llama_index.vector_stores.elasticsearch import ElasticsearchStore
from llama_index.core import Document
from elasticsearch import Elasticsearch


def get_documents_from_file(file):
    """Reads a json file and returns list of Documents"""

    with open(file=file, mode='rt') as f:
        conversations_dict = json.loads(f.read())

    # Build Document objects using fields of interest.
    documents = [Document(text=item['conversation'],
                          metadata={"conversation_id": item['conversation_id']})
                 for
                 item in conversations_dict]
    return documents


# ElasticsearchStore is a VectorStore that
# takes care of ES Index and Data management.
# connection_params = {"verify_certs": False}
# es_vector_store = ElasticsearchStore(
#     index_name="calls",
#     es_url="https://localhost:9200",
#     es_user="elastic",
#     es_password="test123",
#     vector_field='conversation_vector',
#     text_field='conversation',
#     **connection_params,
# )

es_client = Elasticsearch(
    hosts="https://localhost:9200",
    basic_auth=("elastic", "test123"),
    verify_certs=False
)
es_vector_store = ElasticsearchStore(
    index_name="calls",
    es_client=es_client,
    text_field='conversation',
)

def main():
    # LlamaIndex Pipeline configured to take care of chunking, embedding
    # and storing the embeddings in the vector store.
    pipeline = IngestionPipeline(
        vector_store=es_vector_store
    )

    # Load data from a json file into a list of LlamaIndex Documents
    documents = get_documents_from_file(file="conversations.json")

    pipeline.run(documents=documents)
    print(".....Done running pipeline.....\n")


if __name__ == "__main__":
    main()
