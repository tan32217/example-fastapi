from .. import schemas
from .. import models,schemas
from fastapi import  FastAPI, HTTPException, Response, status, Depends, APIRouter
from ..database import engine,SessionLocal,get_db
from sqlalchemy.orm import Session
from .. import utils
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users"
)

@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate,db:Session=Depends(get_db)):
    
    #password hashing
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}",response_model=schemas.UserOut)
def get_user(id:int, db:Session=Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"USer with ID:{id} not found")
    
    return user