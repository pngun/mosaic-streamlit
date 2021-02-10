pyinstaller --additional-hooks-dir=hooks \
			--hidden-import missionbio.mosaic \
			--hidden-import missionbio.h5 \
			--hidden-import plotly \
			--clean --onefile run.py

mv ./dist/* ../
rm -r ./build ./run.spec ./dist
