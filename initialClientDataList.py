import json
from types import SimpleNamespace as Namespace


class initialClientDataList:
  def __init__(self, initial_amount):
    self.list_data = initial_amount
    
  def __init__(self):
    self.list_data = []


  def obj2JSON(self,o):
    #print(o)
    s = json.dumps(o.__dict__) 
    return s
    
  @staticmethod  
  def json2obj(s):
    #print(s)
    c = json.loads(s, object_hook=lambda d: Namespace(**d))
    return c