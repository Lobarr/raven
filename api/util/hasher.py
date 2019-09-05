import bcrypt

class Hasher:
  @staticmethod
  def hash(password: str) -> str:
    """
    hashes password

    @returns jwt token
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
  
  @staticmethod
  def validate(ctx: str, hash: str) -> bool:
    """
    validates a ctx against a hash
  
    @returns: match
    """
    return bcrypt.checkpw(ctx.encode('utf-8'), hash.encode('utf-8'))
