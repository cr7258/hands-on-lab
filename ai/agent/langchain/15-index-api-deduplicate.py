# doc: https://python.langchain.com/docs/how_to/indexing/
from langchain.indexes import SQLRecordManager, index
from langchain_core.documents import Document
from langchain_elasticsearch import SparseVectorStrategy
from langchain_elasticsearch import ElasticsearchStore
from elasticsearch import Elasticsearch

index_name = "test_index"

es_connection = Elasticsearch(
    hosts="https://localhost:9200",
    basic_auth=("elastic", "test123"),
    verify_certs=False
)

vectorstore = ElasticsearchStore(
    es_connection=es_connection,
    index_name=index_name,
    vector_query_field="semantic_text",
    query_field="content",
    strategy=SparseVectorStrategy(model_id=".elser_model_2"),
)

# LangChain indexing makes use of a record manager (RecordManager) that
# keeps track of document writes into the vector store.
# This is useful for deduplication of documents.
namespace = f"elasticsearch/{index_name}"
record_manager = SQLRecordManager(
    namespace, db_url="sqlite:///record_manager_cache.sql"
)
record_manager.create_schema()

doc1 = Document(page_content="kitty is a cat", metadata={"source": "kitty.txt"})
doc2 = Document(page_content="doggy is a dog", metadata={"source": "doggy.txt"})

index_result = index(
    [doc1, doc2],
    record_manager,
    vectorstore,
    cleanup="incremental",
    source_id_key="source",
)
print(index_result)
# {'num_added': 2, 'num_updated': 0, 'num_skipped': 0, 'num_deleted': 0}

# Indexing again should result in both documents getting skipped
index_result = index(
    [doc1, doc2],
    record_manager,
    vectorstore,
    cleanup="incremental",
    source_id_key="source",
)
print(index_result)
# {'num_added': 0, 'num_updated': 0, 'num_skipped': 2, 'num_deleted': 0}

# If we mutate a document, the new version will be written and all old versions sharing the same source will be deleted.
changed_doc_2 = Document(page_content="puppy is a dog", metadata={"source": "doggy.txt"})
index_result = index(
    [changed_doc_2],
    record_manager,
    vectorstore,
    cleanup="incremental",
    source_id_key="source",
)
print(index_result)
# {'num_added': 1, 'num_updated': 0, 'num_skipped': 0, 'num_deleted': 1}

# Any documents that are not passed into the indexing function and are present in the vectorstore will be deleted!
doc3 = Document(page_content="Cathy is a cat", metadata={"source": "cathy.txt"})
index_result = index(
    [doc3],
    record_manager,
    vectorstore,
    cleanup="full",
    source_id_key="source",
)
print(index_result)
# {'num_added': 1, 'num_updated': 0, 'num_skipped': 0, 'num_deleted': 2}
