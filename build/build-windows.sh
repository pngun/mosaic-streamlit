pyinstaller --additional-hooks-dir=hooks \
  --hidden-import insights \
  --hidden-import missionbio.mosaic \
  --hidden-import missionbio.h5 \
  --hidden-import analytics \
  --hidden-import sentry_sdk \
  --clean run.py

cp -r ../src/insights ./dist/run/
mv ./dist/run ./dist/runnable
