import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    BASE_RPC_URL = os.getenv('BASE_RPC_URL')
    ESCROW_CONTRACT_ADDRESS = os.getenv('ESCROW_CONTRACT_ADDRESS')
    PLATFORM_WALLET = os.getenv('PLATFORM_WALLET')
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')
    TEST_USER_PRIVATE_KEY = os.getenv('TEST_USER_PRIVATE_KEY')
    PINATA_API_KEY = os.getenv('PINATA_API_KEY')
    PINATA_API_SECRET = os.getenv('PINATA_API_SECRET')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
