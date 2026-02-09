import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    URL = os.getenv("MAXIMA_URL")
    USER = os.getenv("MAXIMA_USER")
    PASS = os.getenv("MAXIMA_PASS")
    XPATH_USER = os.getenv("XPATH_USER")
    XPATH_PASS = os.getenv("XPATH_PASS")
    ENV_PATH = os.path.join(os.path.dirname(__file__), '.env')