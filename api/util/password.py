import bcrypt
from password_strength.policy import PasswordPolicy, PasswordStats

class Password:
  @staticmethod
  def hash(password: str) -> str:
    """
    hashes password

    @returns jwt token
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
  
  @staticmethod
  def validate(password: str, hash: str) -> bool:
    """
    validates a password against a hash
  
    @returns: match
    """
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))
