from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi import Depends, FastAPI, Form, HTTPException, Response
from fastapi.responses import JSONResponse
from repo import BookRepo
from database import get_db, engine, get_db_sync
import models as models
import schemas as schemas
from repo import BookRepo
from sqlalchemy.orm import Session
import uvicorn
from typing import List,Optional
from fastapi.encoders import jsonable_encoder
import requests
import uvicorn
from starlette.requests import Request
import json
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from routers import books
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter(
    prefix="/api",
)

# origins = [
#     "http://localhost",
#     "http://localhost:8000"
#     "http://localhost:8080",
# ]

# router.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@router.post('/books/add',tags=["api"],status_code=201)
async def add_book(item_request: schemas.BookCreate, db: Session = Depends(get_db)):
    """
    Create a Book and store it in the database
    """
    db_item = BookRepo.fetch_by_google_books(db, google_books=item_request.google_books)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exists!")

    return await BookRepo.create(db=db, item=item_request)

@router.get("/books/all",tags=["api"],status_code=201)
async def get_all(db: Session = Depends(get_db)):
    return BookRepo.fetch_all(db)

@router.get('/books/{google_book_id}', tags=["api"])
def get_Book(google_book_id: str,db: Session = Depends(get_db)):
    """
    Get the Books with the given ID provided by User stored in database
    """
    db_item = BookRepo.fetch_by_google_books(db,google_book_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found with the given ID")
    return db_item

@router.delete('/books/{google_book_id}', tags=["api"])
async def delete_book(google_book_id: str,db: Session = Depends(get_db)):
    """
    Delete the Book with the given ID provided by User stored in database
    """
    db_item = BookRepo.fetch_by_google_books(db,google_book_id)
    db_item_id = db_item.id
    if db_item is None:
        raise HTTPException(status_code=404, detail="Book not found with the given ID")
    await BookRepo.delete(db,db_item_id)
    return "Item deleted successfully!"

@router.put('/books/{google_book_id}', tags=["api"])
async def update_book(google_book_id: str,item_request: schemas.Book, db: Session = Depends(get_db)):
    """
    Update an Book stored in the database
    """
    db_item = BookRepo.fetch_by_google_books(db, google_book_id)
    if db_item:
        update_item_encoded = jsonable_encoder(item_request)
        db_item.name = update_item_encoded['name']
        db_item.description = update_item_encoded['description']
        db_item.count = update_item_encoded['count']
        return await BookRepo.update(db=db, item_data=db_item)
    else:
        raise HTTPException(status_code=400, detail="Item not found with the given ID")
api_key = "AIzaSyBx3YE4jp9gSfel-bbkBir5m2mV4hqaLZE"
@router.get('/search/books/{bookname}',tags=["api"])
def search_book(bookname: str, db: Session = Depends(get_db)):
    print("-----")
    """
    Search for the book on the google book
    """
    url = "https://www.googleapis.com/books/v1/volumes?q={}+intitle:keyes&key={}".format(bookname,api_key)

    resp = requests.get(url)
    resp = json.loads(resp.text)
    print(resp['items'][0]['id'])
    res : list = []

    for book in resp['items']:
        print(book['id'])
        db_item = BookRepo.fetch_by_google_books(db,book['id'])
        books: dict = {}
        if db_item:
            books["id"] = db_item.google_books
            books["name"] = db_item.name
            books["inInventory"] = True
            books["count"] = db_item.count
        else :
            books["id"] = book["id"]
            books["name"] = book["volumeInfo"]["title"]
            books["inInventory"] = False
            books["count"] = 0

        res.append(books);

    return res
