from typing import Optional,List
from fastapi import  FastAPI, HTTPException, Response, status, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from . import models,schemas
from .database import engine,SessionLocal,get_db
from sqlalchemy.orm import Session
from . import utils

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(host='localhost',database='fastapi',user='postgres',password='password123',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection successful")
        break
    except Exception as error:
        print("connection to DB failed!!!!!!!!")
        print("Error: ", error)
        time.sleep(2)



my_posts= [{"title":"favourate food","content":"Pizza","id":50},{"title":"favourate drink","content":"chilly milli","id":27}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
def find_index(id):
    for i,p in enumerate(my_posts):
        if p['id'] == id:
            return i

@app.get("/")
async def root():
    return {"message": "welcome to my api----"}

@app.get("/posts",response_model=List[schemas.Post])
def get_posts(db:Session=Depends(get_db)):
    # cursor.execute("""select * from posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    print(posts)
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post: schemas.PostBase,db:Session=Depends(get_db)):
    new_post = models.Post(title=post.title,content=post.content,published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts/{id}")
def get_post(id:int, response:Response, db:Session = Depends(get_db),response_model=schemas.Post):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with ID:{id} not found")
    
    return post


@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id==id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with ID:{id} does not exsists")
    
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT )

@app.put("/posts/{id}")
def update_posts(id:int,updated_post: schemas.PostCreate,db:Session = Depends(get_db),response_model=schemas.Post):
    # cursor.execute(""" update posts set title=%s, content=%s,published=%s where id=%s returning *""",(post.title,post.content,post.published,str(id)),)
    # post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with ID:{id} does nott exsist")

    post_query.update(updated_post.dict(),synchronize_session=False)

    db.commit()
    return {"data":post_query.first()}
   

@app.post("/users",status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate,db:Session=Depends(get_db)):
    
    #password hashing
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user