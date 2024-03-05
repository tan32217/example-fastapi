from sqlalchemy import func
from .. import schemas
from .. import models,schemas,oauth2
from fastapi import  FastAPI, HTTPException, Response, status, Depends, APIRouter
from ..database import engine,SessionLocal,get_db
from sqlalchemy.orm import Session
from .. import utils
from sqlalchemy.orm import Session
from typing import Optional,List

router = APIRouter(
    prefix="/posts"
)
#,
@router.get("/",response_model=List[schemas.PostOut])
def get_posts(db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user),limit:int=10,skip:int=0,search:Optional[str]=""):
    # cursor.execute("""select * from posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    results = db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote,models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    print(results)
    return results

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post: schemas.PostBase,db:Session=Depends(get_db), current_user:int=Depends(oauth2.get_current_user)):
    new_post = models.Post(owners_id=current_user.id,title=post.title,content=post.content,published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}",response_model=schemas.PostOut)
def get_post(id:int, response:Response, db:Session = Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post =  db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(
        models.Vote,models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with ID:{id} not found")
    
    # if post.owners_id!= current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not Authorized to perform requested action!!")
    
    return post


@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session = Depends(get_db), current_user:int=Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with ID:{id} does not exsists")
    print(current_user.id)
    if post.owners_id!= current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not Authorized to perform requested action!!")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT )

@router.put("/{id}")
def update_posts(id:int,updated_post: schemas.PostCreate,db:Session = Depends(get_db),response_model=schemas.Post,current_user:int=Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id==id)
    post = post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with ID:{id} does not exsist")
    if post.owners_id!= current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not Authorized to perform requested action!!")
    
    post_query.update(updated_post.dict(),synchronize_session=False)

    db.commit()
    return {"data":post_query.first()}
   