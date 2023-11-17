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


index_name = "my-audio-index"

if(es.indices.exists(index=index_name)):
    print("The index has already existed, going to remove it")
    es.options(ignore_status=404).indices.delete(index=index_name)

# Specify index configuration
mappings = {
    "_source": {
      "excludes": ["audio-embedding"]
    },
    "properties": {
      "audio-embedding": {
        "type": "dense_vector",
        "dims": 2048,
        "index": True,
        "similarity": "cosine"
      },
      "path": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "timestamp": {
        "type": "date"
      },
      "title": {
        "type": "text"
      },
      "genre": {
        "type": "text"
      }
    }
}

# Create index
if not es.indices.exists(index=index_name):
    index_creation = es.options(ignore_status=400).indices.create(index=index_name, mappings = mappings)
    print("index created: ", index_creation)
else:
    print("Index already exists.")


import os

def list_audio_files(directory):
    # The list to store the names of .wav files
    audio_files = []

    # Check if the path exists
    if os.path.exists(directory):
        # Walk the directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Check if the file is a .wav file
                if file.endswith('.wav'):
                    # Extract the filename from the path
                    filename = os.path.splitext(file)[0]
                    print(filename)

                    # Add the file to the list
                    audio_files.append(file)
    else:
        print(f"The directory '{directory}' does not exist.")

    # Return the list of .mp3 files
    return audio_files

# Use the function
audio_path = "./dataset"
audio_files = list_audio_files(audio_path)


from panns_inference import AudioTagging
# load the default model into the gpu.
model = AudioTagging(checkpoint_path=None, device='cpu')


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


from datetime import datetime

#Storing Songs in Elasticsearch with Vector Embeddings:
def store_in_elasticsearch(song, embedding, path, index_name, genre, vec_field):
  body = {
      'audio-embedding' : embedding,
      'title': song,
      'timestamp': datetime.now(),
      'path' : path,
      'genre' : genre

  }

  es.index(index=index_name, document=body)
  print ("stored...",song, embedding, path, genre, index_name)


# Initialize a list genre for test
genre_lst = ['jazz', 'opera', 'piano','prompt', 'humming', 'string', 'capella', 'eletronic', 'guitar']

for filename in audio_files:
  audio_file = audio_path + "/" + filename

  emb = get_embedding(audio_file)

  song = filename.lower()

  # Compare if genre list exists inside the song
  genre = next((g for g in genre_lst if g in song), "generic")

  store_in_elasticsearch(song, emb, audio_file, index_name, genre, 2 )

