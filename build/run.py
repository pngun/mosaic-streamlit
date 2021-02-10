import os
import sys
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen

from streamlit import cli as stcli

if __name__ == '__main__':

    launchdir = os.path.dirname(sys.argv[0])

    if launchdir == '':
        launchdir = '.'

    # Download latest code
    try:
        while True:
            val = input("Check for updates: yes/[no] -  ")
            if val not in ['yes', 'no', '']:
                print("Invalid input. Enter one of 'yes' or 'no', or press enter to skip")
            else:
                break

        if val == 'yes':
            resp = urlopen("https://github.com/MissionBio/mosaic-streamlit/archive/master.zip")

            with ZipFile(BytesIO(resp.read())) as zipfile:
                for file in zipfile.namelist()[1:]:
                    local_file = f'{launchdir}/' + '/'.join(file.split('/')[1:])
                    print('Downloading', local_file)

                    if local_file[-1] == '/':
                        if not os.path.exists(local_file):
                            os.mkdir(local_file)
                    else:
                        with open(local_file, 'wb') as f:
                            f.write(zipfile.read(file))

            print('Succesfully downloaded all files')
        else:
            print('Skipping updates')
    except Exception:
        print('FAILED to download code. Running local version.')

    sys.argv = ["streamlit", "run", f"{launchdir}/app.py", "--global.developmentMode=false"]
    sys.exit(stcli.main())
