pyinstaller --additional-hooks-dir=hooks \
			--hidden-import missionbio.mosaic \
			--hidden-import missionbio.h5 \
			--hidden-import plotly \
			--clean --onefile run.py

rm -r ./build ./run.spec

mkdir mosaic-streamlit-mac
mv ./dist/run ./mosaic-streamlit-mac/run
rm -r dist

cd ..
git archive -o latest.zip HEAD
mv latest.zip ./build/mosaic-streamlit-mac/
cd ./build/mosaic-streamlit-mac
unzip latest.zip
rm latest.zip
cd ..

# zip -r -X mosaic-streamlit-mac.zip mosaic-streamlit-mac
