"""
Database backend.
"""
import datetime
import pathlib
import typing

import sqlalchemy as sql
from absl import flags
from absl import logging
from sqlalchemy.ext.declarative import declarative_base

from deeplearning.deepsmith.proto import datastore_pb2

FLAGS = flags.FLAGS

flags.DEFINE_bool('sql_echo', None, 'Print all executed SQL statements')

# The database session type.
session_t = sql.orm.session.Session

# The database query type.
query_t = sql.orm.query.Query

# A type alias for annotating methods which take or return protocol buffers.
ProtocolBuffer = typing.Any

# The SQLAlchemy base table.
Base = declarative_base()

# A shorthand declaration for the current time.
now = datetime.datetime.utcnow


class InvalidInputError(ValueError):
  pass


class StringTooLongError(ValueError):
  def __init__(self, column_name: str, string: str, max_len: int):
    self.column_name = column_name
    self.string = string
    self.max_len = max_len

  def __repr__(self):
    n = len(self.max_len)
    s = string[:20]
    return (f"String '{s}...' too long for '{self.column_name}'. " +
            f"Max length: {self.max_len}, actual length: {n}. ")


class Table(Base):
  """A database-backed object.

  This extends the standard SQLAlchemy 'Base' object by adding features
  specific to Deepsmith: methods for serializing to and from protobufs, and
  an index type for use when declaring foreign keys.
  """
  __abstract__ = True
  id_t = None

  @classmethod
  def GetOrAdd(cls, session: session_t, proto: ProtocolBuffer) -> 'Table':
    """Instantiate an object from a protocol buffer message.

    This is the preferred method for creating database-backed instances.
    If the created instance does not already exist in the database, it is
    added.

    Args:
      session: A database session.
      proto: A protocol buffer.

    Returns:
      An instance.

    Raises:
      InvalidInputError: In case one or more values contained in the protocol
        buffer cannot be stored in the database schema.
    """
    raise NotImplementedError(type(cls).__name__ + ".GetOrAdd() not implemented")

  def ToProto(self) -> ProtocolBuffer:
    """Create protocol buffer representation.

    Returns:
      A protocol buffer.
    """
    raise NotImplementedError(type(self).__name__ + ".ToProto() not implemented")

  def SetProto(self, proto: ProtocolBuffer) -> ProtocolBuffer:
    """Set a protocol buffer representation.

    Args:
      proto: A protocol buffer.

    Returns:
      The same protocol buffer that is passed as argument.
    """
    raise NotImplementedError(type(self).__name__ + ".SetProto() not implemented")

  @classmethod
  def ProtoFromFile(cls, path: pathlib.Path) -> ProtocolBuffer:
    """Instantiate a protocol buffer representation from file.

    Args:
      path: Path to the proto file.

    Returns:
      Protocol buffer message instance.
    """
    raise NotImplementedError(type(cls).__name__ +
                              ".ProtoFromFile() not implemented")

  @classmethod
  def FromFile(cls, session: session_t, path: pathlib.Path) -> 'Table':
    """Instantiate an object from a serialized protocol buffer on file.

    Args:
      session: A database session.
      path: Path to the proto file.

    Returns:
      An instance.
    """
    raise NotImplementedError(type(cls).__name__ +
                              ".FromFile() not implemented")

  def __repr__(self):
    try:
      return str(self.ToProto())
    except NotImplementedError:
      typename = type(self).__name__
      return f"TODO: Define {typename}.ToProto() method"


class StringTable(Table):
  """A table of unique strings.

  A string table maps a unique string to a unique integer. In most cases, it is
  better to use a string table than to store strings directly in columns. The
  advantage of a string table is that it saves space for duplicate strings, and
  reduces table sizes by having tables contain only integer indexes. This makes
  grouping rows by string values faster, as well as reducing the cost of
  modifying a string.

  The downside of a string table is that it requires one extra table lookup to
  resolve the string itself.

  Note that the maximum length of strings is hardcoded to 4k. You should only
  use the StringTable.GetOrAdd() method to insert new strings, as this method
  performs the bounds checking and will raise a StringTooLongError if required.
  Instantiating a StringTable directly with a string which is too long will
  cause some SQL-based error which is harder to catch and potentially
  backend-specific.
  """
  __abstract__ = True
  id_t = sql.Integer
  maxlen = 4096

  # Columns:
  id: int = sql.Column(id_t, primary_key=True)
  date_added: datetime.datetime = sql.Column(
      sql.DateTime, nullable=False, default=now)
  string: str = sql.Column(sql.String(maxlen), nullable=False, unique=True)

  @classmethod
  def GetOrAdd(cls, session: session_t, string: str) -> 'StringTable':
    """Instantiate a StringTable entry from a string.

    This is the preferred method for creating database-backed instances.
    If the created instance does not already exist in the database, it is
    added.

    Args:
      session: A database session.
      string: The string.

    Returns:
      A StringTable instance.

    Raises:
      StringTooLongError: If the string is too long.
    """
    if len(string) > cls.maxlen:
      raise StringTooLongError(cls, string, cls.maxlen)

    return GetOrAdd(session, cls, string=string)

  def TruncatedString(self, n=80):
    """Return the truncated first 'n' characters of the string.

    Args:
      n: The maximum length of the string to return.

    Returns:
      A truncated string.
    """
    if self.string and len(self.string) > n:
      return self.string[:n - 3] + '...'
    elif self.string:
      return self.string
    else:
      return ''

  def __repr__(self):
    return self.TruncatedString(n=52)


def MakeEngine(config: datastore_pb2.DataStore) -> sql.engine.Engine:
  """
  Raises:
      ValueError: If DB_ENGINE config value is invalid.
  """
  if config.HasField('sqlite'):
    url, public_url = config.sqlite.url, config.sqlite.url
  elif config.HasField('mysql'):
    username, password = config.mysql.username, config.mysql.password
    hostname = config.mysql.password
    port = config.mysql.password

    # Use UTF-8 encoding (default is latin-1) when connecting to MySQL.
    # See: https://stackoverflow.com/a/16404147/1318051
    public_url = f'mysql://{username}@{hostname}:{port}/{name}?charset=utf8'
    url = f'mysql+mysqldb://{username}:{password}@{hostname}:{port}/{name}?charset=utf8'
  else:
    raise ValueError(f'unsupported database engine {engine}')

  logging.info('creating database engine %s', public_url)
  return sql.create_engine(url, encoding='utf-8', echo=FLAGS.sql_echo)


def GetOrAdd(session: sql.orm.session.Session, model,
             defaults: typing.Dict[str, object] = None, **kwargs):
  """
  Instantiate a mapped database object. If the object is not in the database,
  add it.

  Note that no change is written to disk until commit() is called on the
  session.
  """
  instance = session.query(model).filter_by(**kwargs).first()
  if not instance:
    params = {k: v for k, v in kwargs.items()
              if not isinstance(v, sql.sql.expression.ClauseElement)}
    params.update(defaults or {})
    instance = model(**params)
    session.add(instance)

    # logging
    logging.debug("new %s record", model.__name__)

  return instance