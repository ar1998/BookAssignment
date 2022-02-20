from queue import Empty
from sqlalchemy import Column, Integer, String, column, null
from sqlalchemy.orm import relationship

from database import Base
    
class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String(80), nullable=False, unique=True,index=True)
    description = Column(String(200))
    google_books = Column(String(20),nullable=False)
    count = Column(Integer)
    def __repr__(self):
        return 'ItemModel(name=%s, description=%s,google_books=%s)' % (self.name, self.description,self.google_books)
    
# class Store(Base):
#     __tablename__ = "stores"
#     id = Column(Integer, primary_key=True,index=True)
#     name = Column(String(80), nullable=False, unique=True)
#     items = relationship("Item",primaryjoin="Store.id == Item.store_id",cascade="all, delete-orphan")

#     def __repr__(self):
#         return 'Store(name=%s)' % self.name