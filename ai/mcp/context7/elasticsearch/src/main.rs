use elasticsearch::{
    Elasticsearch,
    indices::IndicesCreateParts,
    SearchParts,
    IndexParts,
    http::transport::Transport,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

#[derive(Debug, Serialize, Deserialize)]
struct Document {
    id: u32,
    title: String,
    content: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Connecting to Elasticsearch...");
    println!("Note: This example requires Elasticsearch to be running on http://localhost:9200");
    println!("If Elasticsearch is not running, you will see connection errors.");

    // Create a client connected to localhost using HTTP
    let transport = Transport::single_node("http://localhost:9200")?;
    let client = Elasticsearch::new(transport);

    // Index name
    let index_name = "test_index";

    // Create an index with mapping
    println!("Creating index '{}'...", index_name);
    let _response = client
        .indices()
        .create(IndicesCreateParts::Index(index_name))
        .body(json!({
            "mappings": {
                "properties": {
                    "id": { "type": "integer" },
                    "title": { "type": "text" },
                    "content": { "type": "text" }
                }
            }
        }))
        .send()
        .await?;

    println!("Index creation successful!");

    // Create some documents
    let documents = vec![
        Document {
            id: 1,
            title: "First document".to_string(),
            content: "This is the content of the first document".to_string(),
        },
        Document {
            id: 2,
            title: "Second document".to_string(),
            content: "This is the content of the second document".to_string(),
        },
        Document {
            id: 3,
            title: "Third document".to_string(),
            content: "This is the content of the third document".to_string(),
        },
    ];

    // Index the documents
    println!("Indexing documents...");
    for doc in &documents {
        // Create document ID
        let doc_id = doc.id.to_string();

        // Index with document ID in the URL path
        let _response = client
            .index(IndexParts::IndexId(index_name, &doc_id))
            .body(doc)
            .send()
            .await?;

        println!("Document indexed with ID: {}", doc.id);
    }

    // Refresh the index to make the documents searchable immediately
    client
        .indices()
        .refresh(elasticsearch::indices::IndicesRefreshParts::Index(&[index_name]))
        .send()
        .await?;

    // Search for documents
    println!("Searching for documents...");
    let search_response = client
        .search(SearchParts::Index(&[index_name]))
        .body(json!({
            "query": {
                "match_all": {}
            }
        }))
        .send()
        .await?;

    // Process the search response
    let search_body = search_response.json::<Value>().await?;
    let hits = search_body["hits"]["hits"].as_array().unwrap();

    println!("Found {} documents:", hits.len());
    for hit in hits {
        println!("ID: {}, Source: {}",
            hit["_id"].as_str().unwrap(),
            hit["_source"]
        );
    }

    // Search for specific content
    println!("\nSearching for documents with 'first' in content...");
    let search_response = client
        .search(SearchParts::Index(&[index_name]))
        .body(json!({
            "query": {
                "match": {
                    "content": "first"
                }
            }
        }))
        .send()
        .await?;

    // Process the search response
    let search_body = search_response.json::<Value>().await?;
    let hits = search_body["hits"]["hits"].as_array().unwrap();

    println!("Found {} documents with 'first' in content:", hits.len());
    for hit in hits {
        println!("ID: {}, Source: {}",
            hit["_id"].as_str().unwrap(),
            hit["_source"]
        );
    }

    println!("Done!");
    Ok(())
}
