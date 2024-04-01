#¬/usr/bin/env sh
ROOTDIR=$(git rev-parse --show-toplevel)
SRCPATH=$(for d in  $(find ${ROOTDIR}/libs/python/packages -type d -name src); do echo -n "$d:"; done)
export PYTHONPATH="${ROOTDIR}/libs/python/packages:$SRCPATH"
