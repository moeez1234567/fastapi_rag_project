# from qdrant_client import QdrantClient 
# from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
# from fastapi import FastAPI, Body, Request, Form 
# from sentence_transformers import SentenceTransformer 
# # from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline  
# # from huggingface_hub import InferenceClient 
# import uvicorn 
# from fastapi.templating import Jinja2Templates  
# from fastapi.responses import HTMLResponse, JSONResponse 



# from openai import OpenAI 
# from dotenv import load_dotenv 
# import os


# load_dotenv()


# HF_TOKEN = os.getenv("HF_TOKEN")



# #
# templates = Jinja2Templates(directory="templates")



# # # inference = InferenceClient(model=model_name) 
# # generation = pipeline("text-generation", model = model_name)
# model = OpenAI(
#       base_url="https://openrouter.ai/api/v1",
#   api_key=HF_TOKEN,
# )



# # tokenizer = AutoTokenizer.from_pretrained(model_name)
# # model = AutoModelForCausalLM.from_pretrained(model_name) 

# # 
# app = FastAPI() 
# client = QdrantClient("http://localhost:6333")
# embedding_model = SentenceTransformer("all-MiniLM-L6-v2") 


# @app.get("/", response_class=HTMLResponse)
# async def chat(request : Request): 
#     return templates.TemplateResponse("index.html", {"request": request})  


# @app.post("/submit", response_class=HTMLResponse)
# async def chat(request : Request, question : str = Form(...), file : str = Form(...)):  
#     query_encode = embedding_model.encode(question).tolist()
#     result_vectors = client.search(collection_name="company_a", query_vector=query_encode, limit=1, with_payload=True, query_filter=Filter(must = [FieldCondition(key = "file", match = MatchValue(value=file))]))

#     context = "\n".join([hit.payload.get("text","") for hit in result_vectors])  
#     prompt = f"Answer the following question based on the contex and answer just 1 time and answer is must be according to the given context:\n\n{context}\n\nQuestion : {question}"  

#     response = model.chat.completions.create(model="openai/gpt-4o", messages=[{"role":"user", "content":prompt}], max_tokens = 300)

#     return templates.TemplateResponse("index.html", {"request":request, "answer":response.choices[0].message.content}) 















