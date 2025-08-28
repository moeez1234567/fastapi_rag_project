from fastapi import FastAPI, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse 
from fastapi.templating import Jinja2Templates 
from sentence_transformers import SentenceTransformer 
from qdrant_client import QdrantClient 
from qdrant_client.models import FieldCondition, Filter, MatchValue 
from transformers import AutoModelForCausalLM, AutoTokenizer 
import uvicorn 
from openai import OpenAI 
from pydantic import BaseModel 
from connections import session_local, Session, User, Chat 
import os 
from dotenv import load_dotenv


#
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

# 
app = FastAPI() 
encoded_model = SentenceTransformer("all-mpnet-base-v2") 
client = QdrantClient("http://localhost:6333")  


#
# class UserCreate(BaseModel):
#     username : str 
#     email : str | None = None 
#     password = str 


# class UserLogin(BaseModel):
#     username : str 
#     password : str

# gen_model = "microsoft/phi-2"
# tokenizer = AutoTokenizer.from_pretrained(gen_model)
# model = AutoModelForCausalLM.from_pretrained(gen_model)


# model = HuggingFaceEndpoint(endpoint_url=f"https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1", task="text-generation", max_new_tokens=500, temperature=0.2, huggingfacehub_api_token=token)
def db_session():
    db = session_local()
    try:
        yield db 
    finally:
        db.close() 







model = OpenAI(
      base_url="https://openrouter.ai/api/v1",
  api_key=HF_TOKEN,
)




templates = Jinja2Templates(directory="templates") 

# model.config.pad_token_id = model.config.eos_token_id

 


@app.get("/pass", response_class = HTMLResponse)
async def sign_up(request:Request):
    return templates.TemplateResponse("password.html", {"request": request}) 


@app.post("/submit_pass", response_class=HTMLResponse)
async def login(request : Request, username : str = Form(...), email : str = Form(...), password : str = Form(...), db : Session = Depends(db_session)): 
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        return templates.TemplateResponse("password.html", {"request": request, "message" : "You are already Sign-up ! Sign-In Know"})
    else: 
        new_user = User(username = username, email = email, password = password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # response = templates.TemplateResponse("indexb.html", {"request":request, "username": new_user.username}) 
        # response.set_cookie(key="user_id", value = str(new_user.id)) 
        return templates.TemplateResponse("password.html", {"request": request, "message" : "you are successfuly Sign-Up ! Know Login For Chat"})
     

 
@app.post("/login", response_class=HTMLResponse)
async def login(request : Request, username : str = Form(...), password : str = Form(...), db : Session = Depends(db_session)):
    db_user = db.query(User).filter(User.username == username, User.password == password).first()
    if not db_user:
        return templates.TemplateResponse("password.html", {"request":request, "message": "Invalid Password or user Name"})
    else: 
        redirect = RedirectResponse(url="/", status_code=303)
        redirect.set_cookie(key="user_id", value= str(db_user.id))

        return redirect
        


conversation_history = [] 
user_chat = []





@app.post("/submit", response_class=HTMLResponse)
async def data_process(request : Request, question : str = Form(...), file : str = Form(), db : Session = Depends(db_session)): 
    encode = encoded_model.encode(question).tolist() 


    search = client.search(collection_name="company_b", query_vector=encode, with_payload=True, limit = 5, query_filter = Filter(must = [FieldCondition(key = "file", match = MatchValue(value=file))])) 
    context = "\n".join([hit.payload.get("text", "") for hit in search])  
    prompt = f"Answer the following question based on the context and answer just 1 time and answer is must be according to the given context:\n\n{context}\n\nQuestion : {question}"
    # tokens = tokenizer(prompt, return_tensors = "pt")
    # output = model.generate(**tokens, max_new_tokens = 500, do_sample = False) 
    # decode = tokenizer.batch_decode(output, skip_special_tokens = True)[0] 
    response = model.chat.completions.create(model="openai/gpt-4o", messages=[{"role":"user", "content":prompt}], max_tokens = 300)  
    
    user_id = request.cookies.get("user_id")

    if not user_id:
        return templates.TemplateResponse("password.html", {"request" : request, "error": "pleases login first"})

    new_chat = Chat(user_id = int(user_id), question = question , answer = response.choices[0].message.content)
    db.add(new_chat)
    db.commit()  


    conversation_history.append(
        {"question" : question,
         "answer" : response.choices[0].message.content}
    ) 

    # user_chat.append(db.query(Chat).filter(Chat.user_id == int(user_id)).all())
    
    return RedirectResponse(url="/", status_code=303)  



#
@app.get("/", response_class=HTMLResponse)
async def get_page(request : Request, db : Session =  Depends(db_session)): 
    user_id = request.cookies.get("user_id") 
    if user_id is None:
        return templates.TemplateResponse("password.html", {"request": request, "message": "Sign-Up Required"})
    else:
        q_a = db.query(Chat).filter(Chat.user_id == int(user_id)).all()  
        user_name = db.query(User).filter(User.id == int(user_id)).first() 

    return templates.TemplateResponse("indexb.html", {"request": request, "q_a" : q_a, "conversation_history": conversation_history, "user_name" : user_name.username})  


















    







