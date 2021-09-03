#!/usr/bin/env bash

rm -rf build dist run.spec __pycache__
export PYTHONPATH=$PWD/../src;$PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

set -e

pyinstaller --additional-hooks-dir=hooks \
  --paths ../src \
  --copy-metadata streamlit \
  --collect-data altair \
  --collect-all insights \
  --hidden-import insights \
  --hidden-import missionbio.mosaic \
  --hidden-import missionbio.h5 \
  --hidden-import analytics \
  --hidden-import sentry_sdk \
  --clean run.py

mv ./dist/run ./dist/runnable
