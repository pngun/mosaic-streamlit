pyinstaller --additional-hooks-dir=hooks \
  --hidden-import analytics \
  --hidden-import missionbio.mosaic \
  --hidden-import missionbio.h5 \
  --hidden-import plotly \
  --hidden-import plotly.subplots \
  --hidden-import plotly.graph_objects \
  --hidden-import plotly.graph_objs \
  --hidden-import _plotly_future_ \
  --hidden-import _plotly_utils \
  --clean run.py

cp -r ../src/ ./dist/run/
mv ./dist/run ./dist/runnable

# sentry tmp fix
export SENTRY_SDK=$(python -c "import sentry_sdk;print(sentry_sdk.__file__)")
echo $SENTRY_SDK 
export SENTRY_SDK_PATH=$(dirname $SENTRY_SDK)
echo $SENTRY_SDK_PATH
cp -r $SENTRY_SDK_PATH ./dist/runnable/
