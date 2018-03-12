"""This file defines the testcase generator."""
import datetime
import hashlib
import typing

import sqlalchemy as sql
from sqlalchemy import orm

from deeplearning.deepsmith import db
from deeplearning.deepsmith.proto import deepsmith_pb2

# The index types for tables defined in this file.
_GeneratorId = sql.Integer
_GeneratorOptSetId = sql.Binary(16)  # MD5 checksum.
_GeneratorOptId = sql.Integer
_GeneratorOptNameId = db.StringTable.id_t
_GeneratorOptValueId = db.StringTable.id_t


class Generator(db.Table):
  id_t = _GeneratorId
  __tablename__ = "generators"

  # Columns.
  id: int = sql.Column(id_t, primary_key=True)
  date_added: datetime.datetime = sql.Column(
      sql.DateTime, nullable=False, default=db.now)
  name: str = sql.Column(sql.String(1024), nullable=False)
  optset_id: bytes = sql.Column(
      _GeneratorOptSetId, sql.ForeignKey("generator_optsets.id"), nullable=False)

  # Relationships.
  testcases: typing.List["Testcase"] = orm.relationship(
      "Testcase", back_populates="generator")
  optset: typing.List["GeneratorOpt"] = orm.relationship(
      "GeneratorOpt", secondary="generator_optsets",
      primaryjoin="GeneratorOptSet.id == Generator.optset_id",
      secondaryjoin="GeneratorOptSet.opt_id == GeneratorOpt.id")

  # Constraints.
  __table_args__ = (
    sql.UniqueConstraint('name', 'optset_id', name='unique_generator'),
  )

  @property
  def opts(self) -> typing.Dict[str, str]:
    """Get the generator options.

    Returns:
      A map of generator options.
    """
    return {opt.name.string: opt.value.string for opt in self.optset}

  def SetProto(self, proto: deepsmith_pb2.Generator) -> deepsmith_pb2.Generator:
    """Set a protocol buffer representation.

    Args:
      proto: A protocol buffer message.

    Returns:
      A Generator message.
    """
    proto.name = self.name
    for opt in self.optset:
      proto.opts[opt.name.string] = opt.value.string
    return proto

  def ToProto(self) -> deepsmith_pb2.Generator:
    """Create protocol buffer representation.

    Returns:
      A Generator message.
    """
    proto = deepsmith_pb2.Generator()
    return self.SetProto(proto)

  @classmethod
  def GetOrAdd(cls, session: db.session_t,
               proto: deepsmith_pb2.Generator) -> "Generator":

    # Build the list of options, and md5sum the key value strings.
    opts = []
    md5 = hashlib.md5()
    for proto_opt_name in sorted(proto.opts):
      proto_opt_value = proto.opts[proto_opt_name]
      md5.update((proto_opt_name + proto_opt_value).encode("utf-8"))
      opt = db.GetOrAdd(
          session, GeneratorOpt,
          name=GeneratorOptName.GetOrAdd(session, proto_opt_name),
          value=GeneratorOptValue.GetOrAdd(session, proto_opt_value),
      )
      opts.append(opt)

    # Create optset table entries.
    optset_id = md5.digest()
    for opt in opts:
      db.GetOrAdd(session, GeneratorOptSet, id=optset_id, opt=opt)

    return db.GetOrAdd(
        session, cls,
        name=proto.name,
        optset_id=optset_id,
    )


class GeneratorOptSet(db.Table):
  """A set of of generator options.

  An option set groups options for generators.
  """
  __tablename__ = "generator_optsets"
  id_t = _GeneratorOptSetId

  # Columns.
  id: bytes = sql.Column(
      id_t, sql.ForeignKey("generators.optset_id"), nullable=False)
  opt_id: int = sql.Column(
      _GeneratorOptId, sql.ForeignKey("generator_opts.id"), nullable=False)

  # Relationships.
  generators: typing.List[Generator] = orm.relationship(
      "Generator", foreign_keys=[Generator.optset_id])
  opt: "GeneratorOpt" = orm.relationship("GeneratorOpt")

  # Constraints.
  __table_args__ = (
    sql.PrimaryKeyConstraint(
        "id", "opt_id", name="unique_generator_optset"),
  )

  def __repr__(self):
    hex_id = binascii.hexlify(self.id).decode("utf-8")
    return f"{hex_id}: {self.opt_id}={self.opt}"


class GeneratorOpt(db.Table):
  """A generator option consists of a <name, value> pair."""
  id_t = _GeneratorOptId
  __tablename__ = "generator_opts"

  # Columns.
  id: int = sql.Column(id_t, primary_key=True)
  date_added: datetime.datetime = sql.Column(
      sql.DateTime, nullable=False, default=db.now)
  name_id: _GeneratorOptNameId = sql.Column(
      _GeneratorOptNameId, sql.ForeignKey("generator_opt_names.id"), nullable=False)
  value_id: _GeneratorOptValueId = sql.Column(
      _GeneratorOptValueId, sql.ForeignKey("generator_opt_values.id"),
      nullable=False)

  # Relationships.
  name: "GeneratorOptName" = orm.relationship(
      "GeneratorOptName", back_populates="opts")
  value: "GeneratorOptValue" = orm.relationship(
      "GeneratorOptValue", back_populates="opts")

  # Constraints.
  __table_args__ = (
    sql.UniqueConstraint("name_id", "value_id", name="unique_generator_opt"),
  )

  def __repr__(self):
    return f"{self.name}: {self.value}"


class GeneratorOptName(db.StringTable):
  """The name of a generator option."""
  id_t = _GeneratorOptNameId
  __tablename__ = "generator_opt_names"

  # Relationships.
  opts: typing.List[GeneratorOpt] = orm.relationship(
      GeneratorOpt, back_populates="name")


class GeneratorOptValue(db.StringTable):
  """The value of a generator option."""
  id_t = _GeneratorOptValueId
  __tablename__ = "generator_opt_values"

  # Relationships.
  opts: typing.List[GeneratorOpt] = orm.relationship(
      GeneratorOpt, back_populates="value")