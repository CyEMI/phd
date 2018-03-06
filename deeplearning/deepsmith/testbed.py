"""This file implements testbeds."""
import binascii
import datetime
import hashlib
import typing

import sqlalchemy as sql
from sqlalchemy import orm

import deeplearning.deepsmith.toolchain
from deeplearning.deepsmith import db
from deeplearning.deepsmith.protos import deepsmith_pb2

# The index types for tables defined in this file.
_TestbedId = sql.Integer
_TestbedOptSetId = sql.Binary(16)  # MD5 checksum.
_TestbedOptId = sql.Integer
_TestbedOptNameId = db.ListOfNames.id_t
_TestbedOptValueId = db.ListOfNames.id_t


class Testbed(db.Table):
  """A Testbed is a system on which testcases may be run.

  Each testbed is a <toolchain,name,version,opts> tuple.
  """
  id_t = _TestbedId
  __tablename__ = "testbeds"

  # Columns.
  id: int = sql.Column(id_t, primary_key=True)
  date_added: datetime.datetime = sql.Column(sql.DateTime, nullable=False,
                                             default=db.now)
  toolchain_id: int = sql.Column(
      deeplearning.deepsmith.toolchain.Toolchain.id_t,
      sql.ForeignKey("toolchains.id"), nullable=False)
  name: str = sql.Column(sql.String(1024), nullable=False)
  version: str = sql.Column(sql.String(1024), nullable=False)
  optset_id: int = sql.Column(
      _TestbedOptSetId, sql.ForeignKey("testbed_optsets.id"), nullable=False)

  # Relationships.
  toolchain: deeplearning.deepsmith.toolchain.Toolchain = orm.relationship(
      "Toolchain")
  results: typing.List["Result"] = orm.relationship(
      "Result", back_populates="testbed")
  pending_results: typing.List["PendingResult"] = orm.relationship(
      "PendingResult", back_populates="testbed")
  optset: typing.List["TestbedOpt"] = orm.relationship(
      "TestbedOpt", secondary="testbed_optsets",
      primaryjoin="TestbedOptSet.id == Testbed.optset_id",
      secondaryjoin="TestbedOptSet.opt_id == TestbedOpt.id")

  # Constraints.
  __table_args__ = (
    sql.UniqueConstraint(
        "toolchain_id", "name", "version", "optset_id", name="unique_testbed"),
  )

  @property
  def opts(self) -> typing.Dict[str, str]:
    """Get the testbed options.

    Returns:
      A map of testbed options.
    """
    return {opt.name.name: opt.value.name for opt in self.optset}

  def ToProto(self) -> deepsmith_pb2.Testbed:
    """Create protocol buffer representation.

    Returns:
      A Testbed message.
    """
    proto = deepsmith_pb2.Testbed()
    return self.SetProto(proto)

  def SetProto(self, proto: deepsmith_pb2.Testbed) -> deepsmith_pb2.Testbed:
    """Set a protocol buffer representation.

    Args:
      proto: A protocol buffer message.

    Returns:
      A Testbed message.
    """
    proto.toolchain = self.toolchain.name
    proto.name = self.name
    proto.version = self.version
    for opt in self.optset:
      proto.opts[opt.name.name] = opt.value.name
    return proto

  @classmethod
  def GetOrAdd(cls, session: db.session_t,
               proto: deepsmith_pb2.Testbed) -> "Testbed":
    """Instantiate a Testbed from a protocol buffer.

    This is the preferred method for creating database-backed Testbed
    instances. If the Testbed does not already exist in the database, it is
    added.

    Args:
      session: A database session.
      proto: A Testbed message.

    Returns:
      A Testbed.
    """
    toolchain = deeplearning.deepsmith.toolchain.Toolchain.GetOrAdd(
        session, proto.toolchain
    )

    # Build the list of options, and md5sum the key value strings.
    opts = []
    md5 = hashlib.md5()
    for proto_opt_name in sorted(proto.opts):
      proto_opt_value = proto.opts[proto_opt_name]
      md5.update((proto_opt_name + proto_opt_value).encode("utf-8"))
      opt = db.GetOrAdd(
          session, TestbedOpt,
          name=db.GetOrAdd(
              session, TestbedOptName,
              name=proto_opt_name,
          ),
          value=db.GetOrAdd(
              session, TestbedOptValue,
              name=proto_opt_value
          ),
      )
      opts.append(opt)

    # Create optset table entries.
    optset_id = md5.digest()
    for opt in opts:
      db.GetOrAdd(session, TestbedOptSet, id=optset_id, opt=opt)

    return db.GetOrAdd(
        session, cls,
        toolchain=toolchain,
        name=proto.name,
        version=proto.version,
        optset_id=optset_id,
    )


class TestbedOptSet(db.Table):
  """A set of of testbed options.

  An option set groups options for testbed.
  """
  __tablename__ = "testbed_optsets"
  id_t = _TestbedOptSetId

  # Columns.
  id: bytes = sql.Column(
      id_t, sql.ForeignKey("testbeds.optset_id"), nullable=False)
  opt_id: int = sql.Column(
      _TestbedOptId, sql.ForeignKey("testbed_opts.id"), nullable=False)

  # Relationships.
  testbeds: typing.List[Testbed] = orm.relationship(
      "Testbed", foreign_keys=[Testbed.optset_id])
  opt: "TestbedOpt" = orm.relationship("TestbedOpt")

  # Constraints.
  __table_args__ = (
    sql.PrimaryKeyConstraint(
        "id", "opt_id", name="unique_testbed_optset"),
  )

  def __repr__(self):
    hex_id = binascii.hexlify(self.id).decode("utf-8")
    return f"{hex_id}: {self.opt_id}={self.opt}"


class TestbedOpt(db.Table):
  """A testbed option consists of a <name, value> pair."""
  id_t = _TestbedOptId
  __tablename__ = "testbed_opts"

  # Columns.
  id: int = sql.Column(id_t, primary_key=True)
  date_added: datetime.datetime = sql.Column(
      sql.DateTime, nullable=False, default=db.now)
  name_id: _TestbedOptNameId = sql.Column(
      _TestbedOptNameId, sql.ForeignKey("testbed_opt_names.id"), nullable=False)
  value_id: _TestbedOptValueId = sql.Column(
      _TestbedOptValueId, sql.ForeignKey("testbed_opt_values.id"),
      nullable=False)

  # Relationships.
  name: "TestbedOptName" = orm.relationship(
      "TestbedOptName", back_populates="opts")
  value: "TestbedOptValue" = orm.relationship(
      "TestbedOptValue", back_populates="opts")

  # Constraints.
  __table_args__ = (
    sql.UniqueConstraint("name_id", "value_id", name="unique_testbed_opt"),
  )

  def __repr__(self):
    return f"{self.name}: {self.value}"


class TestbedOptName(db.ListOfNames):
  """The name of a testbed option."""
  id_t = _TestbedOptNameId
  __tablename__ = "testbed_opt_names"

  # Relationships.
  opts: typing.List[TestbedOpt] = orm.relationship(
      TestbedOpt, back_populates="name")


class TestbedOptValue(db.ListOfNames):
  """The value of a testbed option."""
  id_t = _TestbedOptValueId
  __tablename__ = "testbed_opt_values"

  # Relationships.
  opts: typing.List[TestbedOpt] = orm.relationship(
      TestbedOpt, back_populates="value")
