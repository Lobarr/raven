import bcrypt
from password_strength.policy import PasswordPolicy, PasswordStats

class Password:
  @staticmethod
  def hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(14)).decode('utf-8')
  
  @staticmethod
  def validate(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
