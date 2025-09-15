# import psycopg2  
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine  
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session




# conn = psycopg2.connect(
#     dbname = "Password",  
#     user = "postgres",
#     password = "bkkb&1234",
#     host = "localhost", 
#     port = "5432"
# )  replace 

# sqlchemy_database_url = "postgresql://postgres:bkkb1234@my-postgres2:5432/ChatsPasswords" 

sqlchemy_database_url = "postgresql://postgres:bkkb&1234@localhost:5432/Chats&Passwords" # for testing


print("connection with postgres")


#
base = declarative_base() 
engine = create_engine(sqlchemy_database_url)
# 
session_local = sessionmaker(autocommit = False, autoflush=False, bind = engine) 


class User(base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String)
    password = Column(String, nullable=False)  

    chats = relationship("Chat", back_populates="user") 



class Chat(base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  
    question = Column(String)
    answer = Column(String)

    user = relationship("User", back_populates="chats") 



# save = int(input("Enter 1 to save all tables : "))\scripts\activate



# if save == 1: 


if __name__ == "__main__":
    print("connection to postgres")
    base.metadata.create_all(bind = engine) 
    print("tables created successfully ! ")














