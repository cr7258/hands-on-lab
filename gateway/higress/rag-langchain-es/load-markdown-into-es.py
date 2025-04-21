from langchain_text_splitters import MarkdownHeaderTextSplitter
from elasticsearch import Elasticsearch
from langchain_elasticsearch import ElasticsearchStore
from langchain_elasticsearch import SparseVectorStrategy
from langchain.indexes import SQLRecordManager, index

# 1. Load Markdown file, split by headers
with open("./employee_handbook.md") as f:
    employee_handbook = f.read()

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on, strip_headers=False)
docs = markdown_splitter.split_text(employee_handbook)

index_name = "employee_handbook"

# 2. Use RecordManager for deduplication
namespace = f"elasticsearch/{index_name}"
record_manager = SQLRecordManager(
    namespace, db_url="sqlite:///record_manager_cache.sql"
)
record_manager.create_schema()

# 3. Index into Elasticsearch, only write to content field (raw text)
es_connection = Elasticsearch(
    hosts="https://localhost:9200",
    basic_auth=("elastic", "test123"),
    verify_certs=False
)

vectorstore = ElasticsearchStore(
    es_connection=es_connection,
    index_name=index_name,
    query_field="content",
    strategy=SparseVectorStrategy(),
)

index_result = index(
    docs,
    record_manager,
    vectorstore,
    cleanup="full",
)

print(index_result)
# {'num_added': 22, 'num_updated': 0, 'num_skipped': 0, 'num_deleted': 0}

# Querying the vector store
def custom_query(query_body: dict, query: str):
    # print(f"Original query body: {query_body}\n")

    new_query_body = {
        "_source": {
            "excludes": "semantic_text"
        },
        "retriever": {
            "rrf": {
                "retrievers": [
                    {
                        "standard": {
                            "query": {
                                "match": {
                                    "content": query
                                }
                            }
                        }
                    },
                    {
                        "standard": {
                            "query": {
                                "semantic": {
                                    "field": "semantic_text",
                                    "query": query
                                }
                            }
                        }
                    }
                ]
            }
        }
    }
    return new_query_body


results = vectorstore.similarity_search("What are the working hours in the company?", custom_query=custom_query)
print(results[0])
# page_content='## 4. Attendance Policy
# ### 4.1 Working Hours
# - Core hours: **Monday to Friday, 9:00 AM – 6:00 PM**
# - Lunch break: **12:00 PM – 1:30 PM**
# - R&D and international teams may operate with flexible schedules upon approval' metadata={'Header 3': '4.1 Working Hours', 'Header 2': '4. Attendance Policy'}


# Update employee handbook then execute the python code again
# {'num_added': 1, 'num_updated': 0, 'num_skipped': 21, 'num_deleted': 1}

# page_content='## 4. Attendance Policy
# ### 4.1 Working Hours
# - Core hours: **Monday to Friday, 8:00 AM – 5:00 PM**
# - Lunch break: **12:00 PM – 1:30 PM**
# - R&D and international teams may operate with flexible schedules upon approval' metadata={'Header 3': '4.1 Working Hours', 'Header 2': '4. Attendance Policy'}
