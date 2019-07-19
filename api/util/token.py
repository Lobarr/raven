import jwt
import json
from api.util.env import JWT_SECRET

JWT_ALGORITHM = 'HS256'

class Token:
    @staticmethod
    def generate(payload: object):
      token = jwt.encode(payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
      return token.decode('utf-8')
    
    @staticmethod
    def decode(token):
      payload = jwt.decode(token, key=JWT_SECRET, algorithms=JWT_ALGORITHM)
      return payload
