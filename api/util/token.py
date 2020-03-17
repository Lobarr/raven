import jwt
from api.util.env import JWT_SECRET

JWT_ALGORITHM = 'HS256'


class Token:
    @staticmethod
    def generate(payload: dict) -> str:
        """
        generates a jwt token

        @return: jwt token
        """
        token = jwt.encode(payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token.decode('utf-8')

    @staticmethod
    def decode(token: str) -> dict:
        """
        decodes a jwt token into it's payload

        @return: provided tokens payload
        """
        payload = jwt.decode(token, key=JWT_SECRET, algorithms=JWT_ALGORITHM)
        return payload
