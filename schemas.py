from tokenize import String
from typing import Optional

from pydantic import BaseModel


class BookBase(BaseModel):
    name: str
    description: Optional[str] = None
    count: int
    google_books: str


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int

    class Config:
        orm_mode = True


# class StoreBase(BaseModel):
#     name: str

# class StoreCreate(StoreBase):
#     pass

# class Store(StoreBase):
#     id: int
#     items: List[Item] = []

#     class Config:
#         orm_mode = True

class BookSearch(BaseModel):
    google_book_id: Optional[str]
    name: str
    inInventory: bool
    count: Optional[int]

