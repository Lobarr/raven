import os

PORT = os.getenv('PORT') or 3001
ENV = os.getenv('ENV') or 'dev'
DB = os.getenv('DB')
JWT_SECRET = os.getenv('JWT_SECRET')
REDIS = os.getenv('REDIS')
