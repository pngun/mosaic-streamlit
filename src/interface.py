import os
import shutil
from pathlib import Path

import streamlit as st

STREAMLIT_STATIC_PATH = Path(st.__path__[0]) / "static"
# We create a downloads directory within the streamlit static asset directory
# and we write output files to it
DOWNLOADS_PATH = STREAMLIT_STATIC_PATH / "downloads"
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()

STATUS = None
SUBHEADER = None


def rerun():
    raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))


def subheader(msg):
    SUBHEADER.subheader(msg)


def info(msg, component=st):
    component.caption(msg)


def warning(msg):
    error_style = """
    <style>
    .error-font {
        color: rgb(191, 48, 53);
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0.7rem 0px 0.5rem;
        line-height: 1.6;
    }
    </style>
    """
    st.markdown(error_style, unsafe_allow_html=True)
    st.markdown(f'<p class="error-font">{msg}</p>', unsafe_allow_html=True)


def error(msg):
    error_style = """
    <style>
    .error-font {
        color: rgb(191, 48, 53);
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0.7rem 0px 0.5rem;
        line-height: 1.6;
    }
    </style>
    """
    st.markdown(error_style, unsafe_allow_html=True)
    SUBHEADER.markdown(f'<p class="error-font">{msg}</p>', unsafe_allow_html=True)

    status("Done.")

    st.stop()


def status(msg):
    global STATUS
    STATUS.write(msg)


def download(download_path):
    if isinstance(download_path, str):
        download_path = Path(download_path)

    name = download_path.name
    shutil.rmtree(DOWNLOADS_PATH)
    os.makedirs(DOWNLOADS_PATH)
    shutil.copy(download_path, DOWNLOADS_PATH / name)
    os.remove(download_path)

    down_style = """
    <style>
    .down-font {
        color: rgb(84, 180, 212);
        font-size: 1.25rem;
        font-weight: 500;
        margin: 0.7rem 0px 0.5rem;
        line-height: 1.6;
    }
    </style>
    """

    st.markdown(down_style, unsafe_allow_html=True)
    SUBHEADER.markdown(f"<p class='down-font'><a href='downloads/{name}'>Click here to download {name}</a></p>", unsafe_allow_html=True)

    st.stop()


def init():
    global SUBHEADER, STATUS

    SUBHEADER = st.empty()
    STATUS = st.empty()

    hide_streamlit_style = "<style>\n" "#MainMenu {visibility: hidden;}\n" "footer {visibility: hidden;}\n" "</style>"

    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 375px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 375px;
            margin-left: -375px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
