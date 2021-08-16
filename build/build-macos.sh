pyinstaller --additional-hooks-dir=hooks \
  --hidden-import missionbio.mosaic \
  --hidden-import missionbio.h5 \
  --hidden-import analytics \
  --hidden-import sentry_sdk \
  --clean -w run.py

rm -rf ./dist/run/
cp -r ../src ./dist/run.app/Contents/Resources/
cp -r ../src ./dist/run.app/Contents/MacOS/
mv ./dist/run.app ./dist/runnable
