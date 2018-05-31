"""This file defines a database for pre-preprocessed content files."""
import binascii
import datetime
import multiprocessing
import pathlib
import pickle
import time

import humanize
import numpy as np
import progressbar
import sqlalchemy as sql
from absl import flags
from absl import logging
from sqlalchemy.ext import declarative
from sqlalchemy.sql import func

from deeplearning.clgen.corpuses import atomizers
from deeplearning.clgen.corpuses import preprocessed
from deeplearning.clgen.proto import internal_pb2
from lib.labm8 import sqlutil


FLAGS = flags.FLAGS

Base = declarative.declarative_base()


class Meta(Base):
  """Meta table for encoded content files database."""
  __tablename__ = 'meta'

  key: str = sql.Column(sql.String(1024), primary_key=True)
  value: str = sql.Column(sql.String(1024), nullable=False)


class EncodedContentFile(Base):
  """A single encoded content file."""
  __tablename__ = 'encoded_contentfiles'

  # The ID of the PreprocessedContentFile.
  id: int = sql.Column(sql.Integer, primary_key=True)
  data: bytes = sql.Column(sql.Binary(), nullable=False)
  tokencount: int = sql.Column(sql.Integer, nullable=False)
  # The number of milliseconds encoding took.
  encoding_time_ms: int = sql.Column(sql.Integer, nullable=False)
  date_added: datetime.datetime = sql.Column(sql.DateTime, nullable=False)

  @property
  def indices_array(self) -> np.ndarray:
    """The numpy array of the encoded data."""
    return np.frombuffer(self.data, dtype=np.int32)

  @property
  def sha256_hex(self) -> str:
    """Return the 64 character hexadecimal representation of sha256."""
    return binascii.hexlify(self.sha256).decode('utf-8')

  @classmethod
  def FromPreprocessed(
      cls, preprocessed_cf: preprocessed.PreprocessedContentFile,
      atomizer: atomizers.AtomizerBase, eof: str) -> 'EncodedContentFile':
    """Instantiate an EncodedContentFile from a preprocessed file.

    Args:
      preprocessed_cf: A PreprocessedContentFile instance.
      atomizer: The atomizer to encode using.
      eof: An end-of-file marker which is concatenated to the encoded sequence.

    Returns:
      An EncodedContentFile instance.
    """
    start_time = time.time()
    data = atomizer.AtomizeString(preprocessed_cf.text)
    encoding_time_ms = int((time.time() - start_time) * 1000)
    return EncodedContentFile(
        id=preprocessed_cf.id,
        # Encode the end-of-file marker separately to ensure that it resolves to
        # the correct token. For example if the vocabulary contains 'a', 'b',
        # and 'ab', then a content file 'a' with EOF marker 'b' would be encoded
        # as 'ab', instead of 'a'+'b'.
        data=np.concatenate((data, atomizer.AtomizeString(eof))).tostring(),
        tokencount=len(data),
        encoding_time_ms=encoding_time_ms,
        date_added=datetime.datetime.utcnow())


def EncoderWorker(job: internal_pb2.EncoderWorker) -> EncodedContentFile:
  """Encode a single content file."""
  return EncodedContentFile.FromPreprocessed(
      preprocessed.PreprocessedContentFile(id=job.id, text=job.text),
      pickle.loads(job.pickled_atomizer), job.contentfile_separator)


class EncodedContentFiles(sqlutil.Database):
  """A database of encoded pre-processed contentfiles."""

  def __init__(self, path: pathlib.Path):
    super(EncodedContentFiles, self).__init__(path, Base)

  def Create(self, p: preprocessed.PreprocessedContentFiles,
             atomizer: atomizers.AtomizerBase,
             contentfile_separator: str) -> bool:
    """Populate the encoded contentfiles database.

    Args:
      p: A PreprocessedContentFiles database.
      atomizer: An AtomizerBase instance.
      contentfile_separator: The contentfile separator.

    Returns:
      True if work was done, else False.
    """
    with self.Session() as session:
      if not self.IsDone(session):
        self.Import(session, p, atomizer, contentfile_separator)
        self.SetDone(session)
        session.commit()
    logging.info("Encoded corpus: %s tokens, %s files",
                 humanize.intcomma(self.token_count),
                 humanize.intcomma(self.size))

  @property
  def size(self):
    """Return the total number of files in the encoded corpus."""
    with self.Session() as session:
      return session.query(EncodedContentFile).count()

  @property
  def token_count(self) -> int:
    """Return the total number of tokens in the encoded corpus.

    This excludes the EOF markers which are appended to each encoded text.
    """
    with self.Session() as session:
      return session.query(func.sum(EncodedContentFile.tokencount)).scalar()

  def IsDone(self, session: sqlutil.Database.session_t):
    if session.query(Meta).filter(Meta.key == 'done').first():
      return True
    else:
      return False

  def SetDone(self, session: sqlutil.Database.session_t):
    session.add(Meta(key='done', value='yes'))

  def Import(self, session: sqlutil.Database.session_t,
             preprocessed_db: preprocessed.PreprocessedContentFiles,
             atomizer: atomizers.AtomizerBase,
             contentfile_separator: str) -> None:
    start_time = time.time()
    with preprocessed_db.Session() as p_session:
      query = p_session.query(preprocessed.PreprocessedContentFile).filter(
          preprocessed.PreprocessedContentFile.preprocessing_succeeded == True,
          ~preprocessed.PreprocessedContentFile.id.in_(
              session.query(EncodedContentFile.id).all()))
      jobs = [
        internal_pb2.EncoderWorker(
            id=x.id, text=x.text, contentfile_separator=contentfile_separator,
            pickled_atomizer=pickle.dumps(atomizer))
        for x in query
      ]
      logging.info('Encoding %s of %s preprocessed files',
                   humanize.intcomma(query.count()),
                   humanize.intcomma(p_session.query(
                       preprocessed.PreprocessedContentFile).filter(
                       preprocessed.PreprocessedContentFile.preprocessing_succeeded == True).count()))
      pool = multiprocessing.Pool()
      bar = progressbar.ProgressBar(max_value=len(jobs))
      last_commit = time.time()
      for encoded_cf in bar(pool.imap_unordered(
          EncoderWorker, jobs)):
        session.add(encoded_cf)
        current_time = time.time()
        if current_time - last_commit > 10:
          session.commit()
          last_commit = current_time

      logging.info('Encoded %s files in %s ms',
                   humanize.intcomma(query.count()),
                   humanize.intcomma(int((time.time() - start_time) * 1000)))