#!/usr/bin/env bash

# protoc.sh - Run protoc on all proto directories to generate python code.
#
# Usage:
#
#     ./protoc.sh
#
set -eu

# The root of the repository.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT"
for file in $(git ls-files | grep '\.proto'); do
  dir="$(dirname $file)"
  no_extension=${file%.proto}
  # Remove previously generated code
  rm -f ${no_extension}_pb2.py
  rm -f ${no_extension}_pb2_grpc.py
  python -m grpc_tools.protoc -I"$ROOT" -I"$dir" \
      --python_out="$dir" --grpc_python_out="$dir" "$file"
  # Fix the imports of generated GRPC code. This is a workaround for issue
  # https://github.com/grpc/grpc/issues/9575#issuecomment-293934506
  sed -i 's/^import /from . import /' ${no_extension}_pb2_grpc.py
  sed -i 's/^from . import grpc$/import grpc/' ${no_extension}_pb2_grpc.py
done
