from itertools import count
from sqlalchemy.orm import Session

import models, schemas


class BookRepo:
    
    async def create(db: Session, item: schemas.BookCreate):
        db_item = models.Book(name=item.name,description=item.description,count=item.count,google_books=item.google_books)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    def fetch_by_id(db: Session,_id):
        return db.query(models.Book).filter(models.Book.id == _id).first()
 
    def fetch_by_google_books(db: Session,google_books):
        return db.query(models.Book).filter(models.Book.google_books == google_books).first()
 
    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
         return db.query(models.Book).offset(skip).limit(limit).all()
 
    async def delete(db: Session,item_id):
        db_item= db.query(models.Book).filter_by(id=item_id).first()
        db.delete(db_item)
        db.commit()
     
     
    async def update(db: Session,item_data):
        updated_item = db.merge(item_data)
        db.commit()
        return updated_item