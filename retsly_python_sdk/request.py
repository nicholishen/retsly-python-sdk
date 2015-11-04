import requests
import jsonurl

class Request:
  def __init__(self, client, method, url, query={}):
    """
    Construct request for the Retsly API

    Args:
      client (dict):          Retsly client
      method (string):        method
      url (string):           url
      query (list):           query

    """
    self.client = client
    self.method = method
    self.url = url
    self.query = query
    self.key = None
    if self.client.token:
      self.query.update({'access_token': self.client.token})

  def where(self, key, op=None, value=None):
    # if only one argument, must be an array
    if (op is None and value is None):
      array = key
      if isinstance(array, list) and len(array) is not 3:
        raise ValueError('You must provide an array as the first argument, e.g. [key, op, value]')
      else:
        key, op, value = array[0], array[1], array[2]
    # assume operator is eq if only two arguments is provided
    elif (value is None):
      value = op
      op = 'eq'

    op = getOperator(op)

    if op == 'eq':
      query = {key: value}
    else:
      query = {key: {op: value}}

    self.query.update(query)
    return self

  def limit(self, value=None):
    if value is not None: self.query.update({'limit': value})
    return self

  def offset(self, value=None):
    if value is not None: self.query.update({'offset': value})
    return self

  def nextPage(self):
    if 'limit' in self.query:
      offset = self.query['offset'] if 'offset' in self.query else 0
      self.query['offset'] = offset + self.query['limit']
    return self

  def prevPage(self):
    if 'limit' in self.query and 'offset' in self.query:
      l = self.query['offset'] - self.query['limit']
      self.query['offset'] = l if l > 0 else 0
    return self

  def get(self, id):
    self.method = 'get'
    self.key = id
    return self.end(id)

  def getAll(self):
    self.method = 'get'
    self.key = None
    return self.end()

  def encodeQS(self):
    return jsonurl.query_string(self.query)

  def getURL(self, id):
    u = '/' + id if (id is not None) else ''
    return self.url + u + '?' + self.encodeQS()

  def end(self, id=None):
    r = requests.get(self.getURL(id), verify=False);
    return r.json()

def getOperator(op):
  if op == '<' or op == 'lt': return 'lt'
  elif op == '>' or op == 'gt': return 'gt'
  elif op == '<=' or op == 'lte': return 'lte'
  elif op == '>=' or op == 'gte': return 'gte'
  elif op == '!=' or op == 'ne': return 'ne'
  elif op == '=' or op == 'eq': return 'eq'
  elif op == 'regex': return 'regex'
  else: raise ValueError('You must provide a valid operator')
