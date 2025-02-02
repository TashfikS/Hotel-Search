import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.environ.get("DATABASE_URL")
secret_key = os.environ.get("SECRET_KEY")
proxy_url = os.environ.get("PROXY_URL")