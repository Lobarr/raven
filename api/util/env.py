import os

PORT = os.getenv('PORT') or 3001
ENV = os.getenv('ENV') or 'dev'
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB = os.getenv('DB')
JWT_SECRET = os.getenv('JWT_SECRET')
REDIS = os.getenv('REDIS')
