from pydantic import BaseModel
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class HotelBase(BaseModel):
    name: str
    image_url: str
    star_rating: float
    city: str
    booking_url: str

class HotelCreate(HotelBase):
     pass


class PriceBase(BaseModel):
    source: str
    price: float

class PriceCreate(PriceBase):
    hotel_id: int


class HotelResponse(HotelBase):
    id: int
    prices: list[PriceBase]

class UserResponse(BaseModel):
   id: int
   username: str
   email: str

   class Config:
       orm_mode = True
       from_attributes = True

class BookmarkCreate(BaseModel):
    hotel_id: int

class BookmarkResponse(BaseModel):
    id: int
    user_id: int
    hotel_id: int