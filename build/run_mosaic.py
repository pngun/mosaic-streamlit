import os
import sys
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

from streamlit import cli as stcli

if __name__ == '__main__':

    launchdir = os.path.dirname(sys.argv[0])

    # Download latest code
    resp = urlopen("http://www.test.com/file.zip")
    zipfile = ZipFile(BytesIO(resp.read()))

    for file in zipfile.namelist():
        if 'mosaic-vignettes-master/streamlit/' in file:
            zipfile.extract(file, path='{launchdir}')


    sys.argv = ["streamlit", "run", f"{launchdir}/mosaic.py", "--global.developmentMode=false"]
    sys.exit(stcli.main())
