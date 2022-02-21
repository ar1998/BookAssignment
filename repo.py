from itertools import count
from sqlalchemy.orm import Session

import models, schemas
"""
This file contains all the Method required for interacting with the databases through ORM
"""

class BookRepo:
    
    async def create(db: Session, item: schemas.BookCreate):
        """
        creates a book entry in the database.
        """
        db_item = models.Book(name=item.name,description=item.description,count=item.count,google_books=item.google_books)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def create_through_ui(db: Session,name:str,description:str,count:int,google_books:str):
        """
        creates a book entry when accessing through UI.
        """
        db_item = models.Book(name=name,description=description,count=count,google_books=google_books)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    
    def fetch_by_id(db: Session,_id):
        """
        fetches books by internal ID
        """
        return db.query(models.Book).filter(models.Book.id == _id).first()
 
    def fetch_by_google_books(db: Session,google_books):
        """
        fetches books by google_books_id
        """
        return db.query(models.Book).filter(models.Book.google_books == google_books).first()
    
    def fetch_by_name(db: Session,name):
        """
        fetches books by name
        """
        return db.query(models.Book).filter(models.Book.name == name).first()
 
    def fetch_all(db: Session, skip: int = 0, limit: int = 100):
        """fetches all books"""
        return db.query(models.Book).offset(skip).limit(limit).all()
 
    async def delete(db: Session,item_id):
        """
        deletes books from the database
        """
        db_item= db.query(models.Book).filter_by(id=item_id).first()
        db.delete(db_item)
        db.commit()
     
     
    async def update(db: Session,item_data):
        """
        updates book in the database
        """
        updated_item = db.merge(item_data)
        db.commit()
        return updated_item
    
    def update_UI(db: Session,name:str,description:str,count:int,google_books:str):
        """
        updates book through UI
        """
        item_data = db.query(models.Book).filter(models.Book.google_books == google_books).first()
        item_data.name = name
        item_data.description = description
        item_data.count = count
        item_data.google_books = google_books
        updated_item = db.merge(item_data)
        db.commit()
        return updated_item