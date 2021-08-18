pyinstaller --additional-hooks-dir=hooks \
  --hidden-import insights \
  --hidden-import missionbio.mosaic \
  --hidden-import missionbio.h5 \
  --hidden-import analytics \
  --hidden-import sentry_sdk \
  --clean -w run.py

rm -rf ./dist/run/
mv ./dist/run.app ./dist/runnable
