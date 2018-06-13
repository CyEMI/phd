#!/bin/bash
# A Python3 wrapper which selects python2 for bazel tools.
#
# This is to workaround a known bug in the rules_docker bazel package, which
# depends on code which is not Python3 compatible.
# See: https://github.com/bazelbuild/rules_docker/issues/293

if [[ $1 = *"/bazel_tools/"* ]] || \
   [[ $1 = *"/containerregistry/"* ]] || \
   [[ $1 = *"/external/puller/file/puller.par" ]] || \
   [[ $1 = *"/io_bazel_rules_docker/"* ]]; then
    PYTHON_BIN=python2
else
    PYTHON_BIN=python3.6
fi

${PYTHON_BIN} "$@"