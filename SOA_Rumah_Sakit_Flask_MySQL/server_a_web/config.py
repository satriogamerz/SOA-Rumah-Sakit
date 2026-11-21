import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-this')
    API_BASE_URL = os.getenv(
        'API_BASE_URL',
        'http://10.241.18.211:5001'
    )