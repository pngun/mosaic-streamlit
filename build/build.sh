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

cp ../*.py ./dist/run/
cp -r ../tasks ./dist/run/
cp ../*.py ./dist/run.app/Contents/Resources/
cp -r ../tasks ./dist/run.app/Contents/Resources/
cp ../*.py ./dist/run.app/Contents/MacOS/
cp -r ../tasks ./dist/run.app/Contents/MacOS/
