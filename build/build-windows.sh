pyinstaller --additional-hooks-dir=hooks \
  --hidden-import missionbio.mosaic \
  --hidden-import missionbio.h5 \
  --hidden-import plotly \
  --hidden-import plotly.subplots \
  --hidden-import plotly.graph_objects \
  --hidden-import plotly.graph_objs \
  --hidden-import _plotly_future_ \
  --hidden-import _plotly_utils \
  --clean run.py

cp ../*.py ./dist/run/
cp -r ../tasks ./dist/run/
