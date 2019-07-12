import jwt
from api.util.env import JWT_SECRET

class JWT:
    @staticmethod
    def generate(payload: object):
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    
    @staticmethod
    def decode(token):
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
