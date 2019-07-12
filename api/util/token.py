import jwt
import json
from api.util.env import JWT_SECRET

class Token:
    @staticmethod
    def generate(payload: object):
      token = jwt.encode(payload, key=JWT_SECRET, algorithm='HS256')
      return token.decode('utf-8')
    
    @staticmethod
    def decode(token):
      payload = jwt.decode(token, key=JWT_SECRET, algorithms='HS256')
      return payload
