# Build for macOS and Windows

## Bash shell

You need a `bash shell` to run the setup and the build script.

Note:
Github Actions use the bash shell included with Git for Windows.
It is used to build the releases.

## Setup environment

```shell
$ python --version
Python 3.8.8

$ python -m venv venv

$ source ./venv/Scripts/activate # On Windows: 
$ source ./venv/bin/activate # On macOS: 

$ python -m pip install -U pip wheel
$ pip install -r windows-requirements.txt

# make sure it's in the new virtualenv folder
$ which python
$ which pip 

$ python -m pip install -U pip wheel
$ pip install -r windows-requirements.txt # On Windows
$ pip install -r macos-requirements.txt # On macOS
```

## Check that streamlit is working

Copy H5 files to `$HOME/mosaic-streamlit-h5` if you have any test files.

```shell
$ streamlit run app.py
```
and select H5 file to check that it's working as expected.

## Build a distribution

You need a bash shell to run the build script.
Note: Github Actions use the bash shell included with Git for Windows.

```shell
$ cd build
$ ./build-windows.sh # on Windows
$ ./build-macos.sh # on macOS
```
