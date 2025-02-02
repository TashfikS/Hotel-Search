from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import MetaData

Base = declarative_base(metadata=MetaData())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    bookmarks = relationship("Bookmark", back_populates="user")


class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    image_url = Column(String)
    star_rating = Column(Integer)
    city = Column(String, index=True)
    booking_url = Column(String)
    prices = relationship("Price", back_populates="hotel")
    bookmarks = relationship("Bookmark", back_populates="hotel")


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    source = Column(String)
    price = Column(Float)
    hotel = relationship("Hotel", back_populates="prices")


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="bookmarks")
    hotel = relationship("Hotel", back_populates="bookmarks")