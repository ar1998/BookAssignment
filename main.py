from ast import For
from imp import reload
from tabnanny import check
from urllib import request
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

app = FastAPI()

# adding routing for api call
app.include_router(books.router)

# mouting static directory for templates.
templates = Jinja2Templates(directory="static/html")
app.mount("/static", StaticFiles(directory="static"), name="static")

# creates all the required tables
models.Base.metadata.create_all(bind=engine)

@app.get('/add', tags=["books"])
def render_add_form(request: Request):
    """
    method for rendering new book addition form
    """
    return templates.TemplateResponse("addform.html",context = {"request": request})


@app.post('/add',tags=["books"],status_code=201)
async def add_book( request: Request,
                    bookname: str = Form(...),
                    book_desc: str = Form(...),
                    book_count: int = Form(...),
                    google_book_id: str = Form(...), db: Session = Depends(get_db)):
    """
    method to add new book (UI)
    """
    db_item = BookRepo.fetch_by_google_books(db, google_books=google_book_id)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exists!")
    resp = BookRepo.create_through_ui(db, bookname,book_desc,book_count,google_book_id)
    return templates.TemplateResponse("base.html",{"request":request})


@app.get("/",tags=["books"],status_code=201)
async def get_all_books(request: Request,db: Session = Depends(get_db)):
    """
    renders all the books available in the inventory
    """
    book_list = BookRepo.fetch_all(db)
    return templates.TemplateResponse("listAll.html",{"request":request, "books":book_list})
    

@app.get('/delete', tags=["books"])
async def delete_book(request: Request,db: Session = Depends(get_db)):
    """
    displays dropdown to select Book to Delete
    """
    books = BookRepo.fetch_all(db)
    return templates.TemplateResponse("deleteDropDown.html", {
        "request": request,
        "books": books
        })


@app.post('/delete', tags=["books"])
async def delete_book(request: Request,google_book_id:str = Form(...),db: Session = Depends(get_db)):
    """
    Deletes the selected book form the inventory
    """
    db_item = BookRepo.fetch_by_google_books(db,google_book_id)
    db_item_id = db_item.id
    if db_item is None:
        raise HTTPException(status_code=404, detail="Book not found with the given ID")
    await BookRepo.delete(db,db_item_id)
    return templates.TemplateResponse("base.html",{"request":request})


@app.get("/update",tags=["books"])
def render_selection_menu(request: Request, db: Session = Depends(get_db)):
    """
    displays dropdown to select Book to update
    """
    books = BookRepo.fetch_all(db)
    return templates.TemplateResponse("updateDropDown.html", {
        "request": request,
        "books": books
        })

@app.post('/update',tags=["books"])
def render_update_form(request: Request,book_name:str = Form(...),db: Session = Depends(get_db)):
    """
    renders the prefilled update form
    """
    item = BookRepo.fetch_by_name(db,book_name)
    book_data = {"book_name":item.name,
                 "book_desc":item.description,
                 "book_count":item.count,
                 "google_books_id":item.google_books,}
    # return book_data
    return templates.TemplateResponse("updateBookForm.html",{"request":request,"book_data":book_data})

@app.post("/update_book",tags=["books"])
def update_book(request: Request,
                book_name:str = Form(...), 
                book_desc:str = Form(...),
                book_count:int = Form(...), 
                google_book_id:str = Form(...),db : Session = Depends(get_db)):
    """
    Updates the books details in the inventory
    """
    book = BookRepo.fetch_by_google_books(db,google_book_id)
    resp = BookRepo.update_UI(db,book_name,book_desc,book_count,google_book_id)
    return templates.TemplateResponse("base.html",{"request":request})


api_key = "AIzaSyBx3YE4jp9gSfel-bbkBir5m2mV4hqaLZE"

@app.get('/search',tags=["books"])
def render_search_form(request: Request):
    """
    Renders the search field
    """
    return templates.TemplateResponse("searchform.html",context = {"request": request})

@app.post('/search',tags=["books"])
def search_book(request: Request,db: Session = Depends(get_db),
                bookname:str = Form(...)):
    """
    Search for the book on the google book in the inventory
    """
    # api URL to hit.
    url = "https://www.googleapis.com/books/v1/volumes?q={}+intitle:keyes&key={}".format(bookname,api_key)
    resp = requests.get(url)
    resp = json.loads(resp.text)
    print(resp['items'][0]['id'])
    res : list = []

    # iterate through each book in result and check
    # if present in inventory
    for book in resp['items']:
        print(book['id'])
        db_item = BookRepo.fetch_by_google_books(db,book['id'])
        books: dict = {}

        # if book is present in the inventory display as in stock
        if db_item:
            books["id"] = db_item.google_books
            books["name"] = db_item.name
            books["inInventory"] = True
            books['link'] = book['accessInfo']['webReaderLink']
            books['thumbnail'] = book['volumeInfo']['imageLinks']['thumbnail']
            books["count"] = db_item.count

        # else display as out of stock
        else :
            books["id"] = book["id"]
            books["name"] = book["volumeInfo"]["title"]
            books["inInventory"] = False
            books['link'] = book['accessInfo']['webReaderLink']
            books['thumbnail'] = book['volumeInfo']['imageLinks']['thumbnail']
            books["count"] = 0

        res.append(books);

    return templates.TemplateResponse("searchresult.html",context={"request": request,"res":res})

    
# uncomment this block when running as a container locally.    
# if __name__ == "__main__":
#     uvicorn.run('main:app', host="0.0.0.0", port=8000)
