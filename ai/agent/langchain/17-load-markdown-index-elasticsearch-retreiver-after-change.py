from langchain_text_splitters import MarkdownHeaderTextSplitter
from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchStore
from langchain_elasticsearch import SparseVectorStrategy
from langchain.indexes import SQLRecordManager, index

with open("./16-employee-handbook.md") as f:
    employee_handbook = f.read()

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on, strip_headers=False)
docs = markdown_splitter.split_text(employee_handbook)

index_name = "employee_handbook"

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

namespace = f"elasticsearch/{index_name}"
record_manager = SQLRecordManager(
    namespace, db_url="sqlite:///record_manager_cache.sql"
)
record_manager.create_schema()

# Change the orginal Core hours to 8:00 AM - 5:00 PM
index_result = index(
    docs,
    record_manager,
    vectorstore,
    cleanup="full",
)

print(index_result)
# {'num_added': 1, 'num_updated': 0, 'num_skipped': 21, 'num_deleted': 1}

results = vectorstore.similarity_search("what's the working hours according to the employee handbook?", k=1)
print(results[0])
# page_content='## 4. Attendance Policy
# ### 4.1 Working Hours
# - Core hours: **Monday to Friday, 8:00 AM – 5:00 PM**
# - Lunch break: **12:00 PM – 1:30 PM**
# - R&D and international teams may operate with flexible schedules upon approval' metadata={'Header 3': '4.1 Working Hours', 'Header 2': '4. Attendance Policy'}
