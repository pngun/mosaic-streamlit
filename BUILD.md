# Build for Windows

## Setup environment

```shell
$ python --version
Python 3.8.8

$ python -m venv venv
```

### On Windows: 

```
$ .\venv\Scripts\Activate.ps1

# make sure it's in the new virtualenv folder
$ Get-Command python 
$ Get-Command pip # make sure it's in the new virtualenv folder

$ python -m pip install -U pip wheel
$ pip install -r windows-requirements.txt
```

### On macOS: 

```
$ source ./venv/bin/activate

# make sure it's in the new virtualenv folder
$ which python
$ which pip 

$ python -m pip install -U pip wheel
$ pip install -r macos-requirements.txt
```

## Check that streamlit is working

Copy H5 files to `$HOME/mosaic-streamlit-h5` if you have any test files.

```shell
$ streamlit run app.py
```
and select H5 file to check that it's working as expected.

## Build a distribution

```shell
$ cd build
$ ./build.ps1 # on Windows
$ ./build.sh # on macOS
```
