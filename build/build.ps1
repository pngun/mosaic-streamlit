pyinstaller --additional-hooks-dir=hooks --hidden-import igraph._igraph --hidden-import missionbio.mosaic --hidden-import missionbio.h5 --hidden-import plotly --clean run.py
Copy-Item ..\*.py -Destination .\dist\run\
Copy-Item ..\tasks -Destination .\dist\run\ -Recurse
