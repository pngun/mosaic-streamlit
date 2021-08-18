pyinstaller --additional-hooks-dir=hooks \
  --hidden-import insights \
  --hidden-import missionbio.mosaic \
  --hidden-import missionbio.h5 \
  --hidden-import analytics \
  --hidden-import sentry_sdk \
  --clean -w run.py

cp -rp ../src/insights ./dist/run.app/Contents/MacOS/
rm -rf ./dist/run/
mv ./dist/run.app ./dist/runnable
