# GUI for Mosaic

**Disclaimer**: This is in active development. Please use at your own risk. This is for research purposes only.

### About

This repository includes the code to an interactive app built using [Streamlit.](https://www.streamlit.io/)
It is a user interface for [Mosaic](https://github.com/MissionBio/mosaic).

After installing [Mosaic](https://github.com/MissionBio/mosaic), install streamlit
in the appropriate environment using:

```
pip install streamlit
```

the app can be launched using:

```
streamlit run ./app.py
```

For s3 access, credentials have to be added to `/.aws/credentials`

The downloaded h5 files must be stored under `./h5/downloads/`
to be accessible throught the UI.

### To Do

* The parameters render the saved values when loading an analyzed file
* Documenting the code
* Documenting the procedure to add new workflows
