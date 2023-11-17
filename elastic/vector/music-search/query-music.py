from elasticsearch import Elasticsearch
from config import Config

with open('simple.cfg') as f:
    cfg = Config(f)
 
print(cfg['ES_PASSWORD'])
 
es = Elasticsearch(
    'https://localhost:9200',
    verify_certs=False,
    basic_auth=('elastic', cfg['ES_PASSWORD'])
)
 
es.info()

# Define a function to query audio vector in Elasticsearch
def query_audio_vector(es, emb, field_key, index_name):
    # Initialize the query structure
    # It's a bool filter query that checks if the field exists
    query = {
        "bool": {
            "filter": [{
                "exists": {
                    "field": field_key
                }
            }]
        }
    }

    # KNN search parameters
    # field is the name of the field to perform the search on
    # k is the number of nearest neighbors to find
    # num_candidates is the number of candidates to consider (more means slower but potentially more accurate results)
    # query_vector is the vector to find nearest neighbors for
    # boost is the multiplier for scores (higher means this match is considered more important)
    knn = {
        "field": field_key,
        "k": 2,
        "num_candidates": 100,
        "query_vector": emb,
        "boost": 100
    }

    # The fields to retrieve from the matching documents
    fields = ["title", "path", "genre", "body_content", "url"]

    # The name of the index to search
    index = index_name

    # Perform the search
    # index is the name of the index to search
    # query is the query to use to find matching documents
    # knn is the parameters for KNN search
    # fields is the fields to retrieve from the matching documents
    # size is the maximum number of matches to return
    # source is whether to include the source document in the results
    resp = es.search(index=index,
                     query=query,
                     knn=knn,
                     fields=fields,
                     size=5,
                     source=False)

    # Return the search results
    return resp


from panns_inference import AudioTagging

# load the default model into the gpu.
model = AudioTagging(checkpoint_path=None, device='cpu') # change device to cpu if a gpu is not available

import numpy as np
import librosa

# Function to normalize a vector. Normalizing a vector means adjusting the values measured in different scales to a common scale.
def normalize(v):
   # np.linalg.norm computes the vector's norm (magnitude). The norm is the total length of all vectors in a space.
   norm = np.linalg.norm(v)
   if norm == 0:
        return v

   # Return the normalized vector.
   return v / norm

# Function to get an embedding of an audio file. An embedding is a reduced-dimensionality representation of the file.
def get_embedding (audio_file):

  # Load the audio file using librosa's load function, which returns an audio time series and its corresponding sample rate.
  a, _ = librosa.load(audio_file, sr=44100)

  # Reshape the audio time series to have an extra dimension, which is required by the model's inference function.
  query_audio = a[None, :]

  # Perform inference on the reshaped audio using the model. This returns an embedding of the audio.
  _, emb = model.inference(query_audio)

  # Normalize the embedding. This scales the embedding to have a length (magnitude) of 1, while maintaining its direction.
  normalized_v = normalize(emb[0])

  # Return the normalized embedding required for dot_product elastic similarity dense vector
  return normalized_v

audio_file = "./dataset/bella_ciao_humming.wav"
# Generate the embedding vector from the provided audio file
# 'get_embedding' is a function that presumably converts the audio file into a numerical vector
emb = get_embedding(audio_file)

# Query the Elasticsearch instance 'es' with the embedding vector 'emb', field key 'audio-embedding',
# and index name 'my-audio-index'
# 'query_audio_vector' is a function that performs a search in Elasticsearch using a vector embedding.
# 'tolist()' method is used to convert numpy array to python list if 'emb' is a numpy array.
print("embedding:", emb)
resp = query_audio_vector (es, emb.tolist(), "audio-embedding","my-audio-index")

NUM_MUSIC = 5  # example value

for i in range(NUM_MUSIC):
    path = resp['hits']['hits'][i]['fields']['path'][0]
    print(path)