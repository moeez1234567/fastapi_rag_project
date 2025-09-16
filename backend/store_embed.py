from fastapi import FastAPI, UploadFile, File, Cookie, Depends
from qdrant_client import QdrantClient 
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer 
import uuid
from pydantic import BaseModel 
import io 
import PyPDF2 
import docx  
from typing import Optional   
from connections import session_local, Session, User, Chat
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn



# opening db 
# async def db_open():
#     db = session_local()
#     try:
#         yield db 
#     finally:
#         db.close()


# app
app = FastAPI()



# #
# class File_Name(BaseModel):
#     file_name : str


# allow frontend to call endpoints

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["http://localhost:3000"] for stricter rules
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# connect 
# client = QdrantClient(host="optimistic_greider", port=6333)
# client = QdrantClient(url="http://localhost:6333") # its for testing
# print("server connect successfuly")

# embedding model 
# model = SentenceTransformer("all-mpnet-base-v2")
# print("embedding model start")

# dataset = "E:/fastapi_rag/data/suleiman_magnificient.txt"  
# dataset = "E:/fastapi_rag/data/dinosaur.txt" 
# dataset = "E:/fastapi_rag/data/nagasaki.txt" 




# # open dataset  
async def text_encode(file : UploadFile):  
    content = await file.read()
    ext = file.filename.split(".")[-1].lower()  
    name = file.filename.split(".")[0].upper() 

    if ext == "txt" or ext == "csv":
        text = content.decode("utf-8") 

    elif ext == "pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(content)) 
        text = ""
        for t in reader.pages:
            text += t.extract_text() or ""

    elif ext == "docx" or ext == "doc":
        doc = docx.Document(io.BytesIO(content))
        text = ""
        for p in doc.paragraphs:
            text += p.text

    else:
        return {"message": "error to generate response ! "} 

    clean_text = text.replace("\n", " ") 
    return {"text": clean_text, "file_id" : name}

    


# create chunks
async def data_chunks(data : str, chunk_size = 200, chunk_overlap = 50):
    chunks = [] 
    start = 0 
    words = data.split()
    while (start < len(words)):
        end = start + chunk_size 
        chunk = " ".join(words[start:end]) 
        chunks.append(chunk)
        start += chunk_size - chunk_overlap 

    return chunks


# embed dataset 
# encode_model = SentenceTransformer("/app/all-mpnet-base-v2-local") 

async def encode_text(chunks):
    encode_model = SentenceTransformer("all-mpnet-base-v2") 
    encode_data = encode_model.encode(chunks).tolist()
    return encode_data


# feed dataset qdrant 
@app.post("/upload_file")
async def qdrant_f(user_id : str = Cookie(None), file : UploadFile = File(...)):
    client = QdrantClient(url="http://localhost:6333")  
    results =  await text_encode(file)
    file_id = results.get("file_id")
    if file_id is None:
        file_id = str(uuid.uuid4())
    
    chunk_text = results.get("text")
    if chunk_text is None:
        return {"message" : "There is No Text In This File Or Failted To Load Text"}
    user_id = 2
    if user_id is None:
        return {"message" : "Sign_In first for upload file"}
    exist = client.scroll(collection_name = "company_c", scroll_filter = Filter(must = [FieldCondition(key = "file", match = MatchValue(value = file_id)), FieldCondition(key = "user_id", match=MatchValue(value = user_id))])) 
    if exist[0]:
        return {"message" : "This file or file with the same name already exist"}  
    
    chunk_data = await data_chunks(chunk_text) 
    encode_data = await encode_text(chunk_data) 

    if len(chunk_data) == len(encode_data): 
        batch_size = 150 
        for i in range(0, len(chunk_data), batch_size):
            points = [PointStruct(id = str(uuid.uuid4()), vector = embed, payload={"file" : file_id, "user_id": user_id, "text" : text, "chunk_idx" : idx}) for idx, (embed, text) in enumerate(zip(encode_data[i : i+batch_size], chunk_data[i : i+batch_size]))]
            if points:
                client.upsert(collection_name="company_c", points = points) 
            else:
                return {"message" : "No Points"} 
    else:
        return {"message" : "Length of chunk data and encode data is not equal"}

    return {"filename" : file_id}



# # with open(dataset, 'r', encoding="utf-8") as f:
# #     data = f.read() 



# # create chunks of this dataset
# def create_chunks(data : str, chunk_size = 200, chunk_overlap = 50): 
#     chunks = []
#     start = 0 
#     words = data.split() 
#     while (start < len(words)):
#         end = start + chunk_size 
#         chunk = " ".join(words[start:end])
#         chunks.append(chunk)
#         start += chunk_size - chunk_overlap 


