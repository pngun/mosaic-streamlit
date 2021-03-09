pyinstaller --additional-hooks-dir=hooks \
			--hidden-import missionbio.mosaic \
			--hidden-import missionbio.h5 \
			--hidden-import plotly \
			--clean run.py

rm -r ./build ./run.spec

mkdir mosaic-streamlit-mac
mv ./dist/run ./mosaic-streamlit-mac/libs
rm -r dist

ln -s ./libs/run mosaic-streamlit-mac/run-streamlit

cd ..
git archive -o latest.zip HEAD
mv latest.zip ./build/mosaic-streamlit-mac/
cd ./build/mosaic-streamlit-mac
unzip latest.zip
rm latest.zip
cd ..

zip -r -X mosaic-streamlit-mac.zip build
