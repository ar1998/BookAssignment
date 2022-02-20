from tabnanny import check
from urllib import request
from fastapi import Depends, FastAPI, HTTPException
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
import json

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# @app.post('/books/add', tags=["Book"],response_model=schemas.Book,status_code=201)
# async def create_item(item_request: schemas.BookCreate, db: Session = Depends(get_db)):
#     """
#     Create a Book and store it in the database
#     """
#     db_item = BookRepo.fetch_by_google_books(db, google_books=item_request.google_books)
#     if db_item:
#         raise HTTPException(status_code=400, detail="Item already exists!")

#     return await BookRepo.create(db=db, item=item_request)

# @app.get('/books', tags=["Book"],response_model=List[schemas.Book])
# def get_all_items(google_books: Optional[str] = None,db: Session = Depends(get_db)):
#     """
#     Get all the Books stored in database
#     """
#     if google_books:
#         items =[]
#         db_item = BookRepo.fetch_by_google_books(db,google_books)
#         items.append(db_item)
#         return items
#     else:
#         return BookRepo.fetch_all(db)

# @app.post("/books", tags=["Book"], response_model=schemas.Book, status_code=201)
# async def add_book(item_request: schemas.BookCreate, db: Session = Depends(get_db)):
#     return await BookRepo.create(db, item_request)

# @app.get("/books", tags=["Book"], response_model=List[schemas.Book], status_code=200)
# async def get_all_books(db: Session = Depends(get_db)):
#     return BookRepo.fetch_all(db)

@app.post('/books/add',tags=["books"],status_code=201)
async def add_book(item_request: schemas.BookCreate, db: Session = Depends(get_db)):
    """
    Create a Book and store it in the database
    """
    db_item = BookRepo.fetch_by_google_books(db, google_books=item_request.google_books)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exists!")

    return await BookRepo.create(db=db, item=item_request)

@app.get("/books/all",tags=["books"],status_code=201)
async def get_all(db: Session = Depends(get_db)):
    return BookRepo.fetch_all(db)

@app.get('/books/{google_book_id}', tags=["Book"])
def get_Book(google_book_id: str,db: Session = Depends(get_db)):
    """
    Get the Books with the given ID provided by User stored in database
    """
    db_item = BookRepo.fetch_by_google_books(db,google_book_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found with the given ID")
    return db_item

@app.delete('/books/{google_book_id}', tags=["Book"])
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

@app.put('/books/{google_book_id}', tags=["Book"])
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

# async def check_in_inventory(google_book_id : str,db: Session = Depends(get_db_sync)):
#     """
#     check for the givrn book in inventory
#     """
#     db_item = BookRepo.fetch_by_google_books(db,google_book_id)
#     if db_item:
#         return True
#     return False


api_key = "AIzaSyBx3YE4jp9gSfel-bbkBir5m2mV4hqaLZE"
@app.get('/books/search/{name}')
def search_book(name: str,db: Session = Depends(get_db)):
    print("-----")
    """
    Search for the book on the google book
    """
    url = "https://www.googleapis.com/books/v1/volumes?q={}+intitle:keyes&key={}".format(name,api_key)

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
            # books["count"] = str(db_item.count)
        else :
            books["id"] = book["id"]
            books["name"] = book["volumeInfo"]["title"]
            books["inInventory"] = False
            # books["count"] = 0

        res.append(books);

    return res

    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
