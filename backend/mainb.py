from fastapi import FastAPI, Request, Form, Depends, Cookie, Header, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
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
from fastapi.middleware.cors import CORSMiddleware 
import jwt


#
load_dotenv()

# model token
HF_TOKEN = os.getenv("HF_TOKEN") 


# secret key of user_id
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")  
ALGORITHM = os.getenv("ALGORITHM", "HS256")



#
app = FastAPI()
encoded_model = SentenceTransformer("app/all-mpnet-base-v2-local")
# encoded_model.save("/app/all-mpnet-base-v2-local")



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://13.127.7.32",       # if HTTP
        "https://13.127.7.32",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://13.127.7.32:3000"  # add your EC2 frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# client = QdrantClient(host="optimistic_greider", port=6333)
client = QdrantClient(host =  "qdrant", port = 6333)  # its for testing


#
class LoginRequest(BaseModel):
    username: str
    email: str
    password: str


class SigninRequest(BaseModel):
    username: str
    password: str


class UserQuery(BaseModel):
    question: str
    file: str = ""


#
# class UserCreate(BaseModel):
#     username : str
#     email : str | None = None
#     password = str


# class UserLogin(BaseModel):
#     username : str
#     password : str
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


# templates = Jinja2Templates(directory="templates")

# model.config.pad_token_id = model.config.eos_token_id


# @app.get("/pass")
# async def sign_up(request:Request):
#     return templates.TemplateResponse("password.html", {"request": request})


@app.post("/submit_pass")
async def login(request: LoginRequest, db: Session = Depends(db_session)):
    db_user = db.query(User).filter(User.username == request.username).first()
    if db_user:
        return {"message": f"User with this Name already Exist{request.username}"}
    else:
        new_user = User(
            username=request.username, email=request.email, password=request.password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # response = templates.TemplateResponse("indexb.html", {"request":request, "username": new_user.username})
        # response.set_cookie(key="user_id", value = str(new_user.id))
        return {"message": "you are successfuly Sign-Up ! Know Login For Chat"}


@app.post("/login")
async def login(request: SigninRequest, db: Session = Depends(db_session)):
    db_user = (
        db.query(User)
        .filter(User.username == request.username, User.password == request.password)
        .first()
    )
    if not db_user:
        return {"message": "Invalid Password Or Username"}
    else:
        token = jwt.encode({"user_id" : db_user.id}, SECRET_KEY, algorithm = ALGORITHM) 


    return {"message" : "User Login SuccFully", "access_token" : token}
        

# session_chats = {}

# get the current user by their id
async def get_current_user(authorization : str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(statue_code = 401, detail = "Invalid auth scheme") 
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        return payload["user_id"] 
    
    except Exception: 
        return HTTPException(status_code=401, detail="invalid or expire token")




@app.post("/submit")
async def data_process(
    request: UserQuery, user_id : int = Depends(get_current_user), db: Session = Depends(db_session)
):
    encode = encoded_model.encode(request.question).tolist() 
    # user_id = 2
    if user_id is None: 
        return {"message": "please sign in"} 
    search = client.search(
        collection_name="company_c",
        query_vector=encode,
        with_payload=True,
        limit=5,
        query_filter=Filter(
            must=[
                FieldCondition(key="file", match=MatchValue(value=request.file)),
                FieldCondition(key="user_id", match=MatchValue(value=int(user_id))),
            ]
        ),
    )
    context = "\n".join([hit.payload.get("text", "") for hit in search])
    prompt = f"Answer the following question based on the context and answer just 1 time and answer is must be according to the given context:\n\n{context}\n\nQuestion : {request.question}"
    # tokens = tokenizer(prompt, return_tensors = "pt")
    # output = model.generate(**tokens, max_new_tokens = 500, do_sample = False)
    # decode = tokenizer.batch_decode(output, skip_special_tokens = True)[0]
    response = model.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )

    user_id = int(user_id)

    if not user_id:
        return {"Please Login First !"}

    question = request.question
    answer = response.choices[0].message.content

    new_chat = Chat(user_id=user_id, question=question, answer=answer)
    db.add(new_chat)
    db.commit()

    # user_name = db.query(User).filter(User.id == user_id).first()

    # # user_chat.append(db.query(Chat).filter(Chat.user_id == int(user_id)).all()) 

    # files = client.scroll(collection_name = "company_c", scroll_filter=Filter(must = FieldCondition(key = "user_id", match = MatchValue(value = int(user_id))))) 
    # file = [hit.payload.get('file') for hit in files] 
    # # if context is None:
    # #     context = "there is no much pave to hide" 
    # if file is None:
    #     return {"message" : "File is Not Present"}

    return {"question": question, "answer": answer}


#
@app.get("/user_history")
async def get_page(user_id : int = Depends(get_current_user) ,db: Session = Depends(db_session)):
    # user_id = "2"
    if user_id is None:
        return {"message": "Sign-Up Required"}
    else:
        q_a = db.query(Chat).filter(Chat.user_id == int(user_id)).all()
        user_name = db.query(User).filter(User.id == int(user_id)).first()

        qa_list = [{"question": chat.question, "answer": chat.answer} for chat in q_a]   



        user_files = [] 
        offset = None  
        

        s = set()
        # for i in range(12):
        while True:
            hits, offset = client.scroll(collection_name = "company_c", scroll_filter= Filter(must = [FieldCondition(key = "user_id", match=MatchValue(value = int(user_id)))]), offset = offset, limit = 100) 
            if not hits:
                break
            # hits, offset = results 
            user_files.extend(h.payload.get("file") for h in hits) 
            s = set(user_files)  

            if offset is None:
                break 

            
        

            if not s:
                break
    


    return {"q_a": qa_list, "user_name": user_name.username, "points" : s } 





# @app.post("/chat")
# async def chat(
#     request,
# ):

#     # Directly send user query to LLM
#     response = model.chat.completions.create(
#         model="openai/gpt-4o",
#         messages=[{"role": "user", "content": request.query}],
#         max_tokens=300,
#     )

#     question = request.query
#     answer = response.choices[0].message.content

#     return {"question": question, "answer": answer}


def main():
    uvicorn.run("mainb:app", host="0.0.0.0", port=8001, reload=True)


# ✅ This makes sure it only runs when you do `python main.py`
if __name__ == "__main__":
    main()
