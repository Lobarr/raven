import base64
import json

class Bytes:
  """
  converts string data to bytes
  """
  @staticmethod
  def str_to_bytes(string: str):
    return string.encode("utf-8")
  
  """
  coverts object to bytes
  """
  @staticmethod
  def object_to_bytes(obj: object):
    return json.dumps(obj).encode('utf-8')
  """
  encodes bytes data to base64
  """
  @staticmethod
  def encode_bytes(data):
    return base64.b64encode(data)
  """
  decodes bytes data from base64
  """
  @staticmethod
  def decode_bytes(data):
    return base64.b64decode(data)
