import bcrypt
from password_strength.policy import PasswordPolicy, PasswordStats

class Password:
  @staticmethod
  def hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
  
  """
  validates a password against a hash

  @returns: match
  """
  @staticmethod
  def validate(password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
