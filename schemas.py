from tokenize import String
from typing import Optional

from pydantic import BaseModel

"""
This Files contains the Schema for response models of the functions
"""

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


class BookSearch(BaseModel):
    google_book_id: Optional[str]
    name: str
    inInventory: bool
    count: Optional[int]

