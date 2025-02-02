from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from app import schemas
from app import models
from db.db import get_db
from app.auth import get_password_hash, get_current_user
from app.scraping import scrape_hotels

bp = Blueprint('api', __name__)

@bp.route("/register/", methods=["POST"])
def create_user():
    user = schemas.UserCreate(**request.json)
    db: Session = next(get_db())
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        return jsonify({"detail": "Username already registered"}), 400
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    user_response = schemas.UserResponse.from_orm(db_user)
    return jsonify(user_response.dict())

@bp.route("/users/me", methods=["GET"])
def read_users_me():
    current_user = get_current_user()
    user_response = schemas.UserResponse.from_orm(current_user)
    return jsonify(user_response.dict())

@bp.route("/hotels/", methods=["POST"])
def search_hotels():
    data = request.get_json()
    city = data.get("city")
    min_price = data.get("min_price")
    max_price = data.get("max_price")
    star_rating = data.get("star_rating")
    db: Session = next(get_db())
    hotels = scrape_hotels(city, min_price, max_price, star_rating, db)
    hotels_dict = [hotel.dict() for hotel in hotels]
    return jsonify(hotels_dict)


@bp.route("/bookmarks/", methods=["POST"])
def create_bookmark():
    bookmark = schemas.BookmarkCreate(**request.json)
    current_user = get_current_user()
    db: Session = next(get_db())

    db_hotel = db.query(models.Hotel).filter(models.Hotel.id == bookmark.hotel_id).first()
    if not db_hotel:
        return jsonify({"detail": "Hotel not found"}), 404

    db_bookmark = models.Bookmark(user_id=current_user.id, hotel_id=bookmark.hotel_id)
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return jsonify(db_bookmark)

@bp.route("/bookmarks/", methods=["GET"])
def get_bookmarks():
    current_user = get_current_user()
    db: Session = next(get_db())
    bookmarks = db.query(models.Bookmark).filter(models.Bookmark.user_id == current_user.id).all()
    return jsonify(bookmarks)