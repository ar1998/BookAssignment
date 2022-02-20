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
app.include_router(books.router)
templates = Jinja2Templates(directory="static/html")
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost",
    "http://localhost:8000"
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# method for rendering new book addition form
@app.get('/add', tags=["books"])
def render_add_form(request: Request):
    return templates.TemplateResponse("addform.html",context = {"request": request})

# method to add new book (UI)
@app.post('/add',tags=["books"],status_code=201)
async def add_book( request: Request,
                    bookname: str = Form(...),
                    book_desc: str = Form(...),
                    book_count: int = Form(...),
                    google_book_id: str = Form(...), db: Session = Depends(get_db)):
    """
    Create a Book and store it in the database
    """
    db_item = BookRepo.fetch_by_google_books(db, google_books=google_book_id)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exists!")

    resp = BookRepo.create_through_ui(db, bookname,book_desc,book_count,google_book_id)
    return templates.TemplateResponse("base.html",{"request":request})

@app.get("/",tags=["books"],status_code=201)
async def get_all_books(request: Request,db: Session = Depends(get_db)):
    book_list = BookRepo.fetch_all(db)
    return templates.TemplateResponse("listAll.html",{"request":request, "books":book_list})
    


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

@app.get("/update")
def render_selection_menu(request: Request, db: Session = Depends(get_db)):
    """
    displays dropdown to select Book to update
    """
    books = BookRepo.fetch_all(db)
    return templates.TemplateResponse("updateDropDown.html", {
        "request": request,
        "books": books
        })

@app.post('/update')
def render_update_form(request: Request,book_name:str = Form(...),db: Session = Depends(get_db)):
    item = BookRepo.fetch_by_name(db,book_name)
    book_data = {"book_name":item.name,
                 "book_desc":item.description,
                 "book_count":item.count,
                 "google_books_id":item.google_books,}
    # return book_data
    return templates.TemplateResponse("updateBookForm.html",{"request":request,"book_data":book_data})

@app.post("/update_book")
def update_book(request: Request,book_name:str = Form(...), book_desc:str = Form(...),book_count:int = Form(...), google_book_id:str = Form(...),db : Session = Depends(get_db)):
    book = BookRepo.fetch_by_google_books(db,google_book_id)
    return BookRepo.update_UI(db,book_name,book_desc,book_count,google_book_id)


api_key = "AIzaSyBx3YE4jp9gSfel-bbkBir5m2mV4hqaLZE"

@app.get('/search',tags=["books"])
def render_search_form(request: Request):
    return templates.TemplateResponse("searchform.html",context = {"request": request})

@app.post('/search')
def search_book(request: Request,db: Session = Depends(get_db),
                bookname:str = Form(...)):
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
            books['link'] = book['accessInfo']['webReaderLink']
            books['thumbnail'] = book['volumeInfo']['imageLinks']['thumbnail']
            books["count"] = db_item.count
        else :
            books["id"] = book["id"]
            books["name"] = book["volumeInfo"]["title"]
            books["inInventory"] = False
            books['link'] = book['accessInfo']['webReaderLink']
            books['thumbnail'] = book['volumeInfo']['imageLinks']['thumbnail']
            books["count"] = 0

        res.append(books);

    return templates.TemplateResponse("searchresult.html",context={"request": request,"res":res})

    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