#     return chunks 


# data_chunks = create_chunks(data) 
# print("chunks created")



# # make a collection table in a qdrant of a company 
# if not client.collection_exists("company_a"):
#     client.create_collection(
#         collection_name="company_a",
#         vectors_config=VectorParams(size = 768, distance=Distance.COSINE)
#     )  



# its for creating new collection


# client = QdrantClient(url="http://localhost:6333")

# if not client.collection_exists("company_c"):
#     client.create_collection(
#         collection_name="company_c",
#         vectors_config=VectorParams(size = 768, distance=Distance.COSINE)
#     ) 

#     print("creatin new collection succefully")




# file_id = "selium_magnificient_version_1" 
# # file_id = "dinosaur_version_1" 
# # file_id = "Nagasaki_version_1"

# # make data embedding
# embeddings = model.encode(data_chunks)  
# print("embedding generated")
# # print(len(embeddings))
# # print(len(data_chunks))
# # insert this embedding in the database 



# # check if the file already exist 
# existing = client.scroll(
#     collection_name="company_b",
#     scroll_filter=Filter(must = [FieldCondition(key = "file", match = MatchValue(value=file_id))])
# )

# if existing[0]:
#     print("data in this alredy exist")

# else:  
#     if len(data_chunks) == len(embeddings):
#         batch_size = 150 
#         for i in range(0, len(data_chunks), batch_size):
#             points = [PointStruct(id = str(uuid.uuid4()), vector=embd, payload = {"file" : file_id, "company" : "company_b", "text": text, "chunk_index": idx}) for idx, (embd,text) in enumerate(zip(embeddings[i: i+batch_size], data_chunks[i:i+batch_size]))]
#             client.upsert(collection_name="company_b", points = points)     
#             print("data updert in qdrant collection succefully")


# # existing = client.scroll(
# #     collection_name="company_a",
# #     scroll_filter=Filter(must= [FieldCondition(key = "file", match = MatchValue(value=file_id))])
# # )


# # if existing[0]:
# #     print("this file is already exist")

# # else:
# #     points = [PointStruct(id = str(uuid.uuid4()), vector = embd, payload = {"file":file_id, "company": "company_a", "chunk_index":i}) for i,embd in enumerate(embeddings)]
# #     client.upsert(collection_name="company_a", points = points)


# # # company b 
# # existing_b = client.scroll(
# #     collection_name="company_b",
# #     scroll_filter=Filter(must = [FieldCondition(key = "file", match=MatchValue(value = file_id))])
# # )


# # if existing_b[0]:
# #     print("this file is already exists")

# # else:
# #     points = [PointStruct(id = str(uuid.uuid4()), vector = embd, payload = {"file":file_id, "company":"company_b", "chunk_index":i}) for i,embd in enumerate(embeddings)]
# #     client.upsert(collection_name="company_b", points = points) 

# # existing_b = client.scroll(
# #     collection_name="company_b",
# #     scroll_filter=Filter(must = [FieldCondition(key="file", match=MatchValue(value=file_id))])
# # )


# # # print("length of data chunks", len(data_chunks))
# # # print("its a length od embedding", len(embeddings))


# # if existing_b[0]:
# #     print("this file is already exists")

# # else:
# #     points = [PointStruct(id = str(uuid.uuid4()), vector = embd, payload = {"file":file_id, "company":"company_b", "chunk_index":i, "text":chunk}) for i, (embd, chunk) in enumerate(zip(embeddings, data_chunks))] 
# #     client.upsert(collection_name="company_b", points=points)


# # batch_size = 150 
# # for i in range(0, len(data_chunks), batch_size):
# #     batch_points = [PointStruct(id = str(uuid.uuid4()), vector = embd, payload = {"file": file_id, "company":"company_b", "chunk_index":idx, "text":chunk})
# #                     for idx, (embd,chunk) in enumerate(zip(embeddings[i:i+batch_size], data_chunks[i:i+batch_size]))] 
    
# #     client.upsert(collection_name="company_b", points=batch_points)


# # delete a file 
# if not client.collection_exists("company_a"):
#     client.delete(
#     collection_name="company_a",
#     points_selector=models.FilterSelector(filter = models.Filter(must = [models.FieldCondition(key = "file", match=models.MatchValue(value = file_id))]))
# )


# # delete a whole collection 
# if not client.collection_exists("company_a"):
#     client.delete_collection(collection_name="company_b")    

    



def main():
    uvicorn.run("store_embed:app", host="127.0.0.1", port = 9001, reload = True) 


if __name__ == "__main__": 
    main()








