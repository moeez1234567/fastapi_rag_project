from qdrant_client import QdrantClient 
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer 
import uuid


# connect 
client = QdrantClient(host="localhost", port=6333)
print("server connect successfuly")

# embedding model 
model = SentenceTransformer("all-mpnet-base-v2")
print("embedding model start")

# dataset = "E:/fastapi_rag/suleiman_magnificient.txt"  
# dataset = "E:/fastapi_rag/dinosaur.txt" 
dataset = "E:/fastapi_rag/nagasaki.txt"

# open dataset 
with open(dataset, 'r', encoding="utf-8") as f:
    data = f.read() 



# create chunks of this dataset
def create_chunks(data : str, chunk_size = 200, chunk_overlap = 50): 
    chunks = []
    start = 0 
    words = data.split() 
    while (start < len(words)):
        end = start + chunk_size 
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - chunk_overlap 


    return chunks 


data_chunks = create_chunks(data) 
print("chunks created")



# make a collection table in a qdrant of a company 
if not client.collection_exists("company_a"):
    client.create_collection(
        collection_name="company_a",
        vectors_config=VectorParams(size = 384, distance=Distance.COSINE)
    )  


if not client.collection_exists("company_b"):
    client.create_collection(
        collection_name="company_b",
        vectors_config=VectorParams(size = 768, distance=Distance.COSINE)
    )




# file_id = "selium_magnificient_version_1" 
# file_id = "dinosaur_version_1" 
file_id = "Nagasaki_version_1"

# make data embedding
embeddings = model.encode(data_chunks)  
print("embedding generated")
# print(len(embeddings))
# print(len(data_chunks))
# insert this embedding in the database 



# check if the file already exist 
existing = client.scroll(
    collection_name="company_b",
    scroll_filter=Filter(must = [FieldCondition(key = "file", match = MatchValue(value=file_id))])
)

if existing[0]:
    print("data in this alredy exist")

else:  
    if len(data_chunks) == len(embeddings):
        batch_size = 150 
        for i in range(0, len(data_chunks), batch_size):
            points = [PointStruct(id = str(uuid.uuid4()), vector=embd, payload = {"file" : file_id, "company" : "company_b", "text": text, "chunk_index": idx}) for idx, (embd,text) in enumerate(zip(embeddings[i: i+batch_size], data_chunks[i:i+batch_size]))]
            client.upsert(collection_name="company_b", points = points)     
            print("data updert in qdrant collection succefully")


# existing = client.scroll(
#     collection_name="company_a",
#     scroll_filter=Filter(must= [FieldCondition(key = "file", match = MatchValue(value=file_id))])
# )


# if existing[0]:
#     print("this file is already exist")

# else:
#     points = [PointStruct(id = str(uuid.uuid4()), vector = embd, payload = {"file":file_id, "company": "company_a", "chunk_index":i}) for i,embd in enumerate(embeddings)]
#     client.upsert(collection_name="company_a", points = points)


# # company b 
# existing_b = client.scroll(
#     collection_name="company_b",
#     scroll_filter=Filter(must = [FieldCondition(key = "file", match=MatchValue(value = file_id))])
# )


# if existing_b[0]:
#     print("this file is already exists")

# else:
#     points = [PointStruct(id = str(uuid.uuid4()), vector = embd, payload = {"file":file_id, "company":"company_b", "chunk_index":i}) for i,embd in enumerate(embeddings)]
#     client.upsert(collection_name="company_b", points = points) 

# existing_b = client.scroll(
#     collection_name="company_b",
#     scroll_filter=Filter(must = [FieldCondition(key="file", match=MatchValue(value=file_id))])
# )


# # print("length of data chunks", len(data_chunks))
# # print("its a length od embedding", len(embeddings))


# if existing_b[0]:
#     print("this file is already exists")

# else:
#     points = [PointStruct(id = str(uuid.uuid4()), vector = embd, payload = {"file":file_id, "company":"company_b", "chunk_index":i, "text":chunk}) for i, (embd, chunk) in enumerate(zip(embeddings, data_chunks))] 
#     client.upsert(collection_name="company_b", points=points)


# batch_size = 150 
# for i in range(0, len(data_chunks), batch_size):
#     batch_points = [PointStruct(id = str(uuid.uuid4()), vector = embd, payload = {"file": file_id, "company":"company_b", "chunk_index":idx, "text":chunk})
#                     for idx, (embd,chunk) in enumerate(zip(embeddings[i:i+batch_size], data_chunks[i:i+batch_size]))] 
    
#     client.upsert(collection_name="company_b", points=batch_points)


# delete a file 
if not client.collection_exists("company_b"):
    client.delete(
    collection_name="company_b",
    points_selector=models.FilterSelector(filter = models.Filter(must = [models.FieldCondition(key = "file", match=models.MatchValue(value = file_id))]))
)


# delete a whole collection 
if not client.collection_exists("company_b"):
    client.delete_collection(collection_name="company_b")    

    











