pyinstaller --additional-hooks-dir=hooks \
  --hidden-import missionbio.mosaic \
  --hidden-import missionbio.h5 \
  --hidden-import plotly \
  --hidden-import plotly.subplots \
  --hidden-import plotly.graph_objects \
  --hidden-import plotly.graph_objs \
  --hidden-import _plotly_future_ \
  --hidden-import _plotly_utils \
  --clean -w run.py

rm -rf ./dist/run/
cp -r ../src ./dist/run.app/Contents/Resources/
cp -r ../src ./dist/run.app/Contents/MacOS/
mv ./dist/run.app ./dist/runnable
