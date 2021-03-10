# Build for Windows

## Setup environment

```shell
$ python --version
Python 3.8.8

$ python -m venv venv
$ .\venv\Scripts\Activate.ps1

$ Get-Command pip # make sure it's in the new virtualenv folder
$ pip install -r windows-requirements.txt
```

## Install mosaic and h5 

Download/clone the repos and checkout a specific tag/branch (tag v1.4.1 tested for mosaic, 3.2.0 for h5).

```shell
$ pip install -e ./missionbio-mosaic/
$ pip install -e ./missionbio-h5/
```

## Check that streamlit is working

```shell
$ streamlit run app.py
```
and select h5 file to check that it's working as expected.

## Build an exe

```shell
$ cd build
$ ./build.ps1
```

## Copy required files

Copy required files to `build/dist/run/h5` if you have any test files.

## Notes

The Streamlit cache decorator used in `tasks/` needs to be disabled for Windows.
It's causing various import errors, mostly for numba and plotly (only in EXE, works fine in a standard Python environment).
