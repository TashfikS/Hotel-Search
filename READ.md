# Hotel Search and Bookmark Application

This project is a web application that allows users to search for hotels, view hotel details, and bookmark their favorite hotels. The application is built using Flask for the backend and vanilla JavaScript for the frontend.

## Features

- User registration and login
- Hotel search based on city, price range, and star rating
- Display hotel details including name, image, star rating, prices from different sources, and booking link
- Bookmark hotels for logged-in users
- View and manage bookmarks

## Technologies Used


- Python
- Flask
- SQLAlchemy
- JavaScript
- HTML/CSS
- Docker
- PostgreSQL
- Scrapy

## Prerequisites

- Docker
- Docker Compose

## Setup and Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/TashfikS/Hotel-Search.git
    cd hotel-search-app
    ```

2. Create a `.env` file in the root directory with the following content:
    ```env
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=admin
    POSTGRES_DB=hotel_db
    ```

3. Build and start the Docker containers:
    ```sh
    docker-compose up --build
    ```

4. The application will be available at `http://localhost:8000/index.html` & swagger documentation at `http://localhost:8000/swagger`

## Project Structure

- `backend/`: Contains the backend Flask application
  - `app/`: Contains the main application code
    - `api.py`: API endpoints
    - `auth.py`: Authentication functions
    - `models.py`: Database models
    - `schemas.py`: Pydantic schemas
    - `scraping.py`: Web scraping logic
  - `migration_script.py`: Script to apply database migrations
- `frontend/`: Contains the frontend HTML, CSS, and JavaScript files
  - `index.html`: Main HTML file
  - `style.css`: CSS styles
  - `script.js`: JavaScript logic
- `docker-compose.yml`: Docker Compose configuration
- `Dockerfile`: Dockerfile for building the backend image

## Usage

1. Register a new user or log in with an existing account.
2. Use the search form to find hotels based on city, price range, and star rating.
3. View the search results and bookmark your favorite hotels.
4. View and manage your bookmarks in the bookmarks section.

## API Endpoints

- `POST /register/`: Register a new user
- `GET /users/me`: Get the current logged-in user
- `POST /hotels/`: Search for hotels
- `POST /bookmarks/`: Create a new bookmark
- `GET /bookmarks/`: Get all bookmarks for the logged-in user

## License

This project is licensed under the MIT License.