#!/usr/bin/env python
import sqlalchemy as sql
from argparse import ArgumentParser
from dsmith import db
from dsmith.db import *
from pathlib import Path
from progressbar import ProgressBar

from phd.lib.labm8 import crypto, fs


def export_todir(s: session_t, table, dir: Path) -> None:
  fs.mkdir(dir)
  q = s.query(table)
  num = s.query(sql.sql.func.count(table.id)).scalar()
  for result in ProgressBar(max_value=num)(q):
    buf = result.toProtobuf().SerializeToString()
    checksum = crypto.sha1(buf)
    with open(f"{dir}/{checksum}.pb", "wb") as f:
      f.write(buf)


def export_protobufs(s: session_t) -> None:
  print("exporting CLSmith results ...")
  export_todir(s, CLSmithResult, "dataset/clsmith")
  print("exporting DeepSmith results ...")
  export_todir(s, CLgenResult, "dataset/dsmith")
  print("exporting clang results ...")
  export_todir(s, CLgenClangResult, "dataset/clang")


if __name__ == "__main__":
  parser = ArgumentParser(description="Collect difftest results for a device")
  parser.add_argument("-H", "--hostname", type=str, default="cc1",
                      help="MySQL database hostname")
  args = parser.parse_args()

  # Connect to database
  db_hostname = args.hostname
  print("connected to", db.init(db_hostname))

  with Session(commit=False) as s:
    export_protobufs(s)
