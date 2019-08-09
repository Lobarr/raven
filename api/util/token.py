import jwt
import json
from api.util.env import JWT_SECRET

JWT_ALGORITHM = 'HS256'

class Token:
    """
    generates a jwt token

    @return: jwt token
    """
    @staticmethod
    def generate(payload: object) -> str:
      token = jwt.encode(payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
      return token.decode('utf-8')
    
    """
    decodes a jwt token into it's payload

    @return: provided tokens payload
    """
    @staticmethod
    def decode(token: str) -> object:
      payload = jwt.decode(token, key=JWT_SECRET, algorithms=JWT_ALGORITHM)
      return payload
