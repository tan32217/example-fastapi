from typing import Optional
from fastapi import Body, FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time



app = FastAPI()

class Post(BaseModel):
    title:str
    content:str
    published:bool=True
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

@app.get("/posts")
def get_posts():
    cursor.execute("""select * from posts""")
    posts = cursor.fetchall()
    print(posts)
    return{"data":posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute(""" insert into posts (title,content,published) values (%s,%s,%s) returning *""",(post.title,post.content,post.published))
    new_post = cursor.fetchone()
    conn.commit()
    # post_dict = post.dict()
    # post_dict['id'] = randrange(0,1000000)
    # my_posts.append(post_dict)
    return{"data":new_post}

@app.get("/posts/{id}")
def get_post(id:int, response:Response):
    cursor.execute(""" select title,content,published from posts where id=(%s)""",[id])
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with ID:{id} not found")
    return {"data":post}


@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    cursor.execute(""" delete from posts where id=(%s) returning *""",(str(id)),)
    deleted_post = cursor.fetchone()
    conn.commit()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with ID:{id} does not exsists")
    return {"detail":"post deleted",
            "post":deleted_post}

@app.put("/posts/{id}")
def update_posts(id:int,post: Post):
    cursor.execute(""" update posts set title=%s, content=%s,published=%s where id=%s returning *""",(post.title,post.content,post.published,str(id)),)
    post = cursor.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with ID:{id} does nott exsist")


    return {"data":post}
    